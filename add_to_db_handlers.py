from funcs_for_handlers import logging_decorator, cancel
from setup_database import open_close_database

from telegram.ext import (
    ConversationHandler, MessageHandler, CommandHandler, Filters)

# consts for conversation handlers
STICKER, STICKER_SHORTCUT = range(2)


def get_add_to_db_handlers():
    return [
        get_conv_sticker_handler()
    ]


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
