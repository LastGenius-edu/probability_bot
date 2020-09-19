#!/usr/bin/env python
# -*- coding: utf-8 -*-
import keys
import os
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ANSWERS_TREE = {
    "Sample space - Finite or Continuous?": [
        {
            "What do you do with objects - Pick or Permutate": [
                {
                    "Does order matter - Yes or No": [
                        {
                            "Can you replace your elements - Yes or No": [
                                "yesformula",
                                "noformula"
                            ]
                        },
                        "noformula"
                    ]
                },
                {
                    "Are there repeatable elements - Yes or No": [
                        "n!/k1!*k2!*...km!",
                        "noformula"
                    ]
                }
            ]
        },
        "*geometric probability explanation*"
    ]
}


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
    message = query['message']['reply_markup']['inline_keyboard'][0][0].callback_data

    # Go to the current tree position saved for this user
    state = context.chat_data['state']
    current_tree = ANSWERS_TREE
    for element in state:
        current_tree = current_tree[element]

    if isinstance(current_tree, dict):
        reply_text = list(current_tree.keys())[0]
        keyboard = [[InlineKeyboardButton("First", callback_data="0")],
                    [InlineKeyboardButton("Second", callback_data="1")]]
        is_keyboard = True
        state.append(reply_text)
    elif isinstance(current_tree, list):
        result = current_tree[int(message)]

        if isinstance(result, dict):
            reply_text = list(result.keys())[0]
            keyboard = [[InlineKeyboardButton("First", callback_data="0")],
                        [InlineKeyboardButton("Second", callback_data="1")]]
            is_keyboard = True
            state.append(int(message))
            state.append(reply_text)
        elif isinstance(result, str):
            reply_text = result
            state = []

    context.chat_data['state'] = state

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
