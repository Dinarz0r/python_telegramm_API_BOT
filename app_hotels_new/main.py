import re

from users import Users
from utility import next_step_city, config, next_step_count_hotels, next_step_count_photo, SearchHotel
from telebot import types, apihelper
from utility import bot, user_bd

info = '● /help — помощь по командам бота\n' \
       '● /lowprice — вывод самых дешёвых отелей в городе\n' \
       '● /highprice — вывод самых дорогих отелей в городе\n' \
       '● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n' \
       '● /history - вывод истории поиска отелей'


@bot.message_handler(commands=['start', 'help', 'lowprice', 'highprice', 'bestdeal', 'history'])
def handle_start_help(message):
    """
    Функция обработки входящих сообщений от пользователя следующих
    команд: /start, /help, /lowprice, /highprice, /bestdeal, /history

    :param message: объект входящего сообщения от пользователя
    :type: message: types.Message
    """
    if not user_bd.get(message.from_user.id):
        user_bd[message.from_user.id] = Users(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=False)
    btn_a = types.KeyboardButton('🏨Найти отель')
    btn_b = types.KeyboardButton('📗 Руководство')
    # btn_c = types.KeyboardButton('🚧 О сервисе')
    markup.row(btn_a, btn_b)
    # markup.row(btn_c)
    if message.text == '/start':
        start_help_text = f"Привет {user_bd[message.from_user.id].username}, я БОТ Too Easy Travel✅,\n" \
                          "И я смогу подобрать для тебя отель 🏨"
        bot.send_message(message.from_user.id, start_help_text, reply_markup=markup)
    elif message.text == '/help':
        bot.send_message(message.from_user.id, info, reply_markup=markup)
    elif message.text in ['/lowprice', '/highprice']:
        user_bd[message.from_user.id].search_method = (
            'PRICE' if message.text == '/lowprice' else 'PRICE_HIGHEST_FIRST')
        msg = bot.send_message(message.from_user.id, 'В каком городе будем искать?')
        bot.register_next_step_handler(msg, next_step_city)
    elif message.text == '/bestdeal':
        user_bd[message.from_user.id].search_method = 'best_deal'
        print('метоД', user_bd[message.from_user.id].search_method)
        msg = bot.send_message(message.from_user.id, 'В каком городе будем искать?')
        bot.register_next_step_handler(msg, next_step_city)
    elif message.text == '/history':
        bot.send_message(message.from_user.id, user_bd[message.from_user.id].history, parse_mode="Markdown")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """
    Функция обработчик входящих сообщений:
    1. '🏨Найти отель' - выдаст пользователю в окне мессенджера варианты поиска отелей.
    2. '📗 Руководство' - краткое руководство пользователя.

    :param message: объект входящего сообщения от пользователя
    :type: message: types.Message
    """
    if not user_bd.get(message.from_user.id):
        user_bd[message.from_user.id] = Users(message)
    if message.text == '🏨Найти отель':
        user_bd[message.from_user.id].clear_cache()
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text='Самый дешёвый в городе', callback_data='low_price'),
            types.InlineKeyboardButton(text='Самый дорогой в городе', callback_data='high_price'),
            types.InlineKeyboardButton(text='фильтр по цене и расположению от центра', callback_data='best_deal'),
            row_width=True)
        massage_info = bot.send_message(message.from_user.id, "🔎 выберете способ поиска", reply_markup=markup)

        user_bd[message.from_user.id].config['id_last_messages'] = massage_info.message_id
    elif message.text == '📗 Руководство':
        bot.send_message(message.from_user.id, info)


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    """
    Функция обработчик возвращаемого значения при клике "кнопки" пользователем в окне мессенджера.

    :param c: response объекта от пользователя при клике на кнопки.
    :return:
    """
    if c.data in ['low_price', 'high_price']:
        bot.delete_message(c.message.chat.id, message_id=c.message.id)
        user_bd[c.message.chat.id].search_method = ('PRICE' if c.data == 'low_price' else 'PRICE_HIGHEST_FIRST')
        print('метоД', user_bd[c.message.chat.id].search_method)
        msg = bot.send_message(c.message.chat.id, 'В каком городе будем искать?')
        bot.register_next_step_handler(msg, next_step_city)
    elif c.data == 'best_deal':
        bot.delete_message(c.message.chat.id, message_id=c.message.id)
        user_bd[c.message.chat.id].search_method = 'best_deal'
        print('метоД', user_bd[c.message.chat.id].search_method)
        msg = bot.send_message(c.message.chat.id, 'В каком городе будем искать?')
        bot.register_next_step_handler(msg, next_step_city)
    elif c.data.startswith('choice_city_'):
        choice_city = int(re.sub(r'choice_city_', '', c.data))
        user_bd[c.message.chat.id].id_city = \
            user_bd[c.message.chat.id].cache_data['suggestions'][0]['entities'][choice_city][
                'destinationId']
        apihelper.delete_message(config['TELEGRAM_API_TOKEN'], c.message.chat.id, c.message.message_id)
        print('выбранный id города', user_bd[c.message.chat.id].id_city)

        msg2 = bot.send_message(c.message.chat.id,
                                'Количество отелей, которые необходимо вывести в результате? (макс. 25)')
        bot.register_next_step_handler(msg2, next_step_count_hotels)
    elif c.data in ['yes_photo', 'no_photo']:
        bot.delete_message(c.message.chat.id, message_id=c.message.id)
        user_bd[c.message.chat.id].photo = (True if c.data == 'yes_photo' else False)
        print(user_bd[c.message.chat.id].photo)
        if user_bd[c.message.chat.id].photo:
            msg2 = bot.send_message(c.message.chat.id,
                                    'Количество фотографий, которые необходимо вывести в результате? (макс. 4)')
            bot.register_next_step_handler(msg2, next_step_count_photo)
        else:
            SearchHotel.show_hotels(c)

        print('ФЛАГ ФОТО', user_bd[c.message.chat.id].photo)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as ex:
            pass
