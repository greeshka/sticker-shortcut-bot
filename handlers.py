from functools import wraps

from setup_database import open_close_database


def logging_decorator(func):
    @wraps(func)
    @open_close_database
    def inner(update, context, mydb=None, mycursor=None):
        user_data = {}
        user_data['update_id'] = update.update_id
        user_data['message_date'] = update.message.date
        user_data['chat_id'] = update.message.chat.id
        user_data['username'] = update.message.chat.username

        # because there is confusion between python help and bot help
        if func.__name__ == 'helpX':
            user_data['command_name'] = 'help'
        else:
            user_data['command_name'] = func.__name__

        sql = '''insert into command_calling
        values (%s, %s, %s, %s, %s)'''
        val = (
            user_data['update_id'], user_data['message_date'],
            user_data['chat_id'], user_data['username'],
            user_date['command_name']
        )

        mycursor.execute(sql, val)


def start(update, context):
    update.message.reply_text(f'''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')
