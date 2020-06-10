## Telegram bot for typing stickers from keyboard
This bot helps you to access stickers from keyboard! You can save stickers with shortcuts and then find them in any chat by calling the bot in inline mode. <br> <br>
I was inspired by Slack emojis. <br> <br>
Feel free to try: [StickerKeyboardBot](https://t.me/StickerKeyboardBot) <br> <br>

P.S. .py and .ipynb files are identical, I am just more comfortable with writing code in Jupyter Notebook (Sorry...) and running .py version of notebook in screen.

## How does it work?

You can begin a series of messages with /add_sticker command. Then a sticker_id for the sticker you've sent will be saved to preferences file with your username and shortcut (will be changed so that the bot doesn't read the whole file each time). After that you can call the bot in any chat in inline mode and begin to type some message. The bot will read the preferences file and suggest yours and everyone's stickers whose shortcuts contain your message as a subline. <br><br>
I also log every command call with a decorator so that when many people would actually use it, I could understand, where do people struggle. <br><br>
Any suggestions will be appreciated!
