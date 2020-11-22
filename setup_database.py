from dotenv import load_dotenv
import os
import mysql.connector

from functools import wraps


def open_close_database(func):
    @wraps(func)
    def inner(*args, **kwargs):
        database_token = os.getenv('database_token')

        mydb = mysql.connector.connect(
            host="localhost",
            user="marcy",
            password=database_token,
            database='marcy_sticker_bot'
        )
        mycursor = mydb.cursor()

        to_return = func(mydb=mydb, mycursor=mycursor, *args, **kwargs)

        mycursor.close()
        mydb.close()

        return to_return
    return inner


@open_close_database
def setup_database(mydb, mycursor):
    mycursor.execute('''
    create table if not exists command_calling (
        update_id int,
        message_datetime datetime,
        chat_id int,
        username varchar(255),
        command_name varchar(255)
    );''')


if __name__ == '__main__':
    setup_database()
