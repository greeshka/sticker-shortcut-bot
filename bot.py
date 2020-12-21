from dotenv import load_dotenv
import os

import telegram
from telegram.ext import Updater, CommandHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters

from handlers import start, helpX
from handlers import error
from handlers import feedback_call, feedback_message, cancel
from handlers import add_sticker, sticker, sticker_shortcut

from setup_database import setup_database

# consts for conversation handlers
FEEDBACK_MESSAGE = 0
STICKER, STICKER_SHORTCUT = range(2)

# load all tokens and get bot_token
load_dotenv()
bot_token = os.environ.get("bot_token")

# initialize bot and dispatcher
bot = telegram.Bot(token=bot_token)
updater = Updater(bot_token, use_context=True)
dp = updater.dispatcher

# define some handlers
conv_feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback_call)],
    states={FEEDBACK_MESSAGE: [MessageHandler(
        filters=None, callback=feedback_message
    )]},
    fallbacks=[CommandHandler('cancel', cancel)])

conv_sticker_handler = ConversationHandler(
    entry_points=[CommandHandler('add_sticker', add_sticker)],
    states={
        STICKER: [MessageHandler(Filters.sticker, sticker)],
        STICKER_SHORTCUT: [MessageHandler(Filters.text, sticker_shortcut)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# add handlers
dp.add_error_handler(error)
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', helpX))
dp.add_handler(conv_feedback_handler)
dp.add_handler(conv_sticker_handler)

# set up database
setup_database()

# start bot
updater.start_polling()
