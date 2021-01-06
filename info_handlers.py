# File for handlers which provide information

import pandas as pd

from setup_database import open_close_database

from telegram.ext import CommandHandler


def get_info_handlers():
    return [
        CommandHandler('my_stickers', my_stickers),
        CommandHandler('my_packs', my_packs)
    ]


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


@open_close_database
def my_packs(update, context, mydb, mycursor):
    user_id = update.message.from_user.id
    answer = get_user_packs(user_id=user_id)

    update.message.reply_text(
        f'These are names and ids of packs you can currently use:\n\n{answer}')


@open_close_database
def get_user_packs(user_id, mydb, mycursor):
    sql = '''
        select
            t1.pack_id,
            t2.pack_name
        from user_packs t1

            inner join pack_info t2
            on true
                and t1.user_id = %s
                and t1.pack_id = t2.pack_id
    '''
    val = (user_id,)
    mycursor.execute(sql, val)
    pack_id_name = mycursor.fetchall()

    answer = '\n'.join([
        f'{pack_name}: {pack_id}' for pack_id, pack_name in pack_id_name
        ])
    return answer
