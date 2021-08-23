import json
import re
import threading
import time
from datetime import date, timedelta
import requests
from telebot import TeleBot, apihelper, types
from dotenv import dotenv_values

from users_new import Users

user_bd = dict()
config = dotenv_values(".env")
bot = TeleBot(config['TELEGRAM_API_TOKEN'])


def check_language(text):
    if re.findall(r'[a-zA-Z]', text):
        return 'en_US'
    else:
        return 'ru_RU'


def mess_wait(stop_event, chat_id, message_id, text, bot):
    count_point = 0
    while not stop_event.wait(0.2):
        if count_point == 0:
            point = '/'
        elif count_point == 1:
            point = '-'
        elif count_point == 2:
            point = '\\'
        else:
            point = '|'
            count_point = -1
        bot.edit_message_text(f"{text}{point}", chat_id=chat_id, message_id=message_id)
        count_point += 1


class SearchHotel:
    headers = {
        'x-rapidapi-key': config['RAPID_API_TOKEN3'],
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    @classmethod
    def search_city_data(cls, bot, message):
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": message.text, "locale": check_language(message.text)}
        message_info = bot.send_message(message.from_user.id, 'Идет поиск информации по городу')
        pill2kill = threading.Event()
        wait_effect = threading.Thread(target=mess_wait,
                                       args=(pill2kill, message_info.chat.id, message_info.id, message_info.text, bot))
        wait_effect.start()
        response = requests.get(url, headers=cls.headers, params=querystring)
        pill2kill.set()
        wait_effect.join()
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], message_info.chat.id, message_info.id)
        user_bd[message.from_user.id].cache_data = json.loads(response.text)
        print('ТЕСТ ДАТА', user_bd[message.from_user.id].cache_data)
        patterns_span = re.compile(r'<.*?>')
        if user_bd[message.from_user.id].cache_data['suggestions'][0]['entities']:
            markup = types.InlineKeyboardMarkup()
            count = 0
            for entities_city in user_bd[message.from_user.id].cache_data['suggestions'][0]['entities']:
                add = types.InlineKeyboardButton(text=patterns_span.sub('', entities_city['caption']),
                                                 callback_data=f'choice_city_{count}', )
                markup.add(add)
                count += 1
            bot.send_message(message.from_user.id, "🌍 Уточните город", reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, 'Информация по указанному городу отсутствует')

    @classmethod
    def search_hotels(cls, bot, message):
        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {
            "destinationId": user_bd[message.from_user.id].id_city,
            "pageNumber": "1",
            "pageSize": user_bd[message.from_user.id].count_show_hotels,
            "checkIn": date.today(),
            "checkOut": date.today() + timedelta(days=1),
            "adults1": "1",
            "sortOrder": user_bd[message.from_user.id].search_method,
            "locale": "ru_RU",
            "currency": "RUB"
        }
        if user_bd[message.from_user.id].search_method == 'best_deal':
            querystring.update({"pageSize": 25,
                                "priceMin": user_bd[message.from_user.id].price_min_max['min'],
                                "priceMax": user_bd[message.from_user.id].price_min_max['max'],
                                "sortOrder": "PRICE",
                                "landmarkIds": "city center"})

        message_info = bot.send_message(message.from_user.id, 'Идет поиск отелей')
        pill2kill = threading.Event()
        wait_effect = threading.Thread(target=mess_wait,
                                       args=(pill2kill, message_info.chat.id, message_info.id, message_info.text, bot))
        wait_effect.start()
        response = requests.get(url, headers=cls.headers, params=querystring)
        pill2kill.set()
        wait_effect.join()
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], message_info.chat.id,
                                 message_info.id)
        user_bd[message.from_user.id].cache_data = json.loads(response.text)
        print("Кэш с отелями", user_bd[message.from_user.id].cache_data)

    @classmethod
    def show_hotels(cls, message):
        url_get_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        best_deal_view = 0
        for i in user_bd[message.from_user.id].cache_data['data']['body']['searchResults']['results']:
            if user_bd[message.from_user.id].distance_min_max \
                    and user_bd[message.from_user.id].search_method == 'best_deal':
                min_dist = user_bd[message.from_user.id].distance_min_max.get('min')
                max_dist = user_bd[message.from_user.id].distance_min_max.get('max')
                test_dist = i["landmarks"][0]["distance"]
                print(test_dist)
                dist_center = int(re.findall(r'\d+', i["landmarks"][0]["distance"])[0])
                print(dist_center)
                if not min_dist <= dist_center <= max_dist:
                    continue
                else:
                    best_deal_view += 1
                    if best_deal_view > user_bd[message.from_user.id].count_show_hotels:
                        break
            i_text = f'Имя: {i["name"]}\n' \
                     f'Адрес: {i["address"]["countryName"]}, {i["address"]["locality"]}, ' \
                     f'{i["address"]["streetAddress"]}\n' \
                     f'От центра города: {i["landmarks"][0]["distance"]}\nЦена {i["ratePlan"]["price"]["current"]}'
            if not user_bd[message.from_user.id].photo:
                bot.send_message(message.from_user.id, i_text)
            else:
                message_info = bot.send_message(message.from_user.id, f'Идет поиск фото отеля {i["name"]}')
                pill2kill = threading.Event()
                wait_effect = threading.Thread(target=mess_wait,
                                               args=(
                                                   pill2kill, message_info.chat.id, message_info.id, message_info.text,
                                                   bot))
                wait_effect.start()
                response = requests.get(url_get_photo, headers=cls.headers, params={"id": i['id']})
                time.sleep(2)

                data = json.loads(response.text)
                if data:
                    photo_list = [
                        types.InputMediaPhoto(data['hotelImages'][0]['baseUrl'].format(size='l'), caption=i_text)
                    ]
                    if len(data['hotelImages']) < user_bd[message.from_user.id].count_show_photo:
                        count_photo = len(data['hotelImages'])
                    else:
                        count_photo = user_bd[message.from_user.id].count_show_photo
                    if count_photo > 1:
                        for index in range(1, count_photo):
                            photo_list.append(
                                types.InputMediaPhoto(data['hotelImages'][index]['baseUrl'].format(size='l')))
                    bot.send_media_group(message.from_user.id, photo_list)
                    pill2kill.set()
                    wait_effect.join()
                    apihelper.delete_message(config['TELEGRAM_API_TOKEN'], message_info.chat.id,
                                             message_info.id)
                    photo_list.clear()
                else:
                    bot.send_message(message.from_user.id, i_text)
        user_bd[message.from_user.id] = Users(message)


def next_step_city(mess):
    print(mess.chat.id, mess.text)
    if len(re.findall(r'[А-Яа-яЁёa-zA-Z0-9 -]+', mess.text)) > 1:
        err_city = bot.send_message(mess.chat.id,
                                    'Город должен содержать только буквы, вводи еще раз город.')
        bot.register_next_step_handler(err_city, next_step_city)
    else:
        user_bd[mess.chat.id].search_city = mess.text
        SearchHotel.search_city_data(bot, mess)
        print(user_bd[mess.chat.id].search_city)


def next_step_count_hotels(mess):
    if not mess.text.isdigit():
        err_num = bot.send_message(mess.chat.id,
                                   'Количество должно состоять из цифр! вводи еще раз количество')
        bot.register_next_step_handler(err_num, next_step_count_hotels)
    else:
        if int(mess.text) > 25:
            user_bd[mess.chat.id].count_show_hotels = 25
            bot.send_message(mess.chat.id, 'Увы я засчитал это за 25')

        else:
            user_bd[mess.chat.id].count_show_hotels = int(mess.text)

        if user_bd[mess.chat.id].search_method != 'best_deal':
            SearchHotel.search_hotels(bot, mess)
            request_photo(mess)
        else:
            msg_price = bot.send_message(mess.chat.id,
                                         'Укажите диапазон цен отеля за сутки. Пример (1000-4000)')
            bot.register_next_step_handler(msg_price, range_request_price)


def range_request_price(mess):
    price_min_max_list = list(map(int, re.findall(r'\d+', mess.text)))
    if len(price_min_max_list) == 2:
        user_bd[mess.chat.id].price_min_max['min'] = min(price_min_max_list)
        user_bd[mess.chat.id].price_min_max['max'] = max(price_min_max_list)
        msg_dist = bot.send_message(mess.chat.id,
                                    'Укажите диапазон расстояния от центра в км. Пример (1-5)')
        bot.register_next_step_handler(msg_dist, search_distance)
    else:
        err_num = bot.send_message(mess.chat.id,
                                   'Должно быть 2 числа! Введи еще раз!')
        bot.register_next_step_handler(err_num, range_request_price)
    print('price max', user_bd[mess.chat.id].price_min_max['max'])
    print('price min', user_bd[mess.chat.id].price_min_max['min'])


def search_distance(mess):
    distance_list = list(map(int, re.findall(r'\d+', mess.text)))
    if len(distance_list) == 2:
        print(distance_list)
        print(min(distance_list))
        print(max(distance_list))
        user_bd[mess.chat.id].distance_min_max['min'] = min(distance_list)
        user_bd[mess.chat.id].distance_min_max['max'] = max(distance_list)
        SearchHotel.search_hotels(bot, mess)
        request_photo(mess)
    else:
        err_num = bot.send_message(mess.chat.id,
                                   'Должно быть 2 числа! Введи еще раз!')
        bot.register_next_step_handler(err_num, search_distance)
    print('dist max', user_bd[mess.chat.id].distance_min_max['max'])
    print('dist min', user_bd[mess.chat.id].distance_min_max['min'])


def request_photo(mess):
    markup = types.InlineKeyboardMarkup()
    yes_photo_hotels = types.InlineKeyboardButton(text='✅Да', callback_data='yes_photo')
    no_photo_hotels = types.InlineKeyboardButton(text='❌Нет', callback_data='no_photo')
    markup.add(yes_photo_hotels, no_photo_hotels)
    bot.send_message(mess.chat.id, "Показать фотографии отелей?", reply_markup=markup)


def next_step_count_photo(mess):
    if not mess.text.isdigit():
        err_num = bot.send_message(mess.chat.id,
                                   'Количество должно состоять из цифр! вводи еще раз количество')
        bot.register_next_step_handler(err_num, next_step_count_photo)
    else:
        if int(mess.text) > 4:
            user_bd[mess.chat.id].count_show_photo = 4
            bot.send_message(mess.chat.id, 'Увы я засчитал это за 4')

        else:
            user_bd[mess.chat.id].count_show_photo = int(mess.text)
        SearchHotel.show_hotels(mess)
