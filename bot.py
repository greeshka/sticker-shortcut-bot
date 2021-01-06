from dotenv import load_dotenv
import os

from telegram import Bot
from telegram.ext import Updater

from basic_handlers import error, get_basic_handlers
from info_handlers import get_info_handlers
from add_to_db_handlers import get_add_to_db_handlers
from inline_query_handlers import get_inline_query_handlers

from setup_database import setup_database

# load all tokens and get bot_token
load_dotenv()
bot_token = os.environ.get("bot_token")

# initialize bot and dispatcher
bot = Bot(token=bot_token)
updater = Updater(bot_token, use_context=True)
dp = updater.dispatcher

# add handlers
dp.add_error_handler(error)

handlers_list = []
get_handlers_funcs = [
    get_basic_handlers, get_info_handlers, get_add_to_db_handlers,
    get_inline_query_handlers
]
for get_handlers in get_handlers_funcs:
    handlers_list.extend(get_handlers())

for handler in handlers_list:
    dp.add_handler(handler)

# set up database
setup_database()

# start bot
updater.start_polling()
