import os
import mysql.connector

from functools import wraps

from dotenv import load_dotenv


def open_close_database(func):
    '''decorator to open and close database'''
    @wraps(func)
    def inner(*args, **kwargs):

        load_dotenv()

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
    '''function to create all needed tables if they don't exist'''

    # table with command calls
    mycursor.execute('''
    create table if not exists command_calls (
        update_id int,
        call_dttm datetime,
        chat_id int,
        user_id varchar(255),
        command_name varchar(255)
    );''')

    # table with user info
    # every user must appear only once
    mycursor.execute('''
    create table if not exists users (
        user_id int,
        username varchar(255),
        language_code varchar(255),
        start_dttm datetime
    );
    ''')

    # table with packs that user can use
    # by default everyone should have default pack
    mycursor.execute('''
    create table if not exists user_packs (
        user_id int,
        pack_id int,
        added_dttm datetime
    );
    ''')

    # table with sticker packs info
    mycursor.execute('''
    create table if not exists packs (
        pack_id int,
        pack_name varchar(255),
        pack_author_id int,
        create_dttm datetime
    );
    ''')

    # table with stickers in pack
    mycursor.execute('''
    create table if not exists pack_stickers (
        pack_id int,
        sticker_id int,
        sticker_shortcut varchar(255),
        user_added_id int,
        added_dttm datetime
    );
    ''')


if __name__ == '__main__':
    setup_database()
