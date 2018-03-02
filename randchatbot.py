from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.ext.dispatcher import run_async
from twowaydict import TwoWayDict
import threading


class ChatBot:

    START_COMMAND_STR = 'start'
    END_COMMAND_STR = 'end'
    WAIT_MSG_STR = 'No users to match please wait'
    MATCHED_MSG_STR = 'You have matched chat'
    NO_PAIR_MSG = 'You have no pair'
    END_CHAT_MSG = 'Your chat is ended'

    def __init__(self):
        self._unmatched_users = list()
        self._user_to_user = TwoWayDict()
        self._user_to_user_lock = threading.Lock()
        self._unmatched_users_lock = threading.Lock()

    @run_async
    def start_cmd(self, bot, update):
        chat_id = update.message.chat_id
        if len(self._unmatched_users) != 0 and not self._is_user_started(chat_id):
            self._unmatched_users_lock.acquire()
            pair_id = self._unmatched_users.pop()
            self._unmatched_users_lock.release()
            
            self._user_to_user_lock.acquire()
            self._user_to_user[chat_id] = pair_id
            self._user_to_user_lock.release()

            bot.send_message(chat_id, text=ChatBot.MATCHED_MSG_STR)
            bot.send_message(pair_id, text=ChatBot.MATCHED_MSG_STR)
        else:
            if self._is_user_started(chat_id):
                return

            self._unmatched_users_lock.acquire()
            self._unmatched_users.append(chat_id)
            self._unmatched_users_lock.release()

            bot.send_message(chat_id, ChatBot.WAIT_MSG_STR)

    def _is_user_started(self, user_id):
        return self._is_user_paired(user_id) or self._is_user_waiting(user_id)

    def _is_user_paired(self, user_id):
        return user_id in self._user_to_user

    def _is_user_waiting(self, user_id):
        return user_id in self._unmatched_users

    @run_async
    def send_text_message_to_pair(self, bot, update):
        chat_id = update.message.chat_id
        if chat_id in self._user_to_user:
            pair_id = self._user_to_user[chat_id]
            bot.send_message(
                chat_id=pair_id,
                text=update.message.text)
        else:
            bot.send_message(chat_id, ChatBot.NO_PAIR_MSG)

    @run_async
    def end_cmd(self, bot, update):
        chat_id = update.message.chat_id
        if chat_id in self._user_to_user:
            pair_id = self._user_to_user[chat_id]

            self._user_to_user_lock.acquire()
            del self._user_to_user[chat_id]
            self._user_to_user_lock.release()

            bot.send_message(chat_id, text=ChatBot.END_CHAT_MSG)
            bot.send_message(pair_id, text=ChatBot.END_CHAT_MSG)
        else:
            bot.send_message(chat_id, text=ChatBot.NO_PAIR_MSG)


def main():
    updater = Updater(token='TOKEN')
    dispatcher = updater.dispatcher

    chat_bot = ChatBot()

    start_handler = CommandHandler(
        ChatBot.START_COMMAND_STR, chat_bot.start_cmd)

    end_handler = CommandHandler(
        ChatBot.END_COMMAND_STR, chat_bot.end_cmd)

    msg_handler = MessageHandler(
        Filters.text, chat_bot.send_text_message_to_pair)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(end_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
