import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import ephem
from datetime import date

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}


def constellation(update, context):
    name = update.message.text.split()[1].capitalize()

    try:
        space_object = getattr(ephem, name)(date.today().strftime('%Y/%m/%d'))
        location = ephem.constellation(space_object)

        update.message.reply_text(f'{name} is currently in the constellation of {location[1]}')

    except AttributeError:
        update.message.reply_text("I don't know, sorry")


def greet_user(update, context):
    print('/start was called')
    update.message.reply_text("I'm here!")


def talk_to_me(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('locate', constellation))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has started')
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
