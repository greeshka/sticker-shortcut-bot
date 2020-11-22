from functools import wraps
import os
import mysql.connector

import logging

from setup_database import open_close_database


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
        user_data['message_datetime'] = update.message.date.strftime(
            '%Y-%m-%d %H:%M:%S')
        user_data['chat_id'] = update.message.chat.id
        user_data['username'] = update.message.chat.username

        # because there is a confusion between python help and bot help
        if func.__name__ == 'helpX':
            user_data['command_name'] = 'help'
        else:
            user_data['command_name'] = func.__name__

        # insert all information into database
        sql = '''insert into command_calling
        values (%s, %s, %s, %s, %s);'''
        val = (
            user_data['update_id'], user_data['message_datetime'],
            user_data['chat_id'], user_data['username'],
            user_data['command_name']
        )
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        mydb.close()

        return func(update, context)
    return inner


@logging_decorator
def start(update, context):
    update.message.reply_text(f'''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')


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
