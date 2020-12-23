from dotenv import load_dotenv
import os

import telegram
from telegram.ext import Updater, CommandHandler, InlineQueryHandler

from handlers import (
    start, helpX,
    error,
    get_conv_feedback_handler, get_conv_sticker_handler,
    inline_query)

from setup_database import setup_database

# load all tokens and get bot_token
load_dotenv()
bot_token = os.environ.get("bot_token")

# initialize bot and dispatcher
bot = telegram.Bot(token=bot_token)
updater = Updater(bot_token, use_context=True)
dp = updater.dispatcher

# add handlers
dp.add_error_handler(error)

dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', helpX))

dp.add_handler(get_conv_feedback_handler())
dp.add_handler(get_conv_sticker_handler())

dp.add_handler(InlineQueryHandler(inline_query))

# set up database
setup_database()

# start bot
updater.start_polling()
