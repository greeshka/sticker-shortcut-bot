#!/usr/bin/env python
# coding: utf-8

# ## IDEAS
# #### 1. Overwrite older shortcuts
# #### 2. Guide with pictures in telegraph
# #### 3. Log somehow inline query stuff

# ### when calling /cancel sticker can still be saved

# In[1]:


import pandas as pd
from dotenv import load_dotenv
import os


# In[2]:


from functools import wraps


# In[3]:


import telegram
import logging
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, ConversationHandler, InlineQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultCachedSticker


# In[4]:


from uuid import uuid4


# In[5]:


load_dotenv()
TOKEN = os.environ.get("TOKEN")
FEEDBACK_BOT_CHAT_ID = os.environ.get('FEEDBACK_BOT_CHAT_ID')


# In[6]:


logging.basicConfig(filename='logs.log', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# In[7]:


STICKER, STICKER_SHORTCUT = range(2)
FEEDBACK_MESSAGE = 0


# ### Adding headers to .csv files if not already

# In[8]:


def add_header_csv(file_path, columns):
    with open(file_path, 'a+') as file:
        if os.stat(file_path).st_size == 0:
            string_to_add = '\t'.join(columns) + '\n'
            file.write(string_to_add)


# In[9]:


add_header_csv(
    file_path='sticker_preferences.csv', 
    columns=['update_id', 'message_date', 'chat_id', 'username', 'sticker_file_id', 'sticker_shortcut'])


# In[10]:


add_header_csv(
    file_path='command_calling.csv', 
    columns=['update_id', 'message_date', 'chat_id', 'username', 'command_name'])


# ### Decorator for logging bot command calls

# In[11]:


def logging_dec(func):
    @wraps(func)
    def inner(update, context):
        user_data = {}
        user_data['update_id'] = update.update_id
        user_data['message_date'] = update.message.date
        user_data['chat_id'] = update.message.chat.id
        user_data['username'] = update.message.chat.username
        if func.__name__ == 'helpX': # because there is confusion between python help and bot help
            user_data['command_name'] = 'help'
        else:
            user_data['command_name'] = func.__name__
        columns = ['update_id', 'message_date', 'chat_id', 'username', 'command_name']
        
        add_header_csv(
            file_path='command_calling.csv', 
            columns=['update_id', 'message_date', 'chat_id', 'username', 'command_name'])
        
        with open('command_calling.csv', 'a+') as file:
            string_to_add = '\t'.join([str(user_data[column]) for column in columns]) + '\n'
            file.write(string_to_add)
        return func(update, context)
    return inner


# ### Functions for service handlers

# In[12]:


@logging_dec
def start(update, context):
    update.message.reply_text('''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')

@logging_dec
def helpX(update, context):
    update.message.reply_text("""
To send stickers type @StickerKeyboardBot in any chat and begin typing name of the sticker you've already saved. 
If you haven't saved any stickers yet you can always send the smiling_frog from the bot profile photo! 
By the way you can start typing from the middle of the word, "fr", for example, and the bot will still understand.

To save stickers use /add_sticker and follow instructions.

If you wish to share some feedback feel free to use /feedback

Good luck!""")
    
def error(update, context):
    logger.warning(f'UPDATE {update}\n CONTEXT {context.error}\n FROM ERROR {context.from_error}')


# ### Functions for feedback conversation handler

# In[13]:


@logging_dec
def feedback_call(update, context):
    update.message.reply_text('Please share your experience!')
    
    return FEEDBACK_MESSAGE

def feedback_message(update, context):
    bot.forward_message(
        chat_id=FEEDBACK_BOT_CHAT_ID, 
        from_chat_id=update.effective_chat.id, 
        message_id=update.message.message_id)    
    update.message.reply_text('Thanks!')
    return ConversationHandler.END


# ### Functions for sticker conversation handler

# In[14]:


@logging_dec
def add_sticker(update, context):
    update.message.reply_text('Send a sticker you wish to save')
    context.user_data['update_id'] = update.update_id
    context.user_data['message_date'] = update.message.date
    context.user_data['chat_id'] = update.message.chat.id
    context.user_data['username'] = update.message.chat.username

    return STICKER

@logging_dec
def sticker(update, context):
    context.user_data['sticker_file_id'] = update.message.sticker.file_id
    update.message.reply_text('Got it! Now send a shortcut for it')
    
    return STICKER_SHORTCUT

@logging_dec
def sticker_shortcut(update, context):
    context.user_data['sticker_shortcut'] = update.message.text
    update.message.reply_text('Sticker saved!')
    add_sticker_preference('sticker_preferences.csv', context.user_data)
    
    context.user_data.clear()
    return ConversationHandler.END

def add_sticker_preference(file_path, user_data):
    columns = ['update_id', 'message_date', 'chat_id', 'username', 'sticker_file_id', 'sticker_shortcut']
    with open(file_path, 'a+') as file:
        if os.stat(file_path).st_size == 0:
            string_to_add = '\t'.join(columns) + '\n'
            file.write(string_to_add)         
        string_to_add = '\t'.join([str(user_data[column]) for column in columns]) + '\n'

        file.write(string_to_add)

@logging_dec
def cancel(update, context):
    update.message.reply_text('Something cancelled... \nI hope everything is ok!')
    context.user_data.clear()
    return ConversationHandler.END


# ### Functions for inline query

# In[15]:


def sticker_list_by_query(username, query):
    df = pd.read_csv('sticker_preferences.csv', sep='\t')
    return list(df[(df['username'].isin([username, '#nonexisting_user'])) & 
                   (df['sticker_shortcut'].str.contains(query))]['sticker_file_id'].unique())

def inline_query(update, context):
    username = update.inline_query.from_user.username
    query = update.inline_query.query
    sticker_list = sticker_list_by_query(username, query)
    results = [InlineQueryResultCachedSticker(
        id=uuid4(), sticker_file_id=sticker) for sticker in sticker_list]
    update.inline_query.answer(results, cache_time=0, is_personal=True)
    sticker_list.clear()
    results.clear()
    


# ### Initializing

# In[16]:


bot = telegram.Bot(token=TOKEN)
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher


# ### Handlers

# In[17]:


start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)


# In[18]:


# dp.remove_handler(start_handler)


# In[19]:


help_handler = CommandHandler('help', helpX)
dp.add_handler(help_handler)


# In[20]:


# dp.remove_handler(help_handler)


# In[21]:


dp.add_error_handler(error)


# In[22]:


# dp.remove_error_handler(error)


# In[23]:


conv_sticker_handler = ConversationHandler(
        entry_points=[CommandHandler('add_sticker', add_sticker)],

        states={
            STICKER: [MessageHandler(Filters.sticker, sticker)],
        STICKER_SHORTCUT: [MessageHandler(Filters.text, sticker_shortcut)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)
dp.add_handler(conv_sticker_handler)


# In[24]:


# dp.remove_handler(conv_sticker_handler)


# In[25]:


conv_feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback_call)], 
    states={FEEDBACK_MESSAGE: [MessageHandler(filters=None, callback=feedback_message)]}, 
    fallbacks=[CommandHandler('cancel', cancel)])
dp.add_handler(conv_feedback_handler)


# In[26]:


# dp.remove_handler(conv_feedback_handler)


# In[27]:


inline_query_handler = InlineQueryHandler(inline_query)
dp.add_handler(inline_query_handler)


# In[28]:


# dp.remove_handler(inline_query_handler)


# ### Starting the bot

# In[29]:


updater.start_polling()


# ### Sandbox

# In[30]:


# with open('sticker_preferences.csv', 'a+') as file:
#     string_to_add = '\t'.join([
#         str(0), '1960-01-01 00:00:00', str(0), '#nonexisting_user2', 
#         'CAACAgIAAxkBAANAXqv52JSrszp6aKaaSciqpbcfRfYAAv4TAAKezgsAARuSPfSbfsZaGQQ', 
#         'cat_waiting']) + '\n'
#     file.write(string_to_add)

