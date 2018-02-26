from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import telegram
from random import randint
import time
from twowaydict import TwoWayDict

############################################################################################################

# Constants
START_COMMAND_STR = 'start'
END_COMMAND_STR = 'end'
WAIT_MSG_STR = 'No users to match please wait'
MATCHED_MSG_STR = 'You have matched chat'
NO_PAIR_MSG = 'You have no pair'
END_CHAT_MSG = 'Your chat is ended'

############################################################################################################


unmatched_users = list()
user_to_user = TwoWayDict()


def start_cmd(bot: telegram.bot.Bot, update: telegram.update.Update):
    chat_id = update.message.chat_id

    if len(unmatched_users) != 0:
        pair_id = unmatched_users[-1]
        user_to_user[chat_id] = pair_id
        unmatched_users.pop()
        bot.send_message(chat_id, text=MATCHED_MSG_STR)
        bot.send_message(pair_id, text=MATCHED_MSG_STR)
    else:
        unmatched_users.append(chat_id)
        bot.send_message(chat_id, WAIT_MSG_STR)


def send_text_message_to_pair(bot, update):
    chat_id = update.message.chat_id
    if chat_id in user_to_user:
        pair_id = user_to_user[chat_id]
        bot.send_message(
            chat_id=pair_id,
            text=update.message.text)
    else:
        bot.send_message(chat_id, NO_PAIR_MSG)


def end_cmd(bot: telegram.bot.Bot, update: telegram.update.Update):
    chat_id = update.message.chat_id
    if chat_id in user_to_user:
        pair_id = user_to_user[chat_id]
        del user_to_user[chat_id]
        bot.send_message(chat_id, text=END_CHAT_MSG)
        bot.send_message(pair_id, text=END_CHAT_MSG)

    else:
        bot.send_message(chat_id, text=NO_PAIR_MSG)


def main():
    updater = Updater('346627696:AAEse-Ml2q32ONAgSPep8Dx_8x_SyNRYQOQ')
    dispatcher = updater.dispatcher

    start_handler = CommandHandler(START_COMMAND_STR, start_cmd)
    end_handler = CommandHandler(END_COMMAND_STR, end_cmd)
    msg_handler = MessageHandler(Filters.text, send_text_message_to_pair)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(end_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
