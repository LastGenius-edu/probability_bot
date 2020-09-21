#!/usr/bin/env python
# -*- coding: utf-8 -*-
import keys
import os
import json
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open("tree.json", "r") as file:
    ANSWERS_TREE = json.load(file)


def start(update, context):
    reply_text = """Hello, I am a bot that helps you to figure out the right formula for combinatorial problems!

    Press 'Ready' when you want me to help you with a problem
    """
    keyboard = [[InlineKeyboardButton("Ready", callback_data="ready")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.chat_data['state'] = []

    update.message.reply_text(reply_text, reply_markup=reply_markup, parse_mode="Markdown")


def answer_handler(update, context):
    """
    Handles user's answers
    """
    query = update.callback_query
    user_choice = update.callback_query.data
    reply_text = ""
    is_photo = False
    print(user_choice)
    print("Message", user_choice)

    # Go to the current tree position saved for this user
    state = context.chat_data['state']
    current_tree = ANSWERS_TREE
    for element in state:
        current_tree = current_tree[element]

    if isinstance(current_tree, dict):
        reply_text = list(current_tree.keys())[0]
        index = reply_text.find(" - ")
        button_text = [reply_text[index + 3:].split(" ")[0], reply_text[index + 3:].split(" ")[2]]
        keyboard = [[InlineKeyboardButton(button_text[0], callback_data="0")],
                    [InlineKeyboardButton(button_text[1][:-1], callback_data="1")]]
        is_keyboard = True
        state.append(reply_text)
    elif isinstance(current_tree, list):
        result = current_tree[int(user_choice)]

        if isinstance(result, dict):
            reply_text = list(result.keys())[0]
            index = reply_text.find(" - ")
            button_text = [reply_text[index + 3:].split(" ")[0], reply_text[index + 3:].split(" ")[2]]
            keyboard = [[InlineKeyboardButton(button_text[0], callback_data="0")],
                        [InlineKeyboardButton(button_text[1][:-1], callback_data="1")]]
            is_keyboard = True
            state.append(int(user_choice))
            state.append(reply_text)
        elif isinstance(result, str):
            is_keyboard = False
            result = result.split(" ")
            is_photo = True
            for photo in result:
                context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(photo, "rb"))
            state = []

    print(state)
    context.chat_data['state'] = state

    if not is_photo:
        query.edit_message_text(text=reply_text, parse_mode="Markdown")
    if is_keyboard:
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


def main():
    """
    Main bot function
    """
    token = os.environ['TOKEN']
    # Create the Updater and pass it your bot's token.
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(answer_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
