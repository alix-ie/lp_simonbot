import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import ephem
from datetime import datetime, date
import string
from geonamescache import GeonamesCache as gc
import random

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

chat_cities = {}


def collect_cities():
    cities_dict = gc().get_cities()
    cities_set = {cities_dict[val]['name'] for val in cities_dict}
    cities_abc = {char: set() for char in string.ascii_lowercase}

    for city in cities_set:
        cities_abc[city[0].lower()].add(city)

    return cities_abc


def cities(update, context):
    user_city = update.message.text

    try:
        user_city = user_city[user_city.index(' '):].strip()
    except ValueError:
        update.message.reply_text("I don't understand")
        return

    chat_id = update.effective_chat.id
    chat_status = chat_cities.get(chat_id, False)

    if not chat_status:
        chat_cities[chat_id] = set()

    if user_city == 'new game':
        chat_cities[chat_id].clear()
        update.message.reply_text("I'm ready")
        return

    if user_city in chat_cities[chat_id]:
        update.message.reply_text('This city has been already used')
        return

    chat_cities[chat_id].add(user_city)

    try:
        bot_city = random.choice(list(bot_cities[user_city[-1].lower()] - chat_cities[chat_id]))
        chat_cities[chat_id].add(bot_city)

        update.message.reply_text(f'{bot_city}, your turn')

    except KeyError:
        update.message.reply_text("I don't understand")

    except IndexError:
        chat_cities[chat_id].clear()
        update.message.reply_text("I don't know. Can we start over?")


def word_count(update, context):
    user_text = update.message.text.split()[1:]
    len_text = len(user_text)

    for word in user_text:
        if len(word) == 1 and word in string.punctuation:
            len_text -= 1

    if len_text == 0:
        update.message.reply_text('No words')
    elif len_text == 1:
        update.message.reply_text('1 word')
    else:
        update.message.reply_text(f'{len_text} words')


def harvest_moon(update, context):
    try:
        user_date = datetime.strptime(update.message.text.split()[1], '%d-%m-%Y')
    except ValueError:
        update.message.reply_text('Wrong date format')
        return

    user_date = user_date.strftime('%Y/%m/%d')

    next_date = ephem.localtime(ephem.next_full_moon(user_date))
    next_date = next_date.strftime('%d %B %Y')

    update.message.reply_text(f'Next full moon is on {next_date}')


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
    dp.add_handler(CommandHandler('next_full_moon', harvest_moon))
    dp.add_handler(CommandHandler('wordcount', word_count))
    dp.add_handler(CommandHandler('cities', cities))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has started')
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    bot_cities = collect_cities()
    main()
