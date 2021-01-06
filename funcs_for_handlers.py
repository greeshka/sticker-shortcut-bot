from functools import wraps
import os
import mysql.connector

from first_interaction import first_interaction_setup

from telegram.ext import ConversationHandler


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
def cancel(update, context):
    update.message.reply_text(
        'Something cancelled... \nI hope everything is ok!')
    context.user_data.clear()
    return ConversationHandler.END
