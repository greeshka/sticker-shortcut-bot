from functools import wraps
import os
import mysql.connector

import logging

import telegram
from telegram import InlineQueryResultCachedSticker
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, Filters
    )

import pandas as pd

from dotenv import load_dotenv

from uuid import uuid4

from first_interaction import first_interaction_setup
from setup_database import open_close_database

# load tokens
load_dotenv()

# consts for conversation handlers
FEEDBACK_MESSAGE = 0
STICKER, STICKER_SHORTCUT = range(2)

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


@logging_decorator
def start(update, context):
    update.message.reply_text(f'''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')


@logging_decorator
def helpX(update, context):
    update.message.reply_text("""<b>How to use the bot</b>

To send stickers type @StickerKeyboardBot in any chat and begin typing the \
name of the sticker.

You can look at the list of stickers you can use right now with \
/my_stickers command.
You already have stickers from the default pack.

Bot searches stickers that contain your inline query as a substring, \
therefore you can find \"smiling_frog\" sticker typing \"sm\" or \
\"fr\" or even nothing!

To save stickers use /add_sticker and follow instructions. Right now you \
can only save stickers to your private pack.

If you wish to share some feedback feel free to use /feedback.

Good luck!""", parse_mode='html')


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


@open_close_database
def my_stickers(update, context, mydb, mycursor):
    user_id = update.message.from_user.id
    sql = '''
        select
            t2.pack_name,
            t3.sticker_shortcut
        from user_packs t1

            inner join pack_info t2
            on true
                and t1.user_id = %s
                and t1.pack_id = t2.pack_id

            inner join pack_stickers t3
            on t1.pack_id = t3.pack_id
            ;'''
    val = (user_id,)
    mycursor.execute(sql, val)

    pack_shortcut = mycursor.fetchall()
    pack_sticker_list = pd.DataFrame(
        pack_shortcut,
        columns=['pack_name', 'sticker_shortcut']).groupby('pack_name')[
            'sticker_shortcut'
            ].apply(lambda x: x.tolist()).reset_index().values.tolist()

    answer = '\n\n'.join(
        f'<b>{pack}</b>:\n' + '\n'.join(stickers)
        for pack, stickers in pack_sticker_list)

    update.message.reply_text(
        f'These are stickers you can currently use \
sorted by packs:\n\n{answer}',
        parse_mode='html')


def get_conv_feedback_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback_call)],
        states={FEEDBACK_MESSAGE: [MessageHandler(
            filters=Filters.text, callback=feedback_message
        )]},
        fallbacks=[CommandHandler('cancel', cancel)])


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


def get_conv_sticker_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('add_sticker', add_sticker)],
        states={
            STICKER: [MessageHandler(Filters.sticker, sticker)],
            STICKER_SHORTCUT: [MessageHandler(Filters.text, sticker_shortcut)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
        )


@logging_decorator
def add_sticker(update, context):
    update.message.reply_text('Send a sticker you wish to save')
    context.user_data['user_added_id'] = update.message.from_user.id

    return STICKER


@logging_decorator
def sticker(update, context):
    context.user_data['sticker_id'] = update.message.sticker.file_id
    update.message.reply_text('Got it! Now send a shortcut for it')

    return STICKER_SHORTCUT


@logging_decorator
def sticker_shortcut(update, context):
    context.user_data['sticker_shortcut'] = update.message.text
    context.user_data['added_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')
    update.message.reply_text('Sticker saved!')
    add_sticker_preference(user_data=context.user_data)

    context.user_data.clear()
    return ConversationHandler.END


@open_close_database
def add_sticker_preference(mydb, mycursor, user_data):
    pack_name = 'private'
    sql = '''select pack_id from pack_info
        where pack_name = %s and pack_author_id = %s'''
    val = [pack_name, user_data['user_added_id']]

    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    pack_id = result[0][0]

    sql = '''insert into pack_stickers
        values (%s, %s, %s, %s, %s);'''
    val = [
        pack_id, user_data['sticker_id'], user_data['sticker_shortcut'],
        user_data['user_added_id'], user_data['added_dttm']
    ]
    mycursor.execute(sql, val)


def inline_query(update, context):
    user_id = update.inline_query.from_user.id
    query = update.inline_query.query
    sticker_list = sticker_list_by_query(user_id=user_id, query=query)
    results = [InlineQueryResultCachedSticker(
        id=uuid4(), sticker_file_id=sticker) for sticker in sticker_list]
    update.inline_query.answer(results, cache_time=15, is_personal=True)
    sticker_list.clear()
    results.clear()


@open_close_database
def sticker_list_by_query(mydb, mycursor, user_id, query):
    sql = '''
        select
            t2.sticker_id
        from user_packs t1

            inner join pack_stickers t2
        on true
            and t1.user_id = %s
            and t1.pack_id = t2.pack_id
            and t2.sticker_shortcut like %s;'''
    val = (user_id, '%' + query + '%')
    mycursor.execute(sql, val)
    result = mycursor.fetchall()

    return [sticker_info[0] for sticker_info in result]
