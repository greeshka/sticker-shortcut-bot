import os
import mysql.connector

from functools import wraps

from dotenv import load_dotenv

import pandas as pd


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

        mydb.commit()

        mycursor.close()
        mydb.close()

        return to_return
    return inner


@open_close_database
def setup_database(mydb, mycursor):
    '''function to create all needed tables if they don't exist and
then insert default values'''

    create_command_calls(mycursor)
    create_user_info(mycursor)
    create_user_packs(mycursor)
    create_pack_info(mycursor)
    create_pack_stickers(mycursor)
    create_user_pack_roles(mycursor)


def create_command_calls(mycursor):
    '''create table with all bot command calls'''

    mycursor.execute('''
        create table if not exists command_calls (
            update_id int PRIMARY KEY,
            call_dttm datetime,
            chat_id int,
            user_id varchar(255),
            command_name varchar(255)
        );
        ''')


def create_user_info(mycursor):
    '''create table with all users who used /start at least once'''
    mycursor.execute('''
        create table if not exists user_info (
            user_id int PRIMARY KEY,
            username varchar(255),
            language_code varchar(255),
            start_dttm datetime
        );
        ''')


def create_user_packs(mycursor):
    '''create table with packs that this user can use
by default everyone can use default pack and his private pack'''
    mycursor.execute('''
        create table if not exists user_packs (
            user_id int,
            pack_id int,
            added_dttm datetime
        );
        ''')


def create_pack_info(mycursor):
    '''create table with description of all existing packs
and insert default pack'''
    mycursor.execute('''
        create table if not exists pack_info (
            pack_id int AUTO_INCREMENT PRIMARY KEY,
            pack_name varchar(255),
            pack_author_id int,
            create_dttm datetime
        );
        ''')

    mycursor.execute('select * from pack_info where pack_id = 1')
    result = mycursor.fetchall()
    if len(result) == 0:
        sql = '''insert into pack_info
            values (%s, %s, %s, %s)'''
        val = (1, 'default', -1, '1960-01-01 00:00:00')
        mycursor.execute(sql, val)


def create_pack_stickers(mycursor):
    '''create table for stickers in pack and insert default pack stikers'''
    mycursor.execute('''
        create table if not exists pack_stickers (
            pack_id int,
            sticker_id varchar(255),
            sticker_shortcut varchar(255),
            user_added_id int,
            added_dttm datetime
        );
        ''')

    mycursor.execute('select * from pack_stickers where pack_id = 1')
    result = mycursor.fetchall()
    if len(result) == 0:
        default_stickers = pd.read_csv('data/default_stickers.csv')
        default_stickers['pack_id'] = 1
        default_stickers['user_added_id'] = -1
        default_stickers['added_dttm'] = '1960-01-01 00:00:00'

        sql = '''insert into pack_stickers
            values (%s, %s, %s, %s, %s)'''
        val = default_stickers[[
            'pack_id', 'sticker_id', 'sticker_shortcut', 'user_added_id',
            'added_dttm'
        ]].values.tolist()

        mycursor.executemany(sql, val)


def create_user_pack_roles(mycursor):
    '''create table for admin roles for packs
        there can be only one role per user-pack pair'''
    mycursor.execute(
        '''
        create table if not exists user_pack_roles (
            user_id int,
            pack_id int,
            role varchar(255),
            user_granted_id int,
            granted_dttm datetime
            );
        '''
    )


if __name__ == '__main__':
    setup_database()
