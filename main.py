import telebot
import os
import re
from telebot import types
from db import Database
from dotenv import load_dotenv


load_dotenv('TOKEN.env') # Загрузка файла с чувствительными данными

TOKEN = os.getenv('TOKEN')
ABOUT_BOT = 'Этот бот даёт возможность создать напоминание' \
            ' для любого дня недели в заданное вами время'
DATA = 'Database\\users.db'
DAYS = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье', 'Каждый день')
ROW_WIDTH = 1 # Количество кнопок в строке
MAX_NOTIFICATIONS = 15 # Максимальное количество оповещений
MAX_OF_SIZE_NOTIFICATION = 150 # Максимальное количество символов в оповещении

bot = telebot.TeleBot(TOKEN)


# МЕНЮ
@bot.message_handler(commands=['start'])
def send_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=ROW_WIDTH)

    # Кнопки на экране
    information_button = types.KeyboardButton('/settings')
    help_button = types.KeyboardButton('/help')
    buttons = (help_button,  information_button)
    [keyboard.add(i) for i in buttons]

    text_main_menu = f'Привет {message.from_user.first_name}, здесь находится меню бота\n \n' \
                      '/settings  --  Настройка уведомлений\n' \
                      '/help  --  Информация о боте'

    bot.send_message(message.chat.id, text_main_menu, reply_markup=keyboard)


# НАСТРОЙКИ
@bot.message_handler(commands=['settings'])
def send_settings(message):
    DB = Database(DATA)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=ROW_WIDTH)

    has_all_commands = False
    have_notification = bool(DB.get_quantity_notifiactions(message.chat.id))

    #Проверка юзера на соответствие к базе данных
    if DB.user_exists(message.chat.id) and have_notification: # Пользователь есть в базе данных
        has_all_commands = True

        ... #список всех оповещений
    else:                                                     # Пользователя нет в базе данных
        DB.add_user_to_users(message.chat.id)

    #Кнопки на экране
    create_notification_button = types.KeyboardButton('/create')
    edit_notification_button = types.KeyboardButton('/edit')
    delete_notification_button = types.KeyboardButton('/delete')

    if has_all_commands:
        settings_menu = 'Вам доступны следующие команды :\n \n' \
                        '/create  --  создать напоминание\n' \
                        '/edit  --  изменить напоминание\n' \
                        '/delete  --  удалить напоминание'

        buttons = (create_notification_button, edit_notification_button, delete_notification_button)

        ...
    else:
        settings_menu = 'Вам доступны следующие команды :\n \n' \
                        '/create  --  создать напоминание\n'

        buttons = [create_notification_button]

    [keyboard.add(i) for i in buttons]
    bot.send_message(message.chat.id, settings_menu, reply_markup=keyboard)


@bot.message_handler(commands=['create'])
def create_notification(message):
    DB = Database(DATA)

    if DB.get_quantity_notifiactions(message.chat.id) > MAX_NOTIFICATIONS: # Проверка на макс количество оповещений
        bot.send_message(message.chat.id, 'У вас превышен лимит напоминаний')
        return

    user_in_data = DB.user_exists(message.chat.id)
    have_notification = bool(DB.get_quantity_notifiactions(message.chat.id))
    have_time = bool(DB.get_time(message.chat.id))

    if not(have_notification) and not(have_time): # Выполняется в случае, если у пользователя нет оповещений и нет времени для них
        bot.send_message(message.chat.id, 'Введите время, когда будут отправляться все оповещения (Например 8:30) :')
        bot.register_next_step_handler(message, set_time)
        return

    if user_in_data and have_notification:        # есть напоминания
        all_commands = ['/create', '/edit', '/delete']
    elif user_in_data and not(have_notification): # нет напоминаний
        all_commands = ['/create']

    if message.text in all_commands: # Проверка на доступные пользователю комманды
        if message.text == '/create':
            bot.send_message(message.chat.id, 'Вы можете выбрать следующии дни: \n \n' # Высылается весь список, когда можно отправить оповещение
                                              'Понедельник, Вторник, Среда, Четверг, Пятница, Суббота, Воскресенье, Каждый день')
            bot.register_next_step_handler(message, add_notification)

    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к такой комманде')

def add_notification(message):
    def add_text_to_notification(message):
        DB = Database(DATA)

        # Проверка на исключения
        if len(message) > MAX_OF_SIZE_NOTIFICATION:
            bot.send_message(message.chat.id, f'Превышен лимит символов, попробуйте еще раз,\n'
                                              f'лимит = {MAX_OF_SIZE_NOTIFICATION}')
            bot.register_next_step_handler(message, add_text_to_notification)
        else:
            DB.add_text_to_notifications(message.chat.id, message.text)

    DB = Database(DATA)

    if message.text not in DAYS: # Проверка на исключения
        bot.send_message(message.chat.id, 'Вы ввели неправильный день')
        bot.register_next_step_handler(message, add_notification)
    else:
        DB.add_time_to_notifications(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Введите текст оповещения')
        bot.register_next_step_handler(message, add_text_to_notification)


def set_time(message):
    DB = Database(DATA)

    pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$' # паттерн для проверки времени

    if re.match(pattern, message.text): # Проверка на исключения
        DB.add_time_to_users(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Время успешно поставлено')
    else:
        bot.send_message(message.chat.id, 'Вы неправильно ввели время, попробуйте еще раз :')
        bot.register_next_step_handler(message, set_time)


@bot.message_handler(commands=['help'])
def send_about_bot(message):
    bot.send_message(message.chat.id, ABOUT_BOT)


if __name__ == '__main__':
    bot.polling()