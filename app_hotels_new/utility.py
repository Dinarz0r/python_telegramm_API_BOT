import json
import re
import threading
from datetime import date, timedelta
import requests
from telebot import TeleBot, apihelper, types
from dotenv import dotenv_values

user_bd = dict()
config = dotenv_values(".env")
bot = TeleBot(config['TELEGRAM_API_TOKEN'])


def check_method(message: types.Message, text_error):
    if message.text in ['/help', '/lowprice', '/highprice', '/bestdeal', '/history', '/start', '🏨Найти отель',
                        '📗 Руководство']:
        return True, bot.send_message(message.chat.id, text_error)


def check_language(text: str) -> str:
    """
    Ф-ция определения английского языка иначе русский, для формы отправки GET Запросов
    :param text: принимаемый текст входящего текста города
    :return: 'en_US' или 'ru_RU'
    """
    if re.findall(r'[a-zA-Z -]', text):
        return "en_US"
    else:
        return "ru_RU"


def mess_wait(stop_event, chat_id: int, message_id: int, text: str, bot) -> None:
    """
    Функция создающая эффект анимированного поиска при ожидании ответа от request.GET()
    работающая в асинхронном режиме.
    """
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
        bot.edit_message_text(f"{text}{point}", chat_id=chat_id, message_id=message_id, parse_mode="Markdown")
        count_point += 1


class SearchHotel:
    """
    Класс направленный на парсинг информации получаемой от request.
    """
    headers = {
        'x-rapidapi-key': config['RAPID_API_TOKEN3'],
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    @classmethod
    def search_city_data(cls, bot, message):
        """
        Функция направленная на отправку get запроса на сервер с целью получения информации
        по уточнению искомого города с записью в объект User кеша полученного ответа, и отправки
        уточняющего характера список кликабельных городов.

        :param bot: объект телеграмм бота
        :param message: объект входящего сообщения от пользователя
        """
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": message.text, "locale": user_bd[message.chat.id].language}
        message_info = bot.send_message(message.from_user.id, 'Идет поиск информации по городу')
        pill2kill = threading.Event()
        wait_effect = threading.Thread(target=mess_wait,
                                       args=(pill2kill, message_info.chat.id, message_info.id, message_info.text, bot))
        wait_effect.start()
        response = requests.get(url, headers=cls.headers, params=querystring, timeout=10)
        if response.status_code != 200:
            bot.send_message(message.from_user.id, 'Технические работы 15 мин. Попробуйте позднее')
        pill2kill.set()
        wait_effect.join()
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], message_info.chat.id, message_info.id)
        user_bd[message.from_user.id].cache_data = json.loads(response.text)
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
            bot.send_message(message.from_user.id, 'Информация по указанному городу отсутствует⛔️')

    @classmethod
    def search_hotels(cls, bot, message):
        """
        Функция поиска отелей по выбранным параметрам метода поиска

        :param bot: объект телеграмм бота
        :param message: объект входящего сообщения от пользователя
        """
        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {
            "destinationId": user_bd[message.from_user.id].id_city,
            "pageNumber": "1",
            "pageSize": f"{user_bd[message.from_user.id].count_show_hotels}",
            "checkIn": date.today() + timedelta(days=1),
            "checkOut": date.today() + timedelta(days=2),
            "adults1": "1",
            "sortOrder": user_bd[message.from_user.id].search_method,
            "locale": user_bd[message.chat.id].language,
            "currency": "RUB",
            "landmarkIds": "city center"
        }

        if user_bd[message.from_user.id].search_method == 'best_deal':
            querystring.update({"pageSize": "25",
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

    @classmethod
    def show_hotels(cls, message):
        """
        Ф-ция подготовки спарсенной информации для последующей подготовки вывода найденных отелей
        по критериям выбранным пользователем
        :param message: объект входящего сообщения от пользователя
        """
        url_get_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        best_deal_view = 0
        for i in user_bd[message.from_user.id].cache_data['data']['body']['searchResults']['results']:
            if user_bd[message.from_user.id].distance_min_max \
                    and user_bd[message.from_user.id].search_method == 'best_deal':
                min_dist = user_bd[message.from_user.id].distance_min_max.get('min')
                max_dist = user_bd[message.from_user.id].distance_min_max.get('max')
                dist_center = int(re.findall(r'\d+', i["landmarks"][0]["distance"])[0])
                if not min_dist <= dist_center <= max_dist:
                    continue
                else:
                    best_deal_view += 1
                    if best_deal_view > user_bd[message.from_user.id].count_show_hotels:
                        break
            i_text = f'*Имя: {i["name"]}*\n' \
                     f'Адрес: {i["address"]["countryName"]}, {i["address"]["locality"]}, ' \
                     f'{i["address"]["streetAddress"]}\n' \
                     f'От центра города: {i["landmarks"][0]["distance"]}\nЦена {i["ratePlan"]["price"]["current"]}'
            if not user_bd[message.from_user.id].photo:
                bot.send_message(message.from_user.id, i_text, parse_mode="Markdown")
            else:
                message_info = bot.send_message(message.from_user.id, f'Идет поиск фото отеля *{i["name"]}*',
                                                parse_mode="Markdown")
                pill2kill = threading.Event()
                wait_effect = threading.Thread(target=mess_wait,
                                               args=(
                                                   pill2kill, message_info.chat.id, message_info.id, message_info.text,
                                                   bot))
                wait_effect.start()
                response = requests.get(url_get_photo, headers=cls.headers, params={"id": i["id"]})
                data = json.loads(response.text)
                if data:
                    photo_list = [
                        types.InputMediaPhoto(data['hotelImages'][0]['baseUrl'].format(size='l'), caption=i_text,
                                              parse_mode="Markdown")
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
                    bot.send_message(message.from_user.id, i_text, parse_mode="Markdown")

        bot.send_message(message.from_user.id,
                         'Поиск завершен✅')
        user_bd[message.from_user.id].save_history()
        user_bd[message.from_user.id].clear_cache()


def next_step_city(mess):
    """
    Ф-ция проверки на корректность ввода названия города.
    :param mess: объект входящего сообщения от пользователя
    """
    if check_method(mess, 'Увы вы выбрали город с названием метода, так нельзя. Давай попробуем сначала'):
        pass
    elif len(re.findall(r'[А-Яа-яЁёa-zA-Z0-9 -]+', mess.text)) > 1:
        err_city = bot.send_message(mess.chat.id,
                                    'Город должен содержать только буквы, вводи еще раз город.')
        bot.register_next_step_handler(err_city, next_step_city)
    else:
        user_bd[mess.chat.id].language = check_language(mess.text)
        user_bd[mess.chat.id].search_city = mess.text
        SearchHotel.search_city_data(bot, mess)


def next_step_count_hotels(mess):
    """
    Ф-ция проверки на корректность ввода кол-ва искомых отелей в городе.
    В случае положительного ответа, вызываем ф-цию range_request_price.
    :param mess: объект входящего сообщения от пользователя
    """
    if check_method(mess, 'Увы вы выбрали кол-во с названием метода, так нельзя. Давай попробуем сначала'):
        pass
    elif not isinstance(mess.text, str) or not mess.text.isdigit():
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
    """
    Ф-ция проверки на корректность ввода диапазона поиска от центра.
    :param mess: объект входящего сообщения от пользователя
    """

    price_min_max_list = list(map(int, re.findall(r'\d+', mess.text)))
    if check_method(mess, 'Увы вы ввели диапазон с названием метода, так нельзя. Давай попробуем сначала'):
        pass
    elif not isinstance(mess.text, str) or len(price_min_max_list) != 2:
        err_num = bot.send_message(mess.chat.id,
                                   'Должно быть 2 числа! Введи еще раз!')
        bot.register_next_step_handler(err_num, range_request_price)
    else:
        user_bd[mess.chat.id].price_min_max['min'] = min(price_min_max_list)
        user_bd[mess.chat.id].price_min_max['max'] = max(price_min_max_list)
        msg_dist = bot.send_message(mess.chat.id,
                                    f'Укажите диапазон расстояния от центра в {"км." if user_bd[mess.chat.id].language == "ru_RU" else "милях"} Пример (1-5)')
        bot.register_next_step_handler(msg_dist, search_distance)


def search_distance(mess):
    """
    Ф-ция проверки на корректность ввода кол-ва искомых отелей в городе.
    :param mess: объект входящего сообщения от пользователя
    """
    distance_list = list(map(int, re.findall(r'\d+', mess.text)))
    if check_method(mess, 'Увы вы ввели диапазон с названием метода, так нельзя. Давай попробуем сначала'):
        pass
    elif not isinstance(mess.text, str) or len(distance_list) != 2:
        err_num = bot.send_message(mess.chat.id,
                                   'Должно быть 2 числа! Введи еще раз!')
        bot.register_next_step_handler(err_num, search_distance)
    else:
        user_bd[mess.chat.id].distance_min_max['min'] = min(distance_list)
        user_bd[mess.chat.id].distance_min_max['max'] = max(distance_list)
        SearchHotel.search_hotels(bot, mess)
        request_photo(mess)


def request_photo(mess):
    """
    Ф-ция отправляющая кнопки с вопросом будем ли искать фото?
    :param mess: объект входящего сообщения от пользователя
    """

    markup = types.InlineKeyboardMarkup()
    yes_photo_hotels = types.InlineKeyboardButton(text='✅Да', callback_data='yes_photo')
    no_photo_hotels = types.InlineKeyboardButton(text='❌Нет', callback_data='no_photo')
    markup.add(yes_photo_hotels, no_photo_hotels)
    bot.send_message(mess.chat.id, "Показать фотографии отелей?", reply_markup=markup)


def next_step_count_photo(mess):
    """
    Ф-ция проверки на корректность ввода пользователем кол-ва отображаемых изображений с отелями.
    :param mess: объект входящего сообщения от пользователя

    """
    if check_method(mess, 'Увы вы ввели кол-фо фото с названием метода, так нельзя. Давай попробуем сначала'):
        pass
    elif not isinstance(mess.text, str) or not mess.text.isdigit():
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
