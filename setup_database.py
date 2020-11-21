from dotenv import load_dotenv
import os
import mysql.connector


def setup_database():
    load_dotenv()
    database_token = os.getenv('database_token')

    mydb = mysql.connector.connect(
        host="localhost",
        user="marcy",
        password=database_token,
        database='marcy_sticker_bot'
    )

    mycursor = mydb.cursor()

    mycursor.execute('''
    create table if not exists command_calling (
        update_id int,
        message_date datetime,
        chat_id int,
        username varchar(255),
        command_name varchar(255),
    )''')
