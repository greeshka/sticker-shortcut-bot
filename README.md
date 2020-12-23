## Telegram bot for typing stickers from keyboard
This bot helps you to access stickers from keyboard! You can save stickers with shortcuts and then find them in any chat by calling the bot in inline mode. <br> <br>
I was inspired by Slack emojis. <br> <br>
Feel free to try: [StickerKeyboardBot](https://t.me/StickerKeyboardBot) <br> <br>
Right now the bot is not functioning due to complete changes in the structure. 

## How does it work?

This bot heavily relies on [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) package. There is a MySQL database with sticker packs. When user tries to send a sticker, script searches through all sticker packs assigned to him and lists all sticker which shortcut matches what user sends. Users can also save stickers to database with their own shortcuts for personal use.  

## Repository structure

Main file is `bot.py`. Handling different commands and whole conversations is done in `handlers.py`. `setup_database.py` is a file for creating all tables needed for sticker database. Preparing the bot for a new user is done in `first_interaction.py`.

## Plans for the future

- Complete basic features:
  - Saving stickers to private pack.
  - Sending stickers from default and private pack.
- Test this bot with a small amount of people. 
- Collect feedback and decide if the bot is ready for mass use or if it misses crucial features.
- Add crucial features if there are any.
- Advertise the bot somehow.

## Possible steps

- Add tests. Right now I don't understand what is the best way of doing this for the bot.
- Add some sort of tools to analyze usage of the bot to search for possible problems.
- Add some tools to track enjoyment from the bot. 
- ??? I would be happy to receive any advice!
