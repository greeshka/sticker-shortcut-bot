from functools import wraps
import os
import mysql.connector

import logging

import telegram
from telegram.ext import ConversationHandler

from dotenv import load_dotenv

# load tokens
load_dotenv()

# consts for conversation handlers
FEEDBACK_MESSAGE = 0

# bot initialization
bot = telegram.Bot(token=os.getenv('bot_token'))


def logging_decorator(func):
    '''decorator for handlers to save every handler call to database'''
    @wraps(func)
    def inner(update, context):
        database_token = os.getenv('database_token')

        mydb = mysql.connector.connect(
            host="localhost",
            user="marcy",
            password=database_token,
            database='marcy_sticker_bot'
        )
        mycursor = mydb.cursor()

        # get all information needed
        user_data = {}
        user_data['update_id'] = update.update_id
        user_data['call_dttm'] = update.message.date.strftime(
            '%Y-%m-%d %H:%M:%S')
        user_data['chat_id'] = update.message.chat.id
        user_data['user_id'] = update.message.from_user.id

        # because there is a confusion between python help and bot help
        if func.__name__ == 'helpX':
            user_data['command_name'] = 'help'
        else:
            user_data['command_name'] = func.__name__

        # insert all information into database
        sql = '''insert into command_calls
            values (%s, %s, %s, %s, %s);'''
        val = (
            user_data['update_id'], user_data['call_dttm'],
            user_data['chat_id'], user_data['user_id'],
            user_data['command_name']
        )
        mycursor.execute(sql, val)

        # check if this is first interaction with the bot
        if func.__name__ == 'start':
            sql = '''select * from user_info where user_id = %s'''
            val = (update.message.from_user.id,)
            mycursor.execute(sql, val)
            result = mycursor.fetchall()

            # if nothing is returned set everything up for further use
            if len(result) == 0:
                first_interaction_setup(update, mycursor)

        mydb.commit()

        mycursor.close()
        mydb.close()

        return func(update, context)
    return inner


def first_interaction_setup(update, mycursor):
    '''Sets up tables for this user.
Must do:
1. Add user to user_info +
2. Add private pack for user to pack_info -
3. Add private pack and default pack to user_packs -'''

    # add user to user_info
    user_data = {}
    user_data['user_id'] = update.message.from_user.id
    user_data['username'] = update.message.chat.username
    user_data['language_code'] = update.message.from_user.language_code
    user_data['call_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')

    sql = '''insert into user_info
        values (%s, %s, %s, %s);'''
    val = (
        user_data['user_id'], user_data['username'],
        user_data['language_code'], user_data['call_dttm']
    )
    mycursor.execute(sql, val)

    # add private pack for user to pack_info
    # user_data = {}
    # user_data['user_id'] = update.message.from_user.id
    # user_data['']


@logging_decorator
def start(update, context):
    update.message.reply_text(f'''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')


@logging_decorator
def helpX(update, context):
    update.message.reply_text("""
To send stickers type @StickerKeyboardBot in any chat and begin typing name \
of the sticker you've already saved.
If you haven't saved any stickers yet you can always send the smiling_frog \
from the bot profile photo!
By the way you can start typing from the middle of the word, "fr", for \
example, and the bot will still understand.

To save stickers use /add_sticker and follow instructions.

If you wish to share some feedback feel free to use /feedback

Good luck!""")


def error(update, context):
    logging.basicConfig(
        filename='logs.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(
        f'''
UPDATE {update}
CONTEXT {context.error}
FROM ERROR {context.from_error}''')


@logging_decorator
def feedback_call(update, context):
    update.message.reply_text('Please share your experience!')

    return FEEDBACK_MESSAGE


def feedback_message(update, context):
    bot.forward_message(
        chat_id=os.getenv('feedback_bot_chat_id'),
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id)
    update.message.reply_text('Thanks!')
    return ConversationHandler.END


@logging_decorator
def cancel(update, context):
    update.message.reply_text(
        'Something cancelled... \nI hope everything is ok!')
    context.user_data.clear()
    return ConversationHandler.END
