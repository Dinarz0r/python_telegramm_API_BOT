import json
import re
import threading
import time

from telebot import TeleBot, types, apihelper
from dotenv import dotenv_values
import requests
from datetime import date, timedelta
from app_tele_hotel.users import Users

config = dotenv_values(".env")

user_bd = dict()


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
        bot.edit_message_text(f"{text}{point}", chat_id=chat_id,
                              message_id=message_id)
        count_point += 1


class SearchHotel:
    headers = {
        'x-rapidapi-key': config['RAPID_API_TOKEN'],
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    @classmethod
    def search_city_data(cls, bot, message):
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": message.text, "locale": check_language(message.text)}
        message_info = bot.send_message(message.from_user.id, 'Идет поиск иформации по городу')
        pill2kill = threading.Event()
        wait_effect = threading.Thread(target=mess_wait,
                                       args=(pill2kill, message_info.chat.id, message_info.id, message_info.text, bot))
        wait_effect.start()
        response = requests.get(url, headers=cls.headers, params=querystring)
        pill2kill.set()
        wait_effect.join()
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], message_info.chat.id,
                                 message_info.id)
        user_bd[message.from_user.id].data = json.loads(response.text)
        print(user_bd[message.from_user.id].data)
        patterns_span = re.compile(r'<.*?>')
        count = 0
        markup = types.InlineKeyboardMarkup()
        for entities_city in user_bd[message.from_user.id].data['suggestions'][0]['entities']:
            add = types.InlineKeyboardButton(text=patterns_span.sub('', entities_city['caption']),
                                             callback_data=str(count))
            markup.add(add)
            count += 1
        bot.send_message(message.from_user.id, "🌍 Уточните город", reply_markup=markup)

    @classmethod
    def search_hotels(cls, bot, message, price_filter, distance=False, photo_hotel=False):
        if price_filter is None:
            price_filter = 'PRICE'
        url = "https://hotels4.p.rapidapi.com/properties/list"
        url_get_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {
            "destinationId": user_bd[message.from_user.id].id_city,
            "pageNumber": "1",
            "pageSize": user_bd[message.from_user.id].config['count_hotels'],
            "checkIn": date.today(),
            "checkOut": date.today() + timedelta(days=1),
            "adults1": "1",
            "sortOrder": price_filter,
            "locale": "ru_RU",
            "currency": "RUB"
        }
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
        user_bd[message.from_user.id].hotels_data = json.loads(response.text)

        for i in user_bd[message.from_user.id].hotels_data['data']['body']['searchResults']['results']:
            i_text = f'Имя: {i["name"]}\n' \
                     f'Адрес: {i["address"]["countryName"]}, {i["address"]["locality"]}, ' \
                     f'{i["address"]["streetAddress"]}\n' \
                     f'От центра города: {i["landmarks"][0]["distance"]}\nЦена {i["ratePlan"]["price"]["current"]}'
            if user_bd[message.from_user.id].config['flag_search_photo']:
                photo_list = list()
                response = requests.get(url_get_photo, headers=cls.headers, params={"id": i['id']})
                time.sleep(2)
                data = json.loads(response.text)
                if data:
                    if len(data['hotelImages']) >= user_bd[message.from_user.id].config['photo_hotel_count']:
                        for index in range(user_bd[message.from_user.id].config['photo_hotel_count']):
                            if not photo_list:
                                photo_list.append(
                                    types.InputMediaPhoto(data['hotelImages'][index]['baseUrl'].format(size='l'),
                                                          caption=i_text))
                            else:
                                photo_list.append(
                                    types.InputMediaPhoto(data['hotelImages'][index]['baseUrl'].format(size='l')))

                    else:
                        for index in range(len(data['hotelImages'])):
                            if photo_list:
                                photo_list.append(
                                    types.InputMediaPhoto(data['hotelImages'][index]['baseUrl'].format(size='l')))
                            else:
                                photo_list.append(
                                    types.InputMediaPhoto(data['hotelImages'][index]['baseUrl'].format(size='l'),
                                                          caption=i_text))
                    bot.send_media_group(message.from_user.id, photo_list)
                    photo_list.clear()
                else:
                    bot.send_message(message.from_user.id, i_text)
            else:
                bot.send_message(message.from_user.id, i_text)
        user_bd[message.from_user.id].config = {'count_hotels': 0, 'search_price_filter': None, 'bool_city': False,
                                                'check_choice_city': False, 'id_last_messages': None, 'messages': None,
                                                'check_photo_hotel': False, 'photo_hotel_count': 0,
                                                'flag_search_photo': False,
                                                'start_search': False}
