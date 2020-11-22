from dotenv import load_dotenv
import os

import telegram
from telegram.ext import Updater, CommandHandler
import logging

from handlers import start, error
from setup_database import setup_database

# get bot_token
load_dotenv()
bot_token = os.environ.get("bot_token")

# set up logger
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# initialize bot and dispatcher
bot = telegram.Bot(token=bot_token)
updater = Updater(bot_token, use_context=True)
dp = updater.dispatcher

# add handlers
dp.add_error_handler(error)
dp.add_handler(CommandHandler('start', start))

# set up database
# setup_database()

# start bot
updater.start_polling()
