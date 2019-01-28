#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
        CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut
from threading import Thread
from private_conf import token_id
from anki_cards_generator import AnkiAutomatic
from send_card import CardSender
from database import AnkiGenDB
from enums import State, Languages
import traceback


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

log_errors = './log/errors.log'

# Create the EventHandler and pass it your bot's token.
updater = Updater(token_id)


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

I'll send you *definitions* for the words that you send me, with its kind of word and a sentence example substituting the #word by ".....". If the language is english, variations of the word will be also removed.

If you set your anki *username* and *password*, I will automatically generate and upload a flashcard with the definition you select. Of course, *I need to store your username and password* in order to do that, I won't use your data for anything but I recommend you not to use the typical password you use everywhere!

Code on [GitHub](https://github.com/damaru2/ankigenbot). You can also find [here](https://github.com/damaru2/anki_cards_generator) a script to generate flashcards from your computer (without compromising your data) by just copying the word and calling the script ''')


def word(bot, update):
    Thread(target=word_th, args=(bot, update)).start()


def word_th(bot, update):
    db = AnkiGenDB()
    try:
        state = State(db.get_state(update.message.chat_id))
    except ValueError as e:
        print(e)
        return
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
            [InlineKeyboardButton("Français", callback_data=str(Languages.fr.value))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select a language', reply_markup=reply_markup)

def swap(bot, update):
    ret = AnkiGenDB().reverse_order(update.message.chat_id)
    if not ret:
        return
    elif ret == 0:
        bot.sendMessage(update.message.chat_id,
                        text='Card format set to definition on the front and word on the back.')
    elif ret == 1:
        bot.sendMessage(update.message.chat_id,
                        text='Card format set to word on the front and definition on the back.')
    else:
        pass


def button(bot, update):
    Thread(target=button_th, args=(bot, update)).start()


def button_th(bot, update):
    query = update.callback_query
    if query.data == str(Languages.en.value):
        AnkiGenDB().update_language(query.message.chat_id, Languages.en)
        bot.editMessageText(text="Success! Language updated.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        return
    elif query.data == str(Languages.es.value):
        AnkiGenDB().update_language(query.message.chat_id, Languages.es)
        bot.editMessageText(text="Success! Language updated.",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        return
    elif query.data == str(Languages.fr.value):
        AnkiGenDB().update_language(query.message.chat_id, Languages.fr)
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
                if db.is_order_reversed(query.message.chat_id) == 1: # Reverse
                    CardSender(username, password).send_card(back, front, deck)
                else: # Don't reverse
                    CardSender(username, password).send_card(front, back, deck)
            except Exception:
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
    dp.add_handler(CommandHandler("user", user))
    dp.add_handler(CommandHandler("pass", passwd))
    dp.add_handler(CommandHandler("swap", swap))
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
