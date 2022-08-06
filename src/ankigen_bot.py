# -*- coding: utf-8 -*-

import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
        CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut
from threading import Thread, Timer, Lock
import traceback
import time

from private_conf import token_id
from anki_cards_generator import AnkiAutomatic, language_translate_shell_codes
from utils import to_ipa, escape_markdown
from send_card import CardSender, NoDeckFoundError
from database import AnkiGenDB
from enums import State, Languages, dict_state_to_lang, dict_state_to_lang_tags, supported_language_codes, dict_state_to_lang_defi, dict_state_to_lang_word

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

log_errors = './log/errors.log'

# Create the EventHandler and pass it your bot's token.
updater = Updater(token_id, use_context=True)

card_senders = dict()
lock_card_senders = Lock()
delay = 10
default_deck_name = 'Vocabulary @ankigen_bot'

def start(update, context):
    context.bot.sendMessage(update.message.chat_id,
        text='Write any word, select definitions and add them to anki!')
    db = AnkiGenDB()
    if db.get_state(update.message.chat_id) is None:
        db.insert_new_user(id_chat=update.message.chat_id)


def help(update, context):
    with open('data/help.txt') as f:
        text = f.read()
    context.bot.sendMessage(update.message.chat_id, parse_mode='Markdown', text=text, disable_web_page_preview = True)



def word(update, context):
    Thread(target=word_th, args=(update, context)).start()


def introduced_word(bot, update, lang, concept, def_lang=None, word_to_lang=None):
    db = AnkiGenDB()
    if not concept.isalpha() and lang not in [Languages.Japanese, Languages.Russian]:
        bot.sendMessage(update.message.chat_id,
            text="Write one word only")
    else:
        concept = concept.lower()
        defs, concept_translations = AnkiAutomatic(concept).retrieve_defs(lang.name, def_lang=def_lang, word_lang=word_to_lang)
        if defs is None:
            bot.sendMessage(update.message.chat_id,
                text='No definitions found')
            return
        for definition in defs:
            keyboard = [[InlineKeyboardButton("Add to anki", callback_data="{}|{}|0".format(lang.value, concept))],

                     #InlineKeyboardButton("Cancel", callback_data='-1'),
                    #InlineKeyboardButton("test", switch_inline_query_current_chat="/asdf this is a test")]
                        ]
            keyboard += [[InlineKeyboardButton(translation, callback_data="{}|{}|{}".format(lang.value, concept, i+1))] for i, translation in enumerate(concept_translations)] if concept_translations else []

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(definition, reply_markup=reply_markup)


def word_th(update, context):
    db = AnkiGenDB()
    try:
        state = State(db.get_state(update.message.chat_id))
    except ValueError as e:
        if db.get_state(update.message.chat_id) is None:
            db.insert_new_user(id_chat=update.message.chat_id)
        state = State(db.get_state(update.message.chat_id))

    if state == State.normal:
        concept = update.message.text.strip()
        lang = Languages(db.get_language(update.message.chat_id))
        def_lang = db.get_def_lang(update.message.chat_id, lang.value)
        word_to_lang = db.get_word_lang(update.message.chat_id, lang.value)
        introduced_word(context.bot, update, lang, concept, def_lang, word_to_lang)
    elif state == State.set_user:
        try:
            db.update_username(update.message.chat_id, update.message.text)
        except:
            context.bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        context.bot.sendMessage(update.message.chat_id,
            text="Success! Username updated.")
    elif state == State.set_pass:
        try:
            db.update_password(update.message.chat_id, update.message.text)
        except:
            context.bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        context.bot.sendMessage(update.message.chat_id,
            text="Success! Password updated.")
    elif state == State.set_card_type:
        try:
            db.update_card_type(update.message.chat_id, update.message.text)
        except:
            context.bot.sendMessage(update.message.chat_id,
                            text="Sorry, something went wrong")
            return
        context.bot.sendMessage(update.message.chat_id,
                        text="Success! Card type updated.")
    elif state in dict_state_to_lang: # Set deck
        try:
            db.update_deck_name(update.message.chat_id, update.message.text, dict_state_to_lang[state])
        except:
            context.bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        context.bot.sendMessage(update.message.chat_id,
            text="Success! Deck name updated.")

    elif state in dict_state_to_lang_tags: # Set tags
        try:
            db.update_tags(update.message.chat_id, update.message.text, dict_state_to_lang_tags[state])
        except:
            context.bot.sendMessage(update.message.chat_id,
                            text="Sorry, something went wrong with the tags")
            return
        context.bot.sendMessage(update.message.chat_id,
                        text="Success! Tags updated.")
    elif state in dict_state_to_lang_defi:
        if update.message.text in supported_language_codes:
           context.bot.sendMessage(update.message.chat_id, text='Ok! I will translate these definitions into {}'.format(supported_language_codes[update.message.text]))
           db.update_def_lang(update.message.chat_id, dict_state_to_lang_defi[state], update.message.text)
           db.update_state(update.message.chat_id, State.normal)
        else:
           keyboard = [[InlineKeyboardButton('Cancel', callback_data="tod{}".format(-1))]]
           context.bot.sendMessage(update.message.chat_id,
                                text="\"{}\" is not a valid code. Introduce a valid code or press Cancel.".format(update.message.text),
                                reply_markup=InlineKeyboardMarkup(keyboard))
    elif state in dict_state_to_lang_word:
        if update.message.text in supported_language_codes:
            context.bot.sendMessage(update.message.chat_id, text='Ok! For new cards, I\'ll give you the option to add the concept translated to {}'.format(supported_language_codes[update.message.text]))
            db.update_word_lang(update.message.chat_id, dict_state_to_lang_word[state], update.message.text)
            db.update_state(update.message.chat_id, State.normal)
        else:
            keyboard = [[InlineKeyboardButton('Cancel', callback_data="tow{}".format(-1))]]
            context.bot.sendMessage(update.message.chat_id,
                                    text="\"{}\" is not a valid code. Introduce a valid code from [this list](https://telegra.ph/Language-codes-07-26) or press Cancel.".format(update.message.text),
                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode='Markdown')
    else:
        print('not a valid state')


def user(update, context):
    context.bot.sendMessage(update.message.chat_id,
        text="Send me you anki username")
    AnkiGenDB().update_state(update.message.chat_id, State.set_user)


def passwd(update, context):
    context.bot.sendMessage(update.message.chat_id,
        text="Send me you anki password")

    AnkiGenDB().update_state(update.message.chat_id, State.set_pass)


def cardtype(update, context):
    db = AnkiGenDB()
    if db.get_state(update.message.chat_id) == State.set_card_type.value: # If it was in this state already then we back to normal and reset the card type to the default
        try:
            db.update_card_type(update.message.chat_id, '')
        except:
            context.bot.sendMessage(update.message.chat_id, text="Sorry, something went wrong")
            return
        context.bot.sendMessage(update.message.chat_id, text="Success! Card type was set back to default (Basic). Recall that sending /cardtype twice returns the cardtype to default.")
    else:
        context.bot.sendMessage(update.message.chat_id,
                        text="(Advanced, optional) Send me the exact name of the card type you would want to use. Examples (copy by clicking/tapping):\n`Basic`\n`Basic (and reversed card)`\nSpaces and capitalization matters. Note that the two first fields of the card type are the ones that are going to be filled with a definition and a word, regardless of the card type\n\nDefault is Basic",
                        parse_mode='Markdown')
        db.update_state(update.message.chat_id, State.set_card_type)


def deck(update, context):
    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton(lang.name, callback_data="deck{}".format(lang.value))] for lang in langs ]
    keyboard.append([InlineKeyboardButton('Cancel', callback_data="deck{}".format(-1))])
    reply_markup = InlineKeyboardMarkup(keyboard)

    deck_names = AnkiGenDB().get_all_deck_names(update.message.chat_id)
    if deck_names is None:
        deck_names = ''
    else:
        deck_names = '\nCurrent deck names are:\n' + ''.join(['\n- *{}*: {}'.format(Languages(language).name, escape_markdown(deck_name) if deck_name else "") for deck_name, language in deck_names])
    text = 'Select a language to set a deck name for that language.{}'.format(deck_names)
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def tags(update, context):
    db = AnkiGenDB()
    state = State(db.get_state(update.message.chat_id))
    if state in dict_state_to_lang_tags:
        db.update_tags(update.message.chat_id, tags="", lang=dict_state_to_lang_tags[state])
        update.message.reply_text("Ok! I deleted all the tags for {}.".format(dict_state_to_lang_tags[state].name), parse_mode='Markdown')
    else:
        langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
        keyboard = [[InlineKeyboardButton(lang.name, callback_data="tags{}".format(lang.value))] for lang in langs ]
        keyboard.append([InlineKeyboardButton('Cancel', callback_data="tags{}".format(-1))])
        reply_markup = InlineKeyboardMarkup(keyboard)

        tags = db.get_all_tags(update.message.chat_id)
        if tags is None:
            tags = ''
        else:
            tags = '\nCurrent tags are:\n' + \
                         ''.join(['\n- *{}*: {}'.format(Languages(language).name, escape_markdown(lang_tags) if tags else "") for lang_tags, language in tags])
        text = 'Select a language to set tags for that language.{}'.format(tags)
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def language(update, context):
    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton(lang.name, callback_data="{}".format(lang.value))] for lang in langs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lang = AnkiGenDB().get_language(update.message.chat_id)
    reminder_interface='\nYou can always use /en /es /fr /de or /it before a word for words in a language that is not the default one. Examples:\n/es amigo\n/en friend'
    update.message.reply_text('Pick a new default language. Current is *{}*.{}'.format(Languages(lang).name, reminder_interface),
                              reply_markup=reply_markup, parse_mode='Markdown')


def swap(update, context):
    ret = AnkiGenDB().reverse_order(update.message.chat_id)
    if ret is None:
        return
    elif ret == 0:
        context.bot.sendMessage(update.message.chat_id,
                        text='Card format set to definition on the front and word on the back.')
    elif ret == 1:
        context.bot.sendMessage(update.message.chat_id,
                        text='Card format set to word on the front and definition on the back.')
    else:
        pass


def definition_language(update, context):
    def_langs = AnkiGenDB().get_all_def_langs(update.message.chat_id)
    def_langs_text = ''
    if def_langs:
        current_settings = ['\n- *{}*: {}'.format(Languages(language).name, supported_language_codes.get(def_lang, "")) for
                            (def_lang, language) in def_langs if def_lang]
        def_langs_text = '\n\nCurrent settings are:{}'.format(''.join(current_settings) if current_settings else "") if current_settings else ""

    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton("{}".format(lang.name), callback_data="fromd{}".format(lang.value))] for lang in langs]
    keyboard.append([InlineKeyboardButton('Cancel', callback_data="fromd{}".format(-1))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Make the definition of a word in language A be in another language B. Note the translation is automatic and can be innacurate.\n*Select language A*{}'.format(def_langs_text),
                              reply_markup=reply_markup, parse_mode='Markdown')


def include_word_translation(update, context):
    word_langs = AnkiGenDB().get_all_word_langs(update.message.chat_id)
    word_langs_text = ''
    if word_langs:
        current_settings = ['\n- *{}*: {}'.format(Languages(language).name, supported_language_codes.get(word_lang, "")) for
                            (word_lang, language) in word_langs if word_lang]
        word_langs_text = '\n\nCurrent settings are:{}'.format(''.join(current_settings) if current_settings else "") if current_settings else ""

    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton("{}".format(lang.name), callback_data="fromw{}".format(lang.value))] for lang in langs]
    keyboard.append([InlineKeyboardButton('Cancel', callback_data="fromw{}".format(-1))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Make me include with the card of a word in language A, the translation of the word in language B. Every time, you will pick which translation you want to use.\n*Select language A*{}'.format(word_langs_text),
                              reply_markup=reply_markup, parse_mode='Markdown')


def ipa(update, context):
    ret = AnkiGenDB().swap_ipa(update.message.chat_id)
    if ret is None:
        return
    elif ret == 0:
        context.bot.sendMessage(update.message.chat_id,
                        text='IPA translation will not be added to English cards.')
    elif ret == 1:
        context.bot.sendMessage(update.message.chat_id,
                        text='IPA translation is now enabled (but only for English cards).')
    else:
        pass


def delete_card_sender(chat_id):
    current_time = time.time()
    with lock_card_senders:
        try:
            if current_time - card_senders[chat_id].last_access  >= delay - 0.1:
                card_senders[chat_id].driver.quit()
                del card_senders[chat_id]
        except KeyError:
            pass


def button(update, context):
    #button_th(update, context)
    Thread(target=button_th, args=(update, context)).start()


def button_th(update, context):
    query = update.callback_query
    language_codes = [str(lang.value) for lang in dict_state_to_lang.values()]
    if query.data in language_codes:
        AnkiGenDB().update_language(query.message.chat_id, int(query.data))
        context.bot.editMessageText(text="Success! Language updated.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        return
    if query.data[:4] == 'deck' and (query.data[4:] == '-1' or query.data[4:] in language_codes):
        if query.data[4:] == '-1':
            context.bot.editMessageText(text="No deck name was changed.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            return
        state = None
        for st,lang in dict_state_to_lang.items():
            if str(lang.value) == query.data[4:]:
                state = st
                break
        AnkiGenDB().update_state(query.message.chat_id, state)
        context.bot.editMessageText(text="Send me the deck name for {}.".format(Languages(int(query.data[4:])).name),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        return
    if query.data[:5] == 'fromd' and (query.data[5:] == '-1' or query.data[5:] in language_codes):
        if query.data[5:] == '-1':
            context.bot.editMessageText(text="No changes were made.",
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            return

        for st, lang in dict_state_to_lang_defi.items():
            if str(lang.value) == query.data[5:]:
                state = st
                break
        db = AnkiGenDB()
        db.update_state(query.message.chat_id, state)
        langs = sorted(list(dict_state_to_lang.values()), key=lambda x: x.value)

        keyboard = [[InlineKeyboardButton("{}".format(lang.name), callback_data="tod{}".format(lang.value))] for lang in langs if lang.value != int(query.data[5:])]
        if db.get_def_lang(query.message.chat_id, int(query.data[5:])):
            keyboard.append([InlineKeyboardButton('Disable {} translation'.format(Languages(int(query.data[5:])).name), callback_data="tod{}".format(-2))])
        keyboard.append([InlineKeyboardButton('Cancel', callback_data="tod{}".format(-1))])

        context.bot.editMessageText(text='\nMake the definition for cards in {} be in another language B. Note the translation is automatic and can be innacurate sometimes\n*Now select language B*\nYou can press a button or write a valid language code from [this list](https://telegra.ph/Language-codes-07-26)'\
                                        .format(Languages(int(query.data[5:])).name),
                                    chat_id=query.message.chat_id,
                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode='Markdown',
                                    message_id=query.message.message_id)
        return
    if query.data[:3] == 'tod' and (query.data[3:] in language_codes + ['-1', '-2']):
        db = AnkiGenDB()
        if query.data[3:] == '-1':
            context.bot.editMessageText(text="No changes were made.",
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            AnkiGenDB().update_state(query.message.chat_id, State.normal)
            return

        state = State(db.get_state(query.message.chat_id))
        if state not in dict_state_to_lang_defi:
            return
        from_lang = dict_state_to_lang_defi[state]
        db.update_state(query.message.chat_id, State.normal)
        if query.data[3:] == '-2':
            AnkiGenDB().remove_def_lang(query.message.chat_id, from_lang)
            context.bot.editMessageText(text='Ok! I will not translate the definition of the {} cards.'
                                        .format(from_lang.name),
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            return
        to_lang = int(query.data[3:])
        db.update_def_lang(query.message.chat_id, from_lang, language_translate_shell_codes[Languages(to_lang).name])
        context.bot.editMessageText(text='Ok! I will translate the definitions of {} cards into {}'
                                        .format(from_lang.name, Languages(to_lang).name),
                                    chat_id=query.message.chat_id,
                                    message_id=query.message.message_id)
        return
    if query.data[:5] == 'fromw' and (query.data[5:] == '-1' or query.data[5:] in language_codes):
        if query.data[5:] == '-1':
            context.bot.editMessageText(text="No changes were made.",
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            return

        for st, lang in dict_state_to_lang_word.items():
            if str(lang.value) == query.data[5:]:
                state = st
                break
        db = AnkiGenDB()
        db.update_state(query.message.chat_id, state)
        langs = sorted(list(dict_state_to_lang_word.values()), key=lambda x: x.value)

        keyboard = [[InlineKeyboardButton("{}".format(lang.name), callback_data="tow{}".format(lang.value))] for lang in langs if lang.value != int(query.data[5:])]

        if db.get_def_lang(query.message.chat_id, int(query.data[5:])):
            keyboard.append([InlineKeyboardButton('Disable {} translation'.format(Languages(int(query.data[5:])).name), callback_data="tow{}".format(-2))])
        keyboard.append([InlineKeyboardButton('Cancel', callback_data="tow{}".format(-1))])
        context.bot.editMessageText(text='\nFor cards in {}, add a translation of the concept to the language you will now select. Note the translations are automatic and can be innacurate sometimes\n**Now select language B**' \
                                    .format(Languages(int(query.data[5:])).name),
                                    chat_id=query.message.chat_id,
                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode='Markdown',
                                    message_id=query.message.message_id)
        return
    if query.data[:3] == 'tow' and (query.data[3:] in language_codes + ['-1', '-2']):
        db = AnkiGenDB()
        if query.data[3:] == '-1':
            context.bot.editMessageText(text="No changes were made.",
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            AnkiGenDB().update_state(query.message.chat_id, State.normal)
            return

        state = State(db.get_state(query.message.chat_id))
        if state not in dict_state_to_lang_word:
            return
        from_lang = dict_state_to_lang_word[state]
        if query.data[3:] == '-2':
            AnkiGenDB().remove_word_lang(query.message.chat_id, from_lang)
            context.bot.editMessageText(text="Word translation has been disabled for {}".format(from_lang.name),
                                        chat_id=query.message.chat_id,
                                        message_id=query.message.message_id)
            return
        to_lang = int(query.data[3:])
        db.update_word_lang(query.message.chat_id, from_lang, language_translate_shell_codes[Languages(to_lang).name])
        context.bot.editMessageText(text='Ok! Cards for {} words will be translated into {} and you will be asked whether you want to add a translation into the card.' \
                                    .format(from_lang.name, Languages(to_lang).name),
                                    chat_id=query.message.chat_id,
                                    message_id=query.message.message_id)
        return
    if query.data[:4] == 'tags' and (query.data[4:] == '-1' or query.data[4:] in language_codes):
        if query.data[4:] == '-1':
            context.bot.editMessageText(text="No tags were changed.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            return
        state = None
        for st,lang in dict_state_to_lang_tags.items():
            if str(lang.value) == query.data[4:]:
                state = st
                break
        AnkiGenDB().update_state(query.message.chat_id, state)
        context.bot.editMessageText(text="Send me the tags for {} (words separated by spaces). Or send /tags again to delete all tags for this language.".format(Languages(int(query.data[4:])).name),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        return
    try:
        if query.data != '-1':
            db = AnkiGenDB()
            spl = query.data.split('|', 1)[0]
            deck = None
            if spl in language_codes:
                deck = db.get_deck_name(query.message.chat_id, spl)
                tags =  db.get_tags(query.message.chat_id, spl)
            if deck is None:
                context.bot.editMessageText(text="You need to specify the name of an existing deck with /deck".format(query.message.text),
                    parse_mode='Markdown',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                return
            try:
                username, password, card_type = db.get_data(query.message.chat_id)
                if username is None or password is None or deck is None:
                    context.bot.editMessageText(text="I can't send your data because I don't have your credentials",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                    return
                front = query.message.text
                if '|' in query.data:
                    data = query.data.split('|', 2)
                    back = data[1]
                    if len(data) > 2:
                        front = "|{}|\n{}".format(query.message.reply_markup.inline_keyboard[int(data[2])][0].text,
                                                 front)
                        #if front[0] == '(':
                        #    idx = front.find(')')
                        #    front = '{} ({}){}'.format(front[: idx+ 1 ], query.message.reply_markup.inline_keyboard[int(data[2])][0].text, front[idx + 1: ] )
                        #else:
                        #    front = "({}) {}".format(query.message.reply_markup.inline_keyboard[int(data[2])][0].text, front)
                else:
                    back = query.data.lower()
                if db.get_if_add_phonetics(query.message.chat_id) != 0 and db.get_language(query.message.chat_id) == Languages.English.value:
                    ipa = to_ipa(back)
                    if ipa != back: # ipa translation found
                        back = "{} /{}/".format(back, ipa)

                if db.is_order_reversed(query.message.chat_id) == 1:  # Reverse if we have to
                    front, back = back, front
                context.bot.editMessageText(
                    text="{}\n---\n{}\n*Uploading card to your anki deck*".format(front, back),
                    parse_mode='Markdown',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                with lock_card_senders:
                    try:
                        card_sender = card_senders[query.message.chat_id]
                        card_sender.last_access = time.time()
                    except KeyError:
                        card_sender = CardSender(username, password, card_type)
                        card_senders[query.message.chat_id] = card_sender

                    Timer(delay, delete_card_sender, [query.message.chat_id]).start()

                    ret = card_sender.send_card(front, back, deck, tags)
                    if ret:
                        context.bot.sendMessage(query.message.chat_id, text=escape_markdown(ret), parse_mode='Markdown')
            except NoDeckFoundError as e:
                print(traceback.format_exc())
                context.bot.editMessageText(
                    text="Could not find the deck \"{}\". Check it exists or use /deck to change the name of the deck I should use for this language".format(e.deck),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                return
            except Exception:
                print(traceback.format_exc())
                context.bot.editMessageText(text="Could not connect to ankiweb. Is your username and password correct? Check if you can access https://ankiweb.net/ with your credentials",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                return
            context.bot.editMessageText(
                    text="{}\n---\n{}\n{}".format(front, back, u"\u2705"),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
        else:
            context.bot.editMessageText(text="{}\n{}".format(query.message.text, u"\u274C"),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
    except TimedOut:
        context.bot.editMessageText(text="Telegram timed out, try again later.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        print("Telegram timed out")
        print(traceback.format_exc())
    except:
        context.bot.editMessageText(text="Sorry, the message was too old",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        print("Sorry, the message was too old")
        print(traceback.format_exc())
        raise


def word_lang(update, context, lang):
    try:
        concept = update.message.text.split(' ', 1)[1].strip()
    except IndexError:
        return

    db = AnkiGenDB()
    def_lang = db.get_def_lang(update.message.chat_id, lang.value)
    word_to_lang = db.get_word_lang(update.message.chat_id, lang.value)
    introduced_word(context.bot, update, lang, concept, def_lang, word_to_lang)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"' % (update, context.error))


def main():

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cardtype", cardtype))
    dp.add_handler(CommandHandler("defilang", definition_language))
    dp.add_handler(CommandHandler("wordtr", include_word_translation))
    dp.add_handler(CommandHandler("language", language))
    dp.add_handler(CommandHandler("languages", language))
    dp.add_handler(CommandHandler("user", user))
    dp.add_handler(CommandHandler("pass", passwd))
    dp.add_handler(CommandHandler("swap", swap))
    dp.add_handler(CommandHandler("ipa", ipa))
    dp.add_handler(CommandHandler("deck", deck))
    dp.add_handler(CommandHandler("tags", tags))

    dp.add_handler(CommandHandler("en", lambda x, y: word_lang(x, y, Languages.English)))
    dp.add_handler(CommandHandler("es", lambda x, y: word_lang(x, y, Languages.Español)))
    dp.add_handler(CommandHandler("fr", lambda x, y: word_lang(x, y, Languages.Français)))
    dp.add_handler(CommandHandler("de", lambda x, y: word_lang(x, y, Languages.Deutsch)))
    dp.add_handler(CommandHandler("it", lambda x, y: word_lang(x, y, Languages.Italiano)))
    dp.add_handler(CommandHandler("ja", lambda x, y: word_lang(x, y, Languages.Japanese)))
    dp.add_handler(CommandHandler("ru", lambda x, y: word_lang(x, y, Languages.Russian)))

    dp.add_handler(MessageHandler(Filters.text, word))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()
