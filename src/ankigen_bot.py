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
from anki_cards_generator import AnkiAutomatic
from utils import to_ipa, escape_markdown
from send_card import CardSender, NoDeckFoundError
from database import AnkiGenDB
from enums import State, Languages, dict_state_to_lang, dict_state_to_lang_tags

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

log_errors = './log/errors.log'

# Create the EventHandler and pass it your bot's token.
updater = Updater(token_id, use_context=False)

card_senders = dict()
lock_card_senders = Lock()
delay = 10
default_deck_name = 'Vocabulary @ankigen_bot'

def start(bot, update):
    bot.sendMessage(update.message.chat_id,
        text='Write any word, select definitions and add them to anki!')
    db = AnkiGenDB()
    #TODO change the way of doing this
    if db.get_state(update.message.chat_id) is None:
        db.insert_new_user(id_chat=update.message.chat_id)


def help(bot, update):
    with open('data/help.txt') as f:
        text = f.read()
    bot.sendMessage(update.message.chat_id, parse_mode='Markdown', text=text)


def word(bot, update):
    Thread(target=word_th, args=(bot, update)).start()


def introduced_word(bot, update, lang, concept):
    db = AnkiGenDB()
    if not concept.isalpha() and lang not in [Languages.Japanese, Languages.Russian]:
        bot.sendMessage(update.message.chat_id,
            text="Write one word only")
    else:
        concept = concept.lower()
        defs = AnkiAutomatic(concept).retrieve_defs(lang.name)
        if defs is None:
            bot.sendMessage(update.message.chat_id,
                text='No definitions found')
            return
        if_add_phonetics = db.get_if_add_phonetics(update.message.chat_id)
        for definition in defs:
            keyboard = [[InlineKeyboardButton("Add to anki", callback_data="{}|{}".format(lang.value, concept)),
                     InlineKeyboardButton("Cancel", callback_data='-1')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(definition, reply_markup=reply_markup)


def word_th(bot, update):
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
        introduced_word(bot, update, lang, concept)
    elif state == State.set_user:
        try:
            db.update_username(update.message.chat_id, update.message.text)
        except:
            bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
            text="Success! Username updated.")
    elif state == State.set_pass:
        try:
            db.update_password(update.message.chat_id, update.message.text)
        except:
            bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
            text="Success! Password updated.")
    elif state == State.set_card_type:
        try:
            db.update_card_type(update.message.chat_id, update.message.text)
        except:
            bot.sendMessage(update.message.chat_id,
                            text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
                        text="Success! Card type updated.")
    elif state in dict_state_to_lang: # Set deck
        try:
            db.update_deck_name(update.message.chat_id, update.message.text, dict_state_to_lang[state])
        except:
            bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
            text="Success! Deck name updated.")

    elif state in dict_state_to_lang_tags: # Set tags
        try:
            db.update_tags(update.message.chat_id, update.message.text, dict_state_to_lang_tags[state])
        except:
            bot.sendMessage(update.message.chat_id,
                            text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
                        text="Success! Tags updated.")
    else:
        print('not a valid state')


def user(bot, update):
    bot.sendMessage(update.message.chat_id,
        text="Send me you anki username")
    AnkiGenDB().update_state(update.message.chat_id, State.set_user)


def passwd(bot, update):
    bot.sendMessage(update.message.chat_id,
        text="Send me you anki password")

    AnkiGenDB().update_state(update.message.chat_id, State.set_pass)


def cardtype(bot, update):
    db = AnkiGenDB()
    if db.get_state(update.message.chat_id) == State.set_card_type.value: # If it was in this state already then we back to normal and reset the card type to the default
        try:
            db.update_card_type(update.message.chat_id, '')
        except:
            bot.sendMessage(update.message.chat_id, text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id, text="Success! Card type was set back to default (Basic). Recall that sending /cardtype twice returns the cardtype to default.")
    else:
        bot.sendMessage(update.message.chat_id,
                        text="(Advanced, optional) Send me the exact name of the card type you would want to use. Examples (copy by clicking/tapping):\n`Basic`\n`Basic (and reversed card)`\nSpaces and capitalization matters. Note that the two first fields of the card type are the ones that are going to be filled with a definition and a word, regardless of the card type\n\nDefault is Basic",
                        parse_mode='Markdown')
        db.update_state(update.message.chat_id, State.set_card_type)


def deck(bot, update):
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


def tags(bot, update):
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


def language(bot, update):
    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton(lang.name, callback_data="{}".format(lang.value))] for lang in langs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lang = AnkiGenDB().get_language(update.message.chat_id)
    reminder_interface='\nYou can always use /en /es /fr /de or /it before a word for words in a language that is not the default one. Examples:\n/es amigo\n/en friend'
    update.message.reply_text('Pick a new default language. Current is *{}*.{}'.format(Languages(lang).name, reminder_interface),
                              reply_markup=reply_markup, parse_mode='Markdown')


def swap(bot, update):
    ret = AnkiGenDB().reverse_order(update.message.chat_id)
    if ret is None:
        return
    elif ret == 0:
        bot.sendMessage(update.message.chat_id,
                        text='Card format set to definition on the front and word on the back.')
    elif ret == 1:
        bot.sendMessage(update.message.chat_id,
                        text='Card format set to word on the front and definition on the back.')
    else:
        pass


def ipa(bot, update):
    ret = AnkiGenDB().swap_ipa(update.message.chat_id)
    if ret is None:
        return
    elif ret == 0:
        bot.sendMessage(update.message.chat_id,
                        text='IPA translation will not be added to English cards.')
    elif ret == 1:
        bot.sendMessage(update.message.chat_id,
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


def button(bot, update):
    #button_th(bot, update)
    Thread(target=button_th, args=(bot, update)).start()


def button_th(bot, update):
    query = update.callback_query
    language_codes = [str(lang.value) for lang in dict_state_to_lang.values()]
    if query.data in language_codes:
        AnkiGenDB().update_language(query.message.chat_id, int(query.data))
        bot.editMessageText(text="Success! Language updated.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        return
    if query.data[:4] == 'deck' and (query.data[4:] == '-1' or query.data[4:] in language_codes):
        if query.data[4:] == '-1':
            bot.editMessageText(text="No deck name was changed.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            return
        state = None
        for st,lang in dict_state_to_lang.items():
            if str(lang.value) == query.data[4:]:
                state = st
                break
        AnkiGenDB().update_state(query.message.chat_id, state)
        bot.editMessageText(text="Send me the deck name for {}.".format(Languages(int(query.data[4:])).name),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        return
    if query.data[:4] == 'tags' and (query.data[4:] == '-1' or query.data[4:] in language_codes):
        if query.data[4:] == '-1':
            bot.editMessageText(text="No tags were changed.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            return
        state = None
        for st,lang in dict_state_to_lang_tags.items():
            if str(lang.value) == query.data[4:]:
                state = st
                break
        AnkiGenDB().update_state(query.message.chat_id, state)
        bot.editMessageText(text="Send me the tags for {} (words separated by spaces). Or send /tags again to delete all tags for this language.".format(Languages(int(query.data[4:])).name),
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
                bot.editMessageText(text="You need to specify the name of an existing deck with /deck".format(query.message.text),
                    parse_mode='Markdown',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                return
            bot.editMessageText(text="{}\n*Uploading card to your anki deck*".format(query.message.text),
                parse_mode='Markdown',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            try:
                username, password, card_type = db.get_data(query.message.chat_id)
                if username is None or password is None or deck is None:
                    bot.editMessageText(text="I can't send your data because I don't have your credentials",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                    return
                front = query.message.text
                if '|' in query.data:
                    back = query.data.split('|', 1)[1]
                else:
                    back = query.data.lower()
                if db.get_if_add_phonetics(query.message.chat_id) != 0 and db.get_language(query.message.chat_id) == Languages.English.value:
                    ipa = to_ipa(back)
                    if ipa != back: # ipa translation found
                        back = "{} /{}/".format(back, ipa)
                with lock_card_senders:
                    try:
                        card_sender = card_senders[query.message.chat_id]
                        card_sender.last_access = time.time()
                    except KeyError:
                        card_sender = CardSender(username, password, card_type)
                        card_senders[query.message.chat_id] = card_sender

                    Timer(delay, delete_card_sender, [query.message.chat_id]).start()

                    if db.is_order_reversed(query.message.chat_id) == 1: # Reverse
                        ret = card_sender.send_card(back, front, deck, tags)
                    else:  # Don't reverse
                        ret = card_sender.send_card(front, back, deck, tags)
                    if ret:
                        bot.sendMessage(query.message.chat_id, text=escape_markdown(ret), parse_mode='Markdown')
            except NoDeckFoundError as e:
                print(traceback.format_exc())
                bot.editMessageText(
                    text="Could not find the deck \"{}\". Check it exists or use /deck to change the name of the deck I should use for this language".format(e.deck),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                return
            except Exception:
                print(traceback.format_exc())
                bot.editMessageText(text="Could not connect to ankiweb. Is your username and password correct? Check if you can access https://ankiweb.net/ with your credentials",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                return
            bot.editMessageText(text="{}\n{}".format(query.message.text, u"\u2705"),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
        else:
            bot.editMessageText(text="{}\n{}".format(query.message.text, u"\u274C"),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
    except TimedOut:
        bot.editMessageText(text="Telegram timed out, try again later.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        print("Telegram timed out")
        print(traceback.format_exc())
    except:
        bot.editMessageText(text="Sorry, the message was too old",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        print("Sorry, the message was too old")
        print(traceback.format_exc())
        raise


def word_lang(bot, update, lang):
    try:
        concept = update.message.text.split(' ', 1)[1].strip()
    except IndexError:
        return
    introduced_word(bot, update, lang, concept)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cardtype", cardtype))
    dp.add_handler(CommandHandler("language", language))
    dp.add_handler(CommandHandler("languages", language))
    dp.add_handler(CommandHandler("user", user))
    dp.add_handler(CommandHandler("pass", passwd))
    dp.add_handler(CommandHandler("swap", swap))
    dp.add_handler(CommandHandler("ipa", ipa))
    dp.add_handler(CommandHandler("deck", deck))
    dp.add_handler(CommandHandler("tags", tags))

    dp.add_handler(CommandHandler("en",
        lambda x,y: word_lang(x, y, Languages.English)
    ))
    dp.add_handler(CommandHandler("es",
        lambda x, y: word_lang(x, y, Languages.Español)
    ))
    dp.add_handler(CommandHandler("fr",
        lambda x, y: word_lang(x, y, Languages.Français)
    ))
    dp.add_handler(CommandHandler("de",
        lambda x, y: word_lang(x, y, Languages.Deutsch)
    ))
    dp.add_handler(CommandHandler("it",
        lambda x, y: word_lang(x, y, Languages.Italiano)
    ))
    dp.add_handler(CommandHandler("ru",
        lambda x, y: word_lang(x, y, Languages.Russian)
    ))
    #dp.add_handler(CommandHandler("ja",
    #    lambda x, y: word_lang(x, y, Languages.Japanese)
    #))

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
