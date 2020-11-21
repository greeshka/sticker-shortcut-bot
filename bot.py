from dotenv import load_dotenv
import os

import telegram
from telegram.ext import Updater, CommandHandler
import logging

from handlers import start

# get bot_token
load_dotenv()
bot_token = os.environ.get("bot_token")

# set up logging
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
dp.add_handler(CommandHandler('start', start))

# start bot
updater.start_polling()
