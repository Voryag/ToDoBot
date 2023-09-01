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
DAYS = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')
ROW_WIDTH = 1 # Количество кнопок в строке
MAX_NOTIFICATIONS = 5 # Максимальное количество оповещений
MAX_OF_SIZE_NOTIFICATION = 150 # Максимальное количество символов в оповещении

bot = telebot.TeleBot(TOKEN)

def has_all_commands(message):
    DB = Database(DATA)

    return bool(DB.get_quantity_notifiactions(message.chat.id))

def get_all_notifications(message):
    DB = Database(DATA)

    all_notifications = DB.get_all_notifications(message.chat.id)
    list = 'Список всех ваших уведомлений (id, text, day): \n \n'
    for n in all_notifications:
        list = list + (str(n[0]) + '      ' + n[1] + '      ' + n[2]) + '\n'

    return list

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

    try:
        have_notification = bool(DB.get_quantity_notifiactions(message.chat.id))
    except:
        have_notification = False

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

    if DB.get_quantity_notifiactions(message.chat.id) > 0: # Отправка списка всех оповещений для пользователя
        bot.send_message(message.chat.id, get_all_notifications(message))


@bot.message_handler(commands=['create'])
def create_notification(message):
    DB = Database(DATA)

    if DB.get_quantity_notifiactions(message.chat.id) > MAX_NOTIFICATIONS: # Проверка на макс количество оповещений
        bot.send_message(message.chat.id, 'У вас превышен лимит напоминаний')
        return

    have_notification = bool(DB.get_quantity_notifiactions(message.chat.id))
    have_time = bool(DB.get_time(message.chat.id))

    if not(have_notification) and not(have_time): # Выполняется в случае, если у пользователя нет оповещений и нет времени для них
        bot.send_message(message.chat.id, 'Введите время, когда будут отправляться все оповещения (Например 8:30) :')
        bot.register_next_step_handler(message, set_time)
        return

    if message.text == '/create':
        days = ', '.join(map(str, DAYS))
        bot.send_message(message.chat.id, 'Вы можете выбрать следующии дни для вашего оповещения: \n \n' # Высылается весь список, когда можно отправить оповещение
                                          f'{days} \n \n'
                                          'Причем, если вы хотите выбрать понедельник и субботу, то напишите так: \n'
                                          'Понедельник Пятница или понедельник пятница')
        bot.register_next_step_handler(message, add_notification)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к такой комманде')

def add_notification(message):
    def get_text(message, day):
        DB = Database(DATA)

        if len(message.text) > MAX_OF_SIZE_NOTIFICATION: # Проверка на исключения
            bot.send_message(message.chat.id, f'Превышен лимит символов, попробуйте еще раз,\n' 
                                              f'лимит = {MAX_OF_SIZE_NOTIFICATION}')
            bot.register_next_step_handler(message, get_text)
        else:
            DB.add_notification_to_notification(message.chat.id, message.text, day)
            bot.send_message(message.chat.id, 'Оповещение добавлено')
            increase_the_notification_quantity(message)
            return

    def increase_the_notification_quantity(message):
        DB = Database(DATA)

        quantity = DB.get_quantity_notifiactions(message.chat.id)
        DB.set_new_quantity(message.chat.id, quantity + 1)
        return

    for word in message.text.split(' '): # Проверка на исключения
        if word.capitalize() not in DAYS:
            bot.send_message(message.chat.id, 'Вы ввели неправильный день, попробуйте еще раз :')
            bot.register_next_step_handler(message, add_notification)
            return

    bot.send_message(message.chat.id, 'Введите текст оповещения :')
    bot.register_next_step_handler(message, get_text, message.text)

def set_time(message):
    DB = Database(DATA)

    pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$' # паттерн для проверки времени

    if re.match(pattern, message.text): # Проверка на исключения
        DB.add_time_to_users(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Время успешно поставлено')
        bot.send_message(message.chat.id, 'Введите еще раз команду: /create')
        return
    else:
        bot.send_message(message.chat.id, 'Вы неправильно ввели время, попробуйте еще раз :')
        bot.register_next_step_handler(message, set_time)


@bot.message_handler(commands=['delete'])
def delete_notification(message):
    if has_all_commands(message) == False:
        bot.send_message(message.chat.id, 'У вас нет доступа к такой комманде')
        return

    bot.send_message(message.chat.id, get_all_notifications(message))
    bot.send_message(message.chat.id, 'Введите id вашего оповещения для удаления :')
    bot.register_next_step_handler(message, del_notification)

def del_notification(message):
    DB = Database(DATA)

    chat_id = message.chat.id
    notification_id = message.text
    quantity = DB.get_quantity_notifiactions(message.chat.id)
    user_ids = [str(i[0]) for i in DB.get_id_of_all_notifications(chat_id)]

    if notification_id in user_ids:
        #DB.del_notification(notification_id)
        DB.set_new_quantity(message.chat.id, quantity - 1)
        bot.send_message(message.chat.id, 'Оповещение успешно удалено')
        return
    else:
        #print(user_ids)
        bot.send_message(message.chat.id, 'Введите id из списка')
        bot.register_next_step_handler(message, del_notification)


@bot.message_handler(commands=['help'])
def send_about_bot(message):
    bot.send_message(message.chat.id, ABOUT_BOT)


if __name__ == '__main__':
    bot.polling()