from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import telegram
from random import randint
import time
from twowaydict import TwoWayDict
import threading
import threading

############################################################################################################

# Constants
START_COMMAND_STR = 'start'
END_COMMAND_STR = 'end'
WAIT_MSG_STR = 'No users to match please wait'
MATCHED_MSG_STR = 'You have matched chat'
NO_PAIR_MSG = 'You have no pair'
END_CHAT_MSG = 'Your chat is ended'

############################################################################################################


class ChatBot:
    def __init__(self, lock):
        self._unmatched_users = list()
        self._user_to_user = TwoWayDict()
        self._lock = lock()

    def start_cmd(self, bot, update):
        self._lock.acquire()
        chat_id = update.message.chat_id
        if len(self._unmatched_users) != 0 and self._unmatched_users[0] != chat_id:
            pair_id = self._unmatched_users.pop()
            self._user_to_user[chat_id] = pair_id
            bot.send_message(chat_id, text=MATCHED_MSG_STR)
            bot.send_message(pair_id, text=MATCHED_MSG_STR)
        else:
            self._unmatched_users.append(chat_id)
            bot.send_message(chat_id, WAIT_MSG_STR)
        self._lock.release()

    def send_text_message_to_pair(self, bot, update):
        self._lock.acquire()
        chat_id = update.message.chat_id
        if chat_id in self._user_to_user:
            pair_id = self._user_to_user[chat_id]
            bot.send_message(
                chat_id=pair_id,
                text=update.message.text)
        else:
            bot.send_message(chat_id, NO_PAIR_MSG)
        self._lock.release()

    def end_cmd(bot: telegram.bot.Bot, update: telegram.update.Update):
        self._lock.acquire()
        chat_id = update.message.chat_id
        if chat_id in self._user_to_user:
            pair_id = self._user_to_user[chat_id]
            del self._user_to_user[chat_id]
            bot.send_message(chat_id, text=END_CHAT_MSG)
            bot.send_message(pair_id, text=END_CHAT_MSG)

        else:
            bot.send_message(chat_id, text=NO_PAIR_MSG)
        self._lock.release()


def main():
    updater = Updater('346627696:AAEse-Ml2q32ONAgSPep8Dx_8x_SyNRYQOQ')
    dispatcher = updater.dispatcher

    chat_bot = ChatBot(threading.Lock)

    start_handler = CommandHandler(START_COMMAND_STR, chat_bot.start_cmd)
    end_handler = CommandHandler(END_COMMAND_STR, chat_bot.end_cmd)
    msg_handler = MessageHandler(
        Filters.text, chat_bot.send_text_message_to_pair)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(end_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
