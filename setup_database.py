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
        update_id int PRIMARY KEY,
        call_dttm datetime,
        chat_id int,
        user_id varchar(255),
        command_name varchar(255)
    );''')

    # table with user info
    # every user must appear only once
    mycursor.execute('''
    create table if not exists user_info (
        user_id int PRIMARY KEY,
        username varchar(255),
        language_code varchar(255),
        start_dttm datetime
    );
    ''')

    # table with packs that user can use
    # by default everyone should have default pack
    mycursor.execute('''
    create table if not exists user_packs (
        user_id int PRIMARY KEY,
        pack_id int,
        added_dttm datetime
    );
    ''')

    # table with sticker packs info
    mycursor.execute('''
    create table if not exists pack_info (
        pack_id int AUTO_INCREMENT PRIMARY KEY,
        pack_name varchar(255),
        pack_author_id int,
        create_dttm datetime
    );
    ''')

    # insert default pack
    mycursor.execute('select * from pack_info where pack_id = 1')
    result = mycursor.fetchall()
    if len(result) == 0:
        sql = '''insert into pack_info
            values (%s, %s, %s, %s)'''
        val = (1, 'default', -1, '2020-12-20 00:00:00')
        mycursor.execute(sql, val)

    # table with stickers in pack
    mycursor.execute('''
    create table if not exists pack_stickers (
        pack_id int PRIMARY KEY,
        sticker_id int,
        sticker_shortcut varchar(255),
        user_added_id int,
        added_dttm datetime
    );
    ''')

    # insert default pack to pack_info


if __name__ == '__main__':
    setup_database()
