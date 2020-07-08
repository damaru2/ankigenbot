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
from utils import to_ipa
from send_card import CardSender
from database import AnkiGenDB
from enums import State, Languages

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

log_errors = './log/errors.log'

# Create the EventHandler and pass it your bot's token.
updater = Updater(token_id)

card_senders = dict()
lock_card_senders = Lock()
delay = 10

def start(bot, update):
    bot.sendMessage(update.message.chat_id,
        text='Write any word, select definitions and add them to anki!')
    db = AnkiGenDB()
    #TODO change the way of doing this
    if db.get_state(update.message.chat_id) is None:
        db.insert_new_user(id_chat=update.message.chat_id)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, parse_mode='Markdown',
        text='''I generate flashcards for [Anki](www.ankisrs.net).

I'll send you *definitions* for the words that you send me, with its kind of word and a sentence example substituting the #word by ".....". If the language is English, variations of the word will be also removed.

Use the commands /user, /deck, /pass to set up automatic uploading.

If you set your anki *username* and *password*, I will automatically generate and upload a flashcard with the definition you select. Of course, *I need to store your username and password* in order to do that, I won't use your data for anything but I recommend you not to use the typical password you use everywhere!

Code on [GitHub](https://github.com/damaru2/ankigenbot). You can also find [here](https://github.com/damaru2/anki_cards_generator) a script to generate flashcards from your computer (without compromising your data) by just copying the word and calling the script ''')


def word(bot, update):
    Thread(target=word_th, args=(bot, update)).start()


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
        if not concept.isalpha():
            bot.sendMessage(update.message.chat_id,
                text="Write only one word")
        else:
            lang = Languages(db.get_language(update.message.chat_id))
            defs = AnkiAutomatic(concept).retrieve_defs(lang.name)
            if defs is None:
                bot.sendMessage(update.message.chat_id,
                    text='No definitions found')
                return
            if_add_phonetics = db.get_if_add_phonetics(update.message.chat_id)
            for definition in defs:
                keyboard = [[InlineKeyboardButton("Add to anki", callback_data=concept),
                         InlineKeyboardButton("Cancel", callback_data='-1')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(definition, reply_markup=reply_markup)
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
    elif state == State.set_deck:
        try:
            db.update_deck(update.message.chat_id, update.message.text)
        except:
            bot.sendMessage(update.message.chat_id,
                text="Sorry, something went wrong")
            return
        bot.sendMessage(update.message.chat_id,
            text="Success! Deck updated.")
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
    bot.sendMessage(update.message.chat_id,
        text="Send me the deck name")

    AnkiGenDB().update_state(update.message.chat_id, State.set_deck)


def language(bot, update):
    keyboard = [[InlineKeyboardButton("English", callback_data=str(Languages.en.value))],
            [InlineKeyboardButton("Español", callback_data=str(Languages.es.value))],
            [InlineKeyboardButton("Français", callback_data=str(Languages.fr.value))],
            [InlineKeyboardButton("Deutsch", callback_data=str(Languages.de.value))],
            [InlineKeyboardButton("Italiano", callback_data=str(Languages.it.value))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select a language', reply_markup=reply_markup)

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
    Thread(target=button_th, args=(bot, update)).start()


def button_th(bot, update):
    query = update.callback_query
    if query.data in [str(Languages.en.value), str(Languages.es.value), str(Languages.fr.value), str(Languages.de.value), str(Languages.it.value) ]:
        AnkiGenDB().update_language(query.message.chat_id, int(query.data))
        bot.editMessageText(text="Success! Language updated.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        return
    try:
        if query.data != '-1':
            bot.editMessageText(text="{}\n*Uploading card to your anki deck*".format(query.message.text),
                    parse_mode='Markdown',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
            try:
                db = AnkiGenDB()
                username, password, deck = db.get_data(query.message.chat_id)
                if username is None or password is None or deck is None:
                    bot.editMessageText(text="I can't send your data because I don't have your credentials or deck name",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                    return
                front = query.message.text
                back = query.data.lower()
                print('{};{}'.format(db.get_language(query.message.chat_id), Languages.en.value))
                if db.get_if_add_phonetics(query.message.chat_id) != 0 and db.get_language(query.message.chat_id) == Languages.en.value:
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
