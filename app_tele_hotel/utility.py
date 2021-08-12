import json
import re
import threading

from telebot import TeleBot, types, apihelper
from dotenv import dotenv_values
import requests

config = dotenv_values(".env")

RAPID_API_TOKEN = TeleBot(config['RAPID_API_TOKEN'])
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
    def SearchCityData(cls, bot, message):
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": message.text, "locale": check_language(message.text)}
        message_info = bot.send_message(message.from_user.id, 'Идет поиск отеля')
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

        patterns_span = re.compile(r'<.*?>')
        count = 0
        markup = types.InlineKeyboardMarkup()
        for entities_city in user_bd[message.from_user.id].data['suggestions'][0]['entities']:
            add = types.InlineKeyboardButton(text=patterns_span.sub('', entities_city['caption']),
                                             callback_data=str(count))
            markup.add(add)
            count += 1
            print(patterns_span.sub('', entities_city['caption']))
        user_bd[message.from_user.id].bool_city = True
        bot.send_message(message.from_user.id, "🌍 Уточните город", reply_markup=markup)
