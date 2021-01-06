from telegram import InlineQueryResultCachedSticker
from telegram.ext import InlineQueryHandler

from uuid import uuid4

from setup_database import open_close_database


def get_inline_query_handlers():
    return [
        InlineQueryHandler(inline_query)
    ]


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
