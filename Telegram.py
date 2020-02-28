import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import json
import re
from threading import Event
from time import time
from datetime import timedelta
import roomLookup
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    keyboard = [[InlineKeyboardButton("Zentrum", callback_data='Z'),
        InlineKeyboardButton("Höngerberg", callback_data='H')],
       [InlineKeyboardButton("CAB/CHN", callback_data='C'),
       InlineKeyboardButton("ETF/ETZ", callback_data='E'),
       InlineKeyboardButton("HG", callback_data='HG'),
       InlineKeyboardButton("ML/NO", callback_data='NO')
       ],
       [
       InlineKeyboardButton("IFW/RZ", callback_data='F'),
       InlineKeyboardButton("HCI", callback_data='HCI'),
       InlineKeyboardButton("HIL", callback_data='HIL'),
       InlineKeyboardButton("HIT", callback_data='HIT')
       ]
       ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Hello! Where do you want to look for rooms?', reply_markup=reply_markup)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hello! This bot can tell you which rooms are currently not in use at ETH.')

def form(data):
    if(len(data) == 0):
        return "No free rooms found, sorry :(\n"

    res = ""
    for entry in data:
        res += entry[2][2] + " " + entry[2][3] + " " + entry[2][4] + ": " + str(int(entry[0]/60)).zfill(2) + ":" + str(int(entry[0])%60).zfill(2) + " - " + str(int(entry[1]/60)).zfill(2) + ":" + str(entry[1]%60).zfill(2) + "\n"

    return res

def button(update, context):
    query = update.callback_query

    con = query.data

    dt = datetime.datetime.today()
    date = [dt.day, dt.strftime("%b"),dt.year]
    time = [dt.hour, dt.minute]

    filter = None

    if con == "HG":
        filter = lambda room: (room[2] == "HG")
    elif con == "Z":
        filter = lambda room: (room[1] == "Z")
    elif con == "H":
        filter = lambda room: (room[1] == "H")
    elif con == "HIL":
        filter = lambda room: (room[2] == "HIL")
    elif con == "HCI":
        filter = lambda room: (room[2] == "HCI")
    elif con == "HIT":
        filter = lambda room: (room[2] == "HIT")
    elif con == "HIT":
        filter = lambda room: (room[2] == "HIT")
    elif con == "HIT":
        filter = lambda room: (room[2] == "HIT")
    elif con == "NO":
        filter = lambda room: (room[2] == "NO" or room[2] == "ML")
    elif con == "E":
        filter = lambda room: (room[2] == "ETF" or room[2] == "ETZ")
    elif con == "C":
        filter = lambda room: (room[2] == "CAB" or room[2] == "CHN")
    elif con == "F":
        filter = lambda room: (room[2] == "IFW" or room[2] == "RZ")

    res = form(roomLookup.lookUpOn(date, time, filter)) + "\nType /start for more rooms!"

    query.edit_message_text(text=res[0:4096])


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def refresh(bot):
    dt = datetime.datetime.today()
    roomLookup.refreshData([dt.day, dt.strftime("%b"),dt.year])

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = open("token", "r").read()
    #refresh(None)
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    job_queue = updater.job_queue

    # Periodically save jobs

    job_queue.run_repeating(refresh, timedelta(minutes=1))


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
