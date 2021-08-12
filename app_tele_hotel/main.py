import json
import re
import threading

from dotenv import dotenv_values
import time
from users import Users

from utility import mess_wait, user_bd, SearchHotel
from telebot import TeleBot, types, apihelper
import requests

config = dotenv_values(".env")
bot = TeleBot(config['TELEGRAM_API_TOKEN'])

info = '● /help — помощь по командам бота\n' \
       '● /lowprice — вывод самых дешёвых отелей в городе\n' \
       '● /highprice — вывод самых дорогих отелей в городе\n' \
       '● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n'


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = ''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtna = types.KeyboardButton('🏨Найти отель')
    itembtnv = types.KeyboardButton('📗 Руководство')
    itembtnd = types.KeyboardButton('🚧 О сервисе')
    markup.row(itembtna, itembtnv)
    markup.row(itembtnd)
    if message.text == '/start':
        user_bd[message.from_user.id] = Users(message.from_user.id)
        print(user_bd[message.from_user.id])
        start_help_text = f"Привет {username}, я БОТ Too Easy Travel✅,\n" \
                          "И я смогу подобрать для тебя отель 🏨 или хостел 🏩"
        bot.send_message(message.from_user.id, start_help_text, reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, info, reply_markup=markup)


@bot.message_handler(content_types=['text', 'document', 'audio', 'photo'])
def get_text_messages(message):
    if message.text == '🏨Найти отель':
        user_bd[message.from_user.id] = Users(message.from_user.id)
        # bot.send_message(message.from_user.id, "В каком городе будем искать отель?")
        user_bd[message.from_user.id].check_choice_city = True
        markup = types.InlineKeyboardMarkup()
        low_price = types.InlineKeyboardButton(text='Самый дешёвый в городе', callback_data='/lowprice')
        high_price = types.InlineKeyboardButton(text='Самый дорогой в городе', callback_data='/highprice')
        best_deal = types.InlineKeyboardButton(text='фильтр по цене и расположению от центра',
                                               callback_data='/bestdeal')
        markup.add(low_price, high_price, best_deal, row_width=True)
        bot.send_message(message.from_user.id, "⚙ выберете способ поиска", reply_markup=markup)

    elif message.text == '📗 Руководство':
        bot.send_message(message.from_user.id, info)

    elif message.text == '/lowprice':
        user_bd[message.from_user.id] = Users(message.from_user.id)
        """После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print('Тут бизнес логика lowprice')
    elif message.text == '/highprice':
        user_bd[message.from_user.id] = Users(message.from_user.id)

        """После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print('Тут бизнес логика highprice')
    elif message.text == '/bestdeal':
        user_bd[message.from_user.id] = Users(message.from_user.id)

        """
        После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Диапазон цен.
        3. Диапазон расстояния, на котором находится отель от центра.
        4. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print('Тут бизнес логика bestdeal')
    elif user_bd[message.from_user.id].check_choice_city:
        user_bd[message.from_user.id].check_choice_city = False
        SearchHotel.SearchCityData(bot, message)

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    User = user_bd[c.message.chat.id]
    User.bool_city = True

    if User.bool_city:
        if c.data == '/lowprice':
            print('/lowprice salam')
            markup = types.InlineKeyboardMarkup()
            low_price = types.InlineKeyboardButton(text='1', callback_data='1')
            high_price = types.InlineKeyboardButton(text='2', callback_data='2')
            best_deal = types.InlineKeyboardButton(text='3',
                                                   callback_data='3')
            markup.add(low_price, high_price, best_deal, row_width=True)
            bot.send_message(User.id_user, "Какое кол-во отелей вывести?")
            User.bool_city = False
            User.id_city = User.data['suggestions'][0]['entities'][int(c.data)][
                'destinationId']
            print(User.id_user)
            print(User.id_city)
            print('id города', User.id_city)
            # req_get_hotels = requests.get()
            apihelper.delete_message('1921101611:AAHACgqfBNMQJGpFIGk2NDrBmZhpNQzYf90', c.message.chat.id,
                                     c.message.message_id)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as ex:
            # TODO Доработаь Обработка ошибок
            pass
