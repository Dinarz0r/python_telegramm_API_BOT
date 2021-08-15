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
    if not user_bd.get(message.from_user.id):
        user_bd[message.from_user.id] = Users(message.from_user.id)
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
                          "И я смогу подобрать для тебя отель 🏨"
        bot.send_message(message.from_user.id, start_help_text, reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, info, reply_markup=markup)


@bot.message_handler(content_types=['text', 'document', 'audio', 'photo'])
def get_text_messages(message):
    if not user_bd.get(message.from_user.id):
        user_bd[message.from_user.id] = Users(message.from_user.id)
    if message.text == '🏨Найти отель':
        markup = types.InlineKeyboardMarkup()
        low_price = types.InlineKeyboardButton(text='Самый дешёвый в городе', callback_data='/lowprice')
        high_price = types.InlineKeyboardButton(text='Самый дорогой в городе', callback_data='/highprice')
        best_deal = types.InlineKeyboardButton(text='фильтр по цене и расположению от центра',
                                               callback_data='/bestdeal')
        markup.add(low_price, high_price, best_deal, row_width=True)
        massage_info = bot.send_message(message.from_user.id, "🔎 выберете способ поиска", reply_markup=markup)
        user_bd[message.from_user.id].config['id_last_messages'] = massage_info.message_id
    elif message.text == '📗 Руководство':
        bot.send_message(message.from_user.id, info)

    # elif message.text == '/lowprice':
    #     """После ввода команды у пользователя запрашивается:
    #     1. Город, где будет проводиться поиск.
    #     2. Количество отелей, которые необходимо вывести в результате (не больше
    #     заранее определённого максимума).
    #     """
    #     print('Тут бизнес логика lowprice')
    # elif message.text == '/highprice':
    #     """После ввода команды у пользователя запрашивается:
    #     1. Город, где будет проводиться поиск.
    #     2. Количество отелей, которые необходимо вывести в результате (не больше
    #     заранее определённого максимума).
    #     """
    #     print('Тут бизнес логика highprice')
    # elif message.text == '/bestdeal':
    #     """
    #     После ввода команды у пользователя запрашивается:
    #     1. Город, где будет проводиться поиск.
    #     2. Диапазон цен.
    #     3. Диапазон расстояния, на котором находится отель от центра.
    #     4. Количество отелей, которые необходимо вывести в результате (не больше
    #     заранее определённого максимума).
    #     """
    #     print('Тут бизнес логика bestdeal')
    elif user_bd[message.from_user.id].config['bool_city'] and not user_bd[message.from_user.id].config[
        'check_choice_city'] and not user_bd[message.from_user.id].config['count_hotels']:
        # user_bd[message.from_user.id].config['bool_city'] = False
        user_bd[message.from_user.id].config['check_choice_city'] = True
        SearchHotel.search_city_data(bot, message)

    elif user_bd[message.from_user.id].config['check_choice_city'] \
            and user_bd[message.from_user.id].config['bool_city'] \
            and not user_bd[message.from_user.id].config['count_hotels']:
        user_bd[message.from_user.id].config['count_hotels'] = int(message.text)
        print("кол-во отелей", user_bd[message.from_user.id].config['count_hotels'])
        SearchHotel.search_hotels(bot, message)

    # elif user_bd[message.from_user.id].config['check_choice_city'] \
    #         and user_bd[message.from_user.id].config['bool_city'] \
    #         and user_bd[message.from_user.id].config['count_hotels']:




@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == '/lowprice':
        print('/lowprice salam')
        user_bd[c.message.chat.id].config['search_price_filter'] = 'lowprice'
        bot.send_message(user_bd[c.message.chat.id].id_user, "В каком городе будем искать ?")
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], user_bd[c.message.chat.id].id_user,
                                 user_bd[c.message.chat.id].config['id_last_messages'])
        user_bd[c.message.chat.id].config['bool_city'] = True
    elif user_bd[c.message.chat.id].config['check_choice_city'] and user_bd[c.message.chat.id].config['bool_city']:
        bot.send_message(user_bd[c.message.chat.id].id_user, "Какое кол-во отелей вывести? (Макс. 10)")
        user_bd[c.message.chat.id].id_city = user_bd[c.message.chat.id].data['suggestions'][0]['entities'][int(c.data)][
            'destinationId']

        patterns_span = re.compile(r'<.*?>')

        user_bd[c.message.chat.id].config['check_choice_city'] = True


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as ex:
            # TODO Доработаь Обработка ошибок
            pass
