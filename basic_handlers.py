from funcs_for_handlers import logging_decorator, cancel

import logging

import os
from dotenv import load_dotenv

import telegram
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, Filters)

# load tokens
load_dotenv()

# consts for conversation handlers
FEEDBACK_MESSAGE = 0

bot = telegram.Bot(token=os.getenv('bot_token'))


def get_basic_handlers():
    return [
        CommandHandler('start', start),
        CommandHandler('help', helpX),
        get_conv_feedback_handler()
    ]


@logging_decorator
def start(update, context):
    update.message.reply_text(f'''Hi there!
I can help you to quickly access stickers via keaborad.
Use /help for instructions.''')


@logging_decorator
def helpX(update, context):
    update.message.reply_text("""<b>How to use the bot</b>

To send stickers type @StickerKeyboardBot in any chat and begin typing the \
name of the sticker.

You can look at the list of stickers you can use right now with \
/my_stickers command. Same for packs with /my_packs command.
You already have stickers from the default pack.

Bot searches stickers that contain your inline query as a substring, \
therefore you can find \"smiling_frog\" sticker typing \"sm\" or \
\"fr\" or even nothing!

To save stickers use /add_sticker and follow instructions.
You can create new packs with /create_pack.

If you wish to share some feedback feel free to use /feedback.

Good luck!""", parse_mode='html')


def error(update, context):
    logging.basicConfig(
        filename='logs.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(
        f'''

UPDATE {update}
CONTEXT {context.error}
FROM ERROR {context.from_error}''')


def get_conv_feedback_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback_call)],
        states={FEEDBACK_MESSAGE: [MessageHandler(
            filters=Filters.text & ~Filters.command, callback=feedback_message
        )]},
        fallbacks=[CommandHandler('cancel', cancel)])


@logging_decorator
def feedback_call(update, context):
    update.message.reply_text('Please share your experience!')

    return FEEDBACK_MESSAGE


def feedback_message(update, context):
    bot.forward_message(
        chat_id=os.getenv('feedback_bot_chat_id'),
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id)
    update.message.reply_text('Thanks!')
    return ConversationHandler.END
