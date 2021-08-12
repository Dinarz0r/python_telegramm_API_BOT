import json
import re
import threading
import time
from users import Users

from utility import mess_wait
from telebot import TeleBot, types, apihelper
import requests

bot = TeleBot('1921101611:AAHACgqfBNMQJGpFIGk2NDrBmZhpNQzYf90')
headers = {
    'x-rapidapi-key': "4d9d661215mshca27e4738c71a90p129c4ajsn858bb7dd9791",
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
}
info = '● /help — помощь по командам бота\n' \
       '● /lowprice — вывод самых дешёвых отелей в городе\n' \
       '● /highprice — вывод самых дорогих отелей в городе\n' \
       '● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n'
user_info_dict = {'check_choice_city': False, 'city': False}
json_data = dict()
user_bd = dict()





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
        bot.send_message(message.from_user.id, "В каком городе будем искать отель?")
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

    elif user_bd[message.from_user.id].check_choice_city:

        user_bd[message.from_user.id].check_choice_city = False
        message_info = bot.send_message(message.from_user.id, 'Идет поиск отеля')
        pill2kill = threading.Event()
        proc = threading.Thread(target=mess_wait,
                                args=(pill2kill, message_info.chat.id, message_info.id, message_info.text))
        proc.start()

        markup = types.InlineKeyboardMarkup()
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": message.text, "locale": "ru_RU"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        pill2kill.set()
        proc.join()
        apihelper.delete_message('1921101611:AAHACgqfBNMQJGpFIGk2NDrBmZhpNQzYf90', message_info.chat.id,
                                 message_info.id)
        user_bd[message.from_user.id].data = json.loads(response.text)
        count = 0
        for entities_city in user_bd[message.from_user.id].data['suggestions'][0]['entities']:
            patterns_span = re.compile(r'<.*?>')
            add = types.InlineKeyboardButton(text=patterns_span.sub('', entities_city['caption']),
                                             callback_data=str(count))
            markup.add(add)
            count += 1
            print(patterns_span.sub('', entities_city['caption']))
        user_bd[message.from_user.id].bool_city = True

        bot.send_message(message.from_user.id, "🌍 Уточните город", reply_markup=markup)

    elif message.text == '/lowprice':
        """После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print(message.text)
    elif message.text == '/highprice':
        """После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print('Тут бизнес логика highprice')

        url = "https://hotels4.p.rapidapi.com/locations/search"

        querystring = {"query": "Москва", "locale": "ru_RU"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        print(response.text)

    elif message.text == '/bestdeal':
        """
        После ввода команды у пользователя запрашивается:
        1. Город, где будет проводиться поиск.
        2. Диапазон цен.
        3. Диапазон расстояния, на котором находится отель от центра.
        4. Количество отелей, которые необходимо вывести в результате (не больше
        заранее определённого максимума).
        """
        print('Тут бизнес логика bestdeal')


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if user_bd[c.message.chat.id].bool_city:
        user_bd[c.message.chat.id].bool_city = False
        user_bd[c.message.chat.id].id_city = user_bd[c.message.chat.id].data['suggestions'][0]['entities'][int(c.data)][
            'destinationId']
        print(user_bd[c.message.chat.id].id_user)
        print(user_bd[c.message.chat.id].id_city)
        print('id города', user_bd[c.message.chat.id].id_city)
        req_get_hotels = requests.get()
        apihelper.delete_message('1921101611:AAHACgqfBNMQJGpFIGk2NDrBmZhpNQzYf90', c.message.chat.id,
                                 c.message.message_id)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as ex:
            # TODO Доработаь Обработка ошибок
            pass
