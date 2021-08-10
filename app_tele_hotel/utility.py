from telebot import TeleBot


bot = TeleBot('1921101611:AAHACgqfBNMQJGpFIGk2NDrBmZhpNQzYf90')


def mess_wait(stop_event, chat_id, message_id, text):
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
