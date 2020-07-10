#!/usr/bin/env python
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
from send_card import CardSender
from database import AnkiGenDB
from enums import State, Languages, dict_state_to_lang

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
    if not concept.isalpha():
        bot.sendMessage(update.message.chat_id,
            text="Write only one word")
    else:
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
    elif state in dict_state_to_lang:
        try:
            db.update_deck_name(update.message.chat_id, update.message.text, dict_state_to_lang[state])
        except:
            bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
            text="Success! Deck name updated.")
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


def deck(bot, update):
    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton(lang.name, callback_data="deck{}".format(lang.value))] for lang in langs ]
    keyboard.append([InlineKeyboardButton('Cancel', callback_data="deck{}".format(-1))])
    reply_markup = InlineKeyboardMarkup(keyboard)

    deck_names = AnkiGenDB().get_all_deck_names(update.message.chat_id)
    if deck_names is None:
        deck_names = ''
    else:
        deck_names = '\nCurrent deck names are:\n' + \
                     ''.join(['\n- *{}*: {}'.format(Languages(language).name, escape_markdown(deck_name)) for deck_name, language in deck_names])
    text = 'Select a language to set a deck name for that language.{}'.format(deck_names)
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def language(bot, update):
    langs = sorted(list(dict_state_to_lang.values()),key=lambda x: x.value)
    keyboard = [[InlineKeyboardButton(lang.name, callback_data="{}".format(lang.value))] for lang in langs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lang = AnkiGenDB().get_language(update.message.chat_id)
    reminder_interface='\nRemember you can add words in a language that is not the default one by adding /en /es /fr /de or /it before them. Like\n\n/es amigo'
    update.message.reply_text('*{}* is the current default language. Which should be the new default language? {}'.format(Languages(lang).name, reminder_interface),
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
    try:
        if query.data != '-1':
            db = AnkiGenDB()
            spl = query.data.split('|', 1)[0]
            deck = None
            if spl in language_codes:
                deck = db.get_deck_name(query.message.chat_id, spl)
            if deck is None:
                deck = default_deck_name
            bot.editMessageText(text="{}\n*Uploading card to your anki deck*".format(query.message.text),
                parse_mode='Markdown',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            try:
                username, password = db.get_data(query.message.chat_id)
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
                        card_sender = CardSender(username, password)
                        card_senders[query.message.chat_id] = card_sender

                    Timer(delay, delete_card_sender, [query.message.chat_id]).start()

                    if db.is_order_reversed(query.message.chat_id) == 1: # Reverse
                        card_sender.send_card(back, front, deck)
                    else: # Don't reverse
                        card_sender.send_card(front, back, deck)
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


def word_en(bot, update):
    try:
        concept = update.message.text.split(' ', 1)[1]
    except IndexError:
        return
    introduced_word(bot, update, Languages.English, concept)


def word_es(bot, update):
    try:
        concept = update.message.text.split(' ', 1)[1]
    except IndexError:
        return
    introduced_word(bot, update, Languages.Español, concept)


def word_fr(bot, update):
    try:
        concept = update.message.text.split(' ', 1)[1]
    except IndexError:
        return
    introduced_word(bot, update, Languages.Français, concept)


def word_de(bot, update):
    try:
        concept = update.message.text.split(' ', 1)[1]
    except IndexError:
        return
    introduced_word(bot, update, Languages.Deutsch, concept)


def word_it(bot, update):
    try:
        concept = update.message.text.split(' ', 1)[1]
    except IndexError:
        return
    introduced_word(bot, update, Languages.Italiano, concept)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("language", language))
    dp.add_handler(CommandHandler("languages", language))
    dp.add_handler(CommandHandler("user", user))
    dp.add_handler(CommandHandler("pass", passwd))
    dp.add_handler(CommandHandler("swap", swap))
    dp.add_handler(CommandHandler("ipa", ipa))
    dp.add_handler(CommandHandler("deck", deck))


    dp.add_handler(CommandHandler("en", word_en))
    dp.add_handler(CommandHandler("es", word_es))
    dp.add_handler(CommandHandler("fr", word_fr))
    dp.add_handler(CommandHandler("de", word_de))
    dp.add_handler(CommandHandler("it", word_it))

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
