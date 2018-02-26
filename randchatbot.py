from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import telegram
from random import randint


START_COMMAND_STR = "start"
WAIT_MSG_STR = "No users to match please wait"
MATCHED_MSG_STR = "You have matched chat"
NO_PAIR_MSG = "You have no pair"

unmatched_users = list()
user_to_user = dict()

def start(bot, update):
    chat_id = update.message.chat_id
    has_user = len(unmatched_users) != 0
    parir_user_id = unmatched_users[-1] if has_user != 0 else None
    
    if parir_user_id is not None:
        user_to_user[chat_id] = parir_user_id
        user_to_user[parir_user_id] = chat_id
        unmatched_users.pop()
        update.message.reply_text(MATCHED_MSG_STR)
        bot.send_message(chat_id=parir_user_id, text=MATCHED_MSG_STR)
    else:
        unmatched_users.append(chat_id)
        update.message.reply_text(WAIT_MSG_STR)
    


def send_text_message_to_pair(bot, update):
    chat_id = update.message.chat_id

    try:
        pair_id = user_to_user[chat_id]
        bot.send_message(
            chat_id=pair_id,
            text=update.message.text)
    except:
        update.message.reply_text(NO_PAIR_MSG)


def main():
    updater = Updater('346627696:AAEse-Ml2q32ONAgSPep8Dx_8x_SyNRYQOQ')
    dispatcher = updater.dispatcher

    start_handler = CommandHandler(START_COMMAND_STR, start)
    msg_handler = MessageHandler(Filters.text, send_message_to_pair)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
