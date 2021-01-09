from funcs_for_handlers import logging_decorator, cancel
from setup_database import open_close_database

from telegram.ext import (
    ConversationHandler, MessageHandler, CommandHandler, Filters)

# consts for conversation handlers
STICKER, STICKER_SHORTCUT, PACK_ID = range(3)
SET_PACK_NAME = 0


def get_add_to_db_handlers():
    return [
        get_conv_sticker_handler(),
        get_create_pack_handler()
    ]


def get_conv_sticker_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('add_sticker', add_sticker)],
        states={
            STICKER: [MessageHandler(Filters.sticker, sticker)],
            STICKER_SHORTCUT: [MessageHandler(Filters.text, sticker_shortcut)],
            PACK_ID: [MessageHandler(Filters.text, pack_id)]
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
    user_id = update.message.from_user.id
    pack_id_name = get_admin_packs(user_id=user_id)
    answer = '\n'.join([
        f'{pack_name}: {pack_id}' for pack_id, pack_name in pack_id_name
        ])

    update.message.reply_text(f'''Now select an id of the pack to add to.
Your packs with admin rights:\n\n{answer}''')

    return PACK_ID


@logging_decorator
def pack_id(update, context):
    user_id = update.message.from_user.id
    pack_id_name = get_admin_packs(user_id=user_id)
    pack_ids = [x[0] for x in pack_id_name]

    text_pack_id = update.message.text

    try:
        pack_id = int(text_pack_id)
    except ValueError:
        update.message.reply_text(
            'Pack id should be a number')
        return ConversationHandler.END

    if pack_id not in pack_ids:
        update.message.reply_text(
            'You don\'t have admin rights for this pack')
        return ConversationHandler.END

    context.user_data['pack_id'] = pack_id
    add_sticker_preference(user_data=context.user_data)

    update.message.reply_text(
        'Sticker added successfully!')

    return ConversationHandler.END


@open_close_database
def get_admin_packs(mydb, mycursor, user_id):
    sql = '''
        select
            t1.pack_id,
            t2.pack_name
        from user_pack_roles t1

            inner join pack_info t2
            on true
                and t1.user_id = %s
                and t1.role = 'admin'
                and t1.pack_id = t2.pack_id;'''
    val = (user_id,)
    mycursor.execute(sql, val)
    pack_id_name = mycursor.fetchall()

    return pack_id_name


@open_close_database
def add_sticker_preference(mydb, mycursor, user_data):
    sql = '''insert into pack_stickers
        values (%s, %s, %s, %s, %s);'''
    val = [
        user_data['pack_id'], user_data['sticker_id'],
        user_data['sticker_shortcut'], user_data['user_added_id'],
        user_data['added_dttm']
    ]
    mycursor.execute(sql, val)


def get_create_pack_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('create_pack', create_pack)],
        states={
            SET_PACK_NAME: [MessageHandler(Filters.text, set_pack_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
        )


@logging_decorator
def create_pack(update, context):
    update.message.reply_text('Send a name for your pack. \
Keep in mind that for now all non-personal packs are public.')
    return SET_PACK_NAME


@open_close_database
def set_pack_name(update, context, mydb, mycursor):
    user_data = {}
    user_data['pack_name'] = update.message.text
    user_data['pack_author_id'] = update.message.from_user.id
    user_data['create_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')
    user_data['type'] = 'public'

    sql = '''insert into pack_info (
        pack_name, pack_author_id, create_dttm, type)
        values (%s, %s, %s, %s)'''
    val = (
        user_data['pack_name'], user_data['pack_author_id'],
        user_data['create_dttm'], user_data['type']
    )
    mycursor.execute(sql, val)

    # sql = '''
    #     select
    #         pack_id
    #     from pack_info
    #     where true
    #         and pack_name = %s
    #         and pack_author_id = %s
    #         and create_dttm = %s'''
    # val = (
    #     user_data['pack_name'], user_data['pack_author_id'],
    #     user_data['create_dttm']
    # )
    # mycursor.execute(sql, val)
    # result = mycursor.fetchall()
    # created_pack_id = result[0][0]

    # sql = '''insert into user_packs
    #     values (%s, %s, %s)'''
    # val = (
    #     user_data['pack_author_id'], created_pack_id,
    #     user_data['create_dttm']
    # )
    # mycursor.execute(sql, val)
