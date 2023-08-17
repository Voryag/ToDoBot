import telebot
from telebot import types
from db import Database

TOKEN = '6625778795:AAEkvLSDlu2WayMyFRqpw1CkK_sxoxR2Pzk'  # Токен бота
ABOUT_BOT = 'Этот бот даёт возможность создать напоминание' \
            ' для любого дня недели в определенное время'
DATA = 'Database\\users.db'
ROW_WIDTH = 1 # Количество кнопок в строке
MAX_NOTIFICATIONS = 15 # Максимальное количество оповещений

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
    else:                                                                                # Пользователя нет в базе данных
        DB.add_user_to_users(message.chat.id)

    #Кнопки на экране
    create_notification_button = types.KeyboardButton('/create')
    edit_notification_button = types.KeyboardButton('/edit')
    delete_notification_button = types.KeyboardButton('/delete')

    if has_all_commands:
        settings_menu = 'Вам доступны следующие команды:\n \n' \
                        '/create  --  создать напоминание\n' \
                        '/edit  --  изменить напоминание\n' \
                        '/delete  --  удалить напоминание'

        buttons = (create_notification_button, edit_notification_button, delete_notification_button)

        ...
    else:
        settings_menu = 'Вам доступны следующие команды:\n \n' \
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

    if have_notification == False:
        bot.send_message(message.chat.id, 'Введите время, когда будут отправляться все оповещения:')
        bot.register_next_step_handler(message, set_time)

    if user_in_data and have_notification: # есть напоминания
        has_all_commands = True
    elif user_in_data and not(have_notification): # нет нпоминаний
        pass

def set_time(message):
    DB = Database(DATA)

    DB.add_time_to_users(message.chat.id, message.text)


@bot.message_handler(commands=['help'])
def send_about_bot(message):
    bot.send_message(message.chat.id, ABOUT_BOT)


if __name__ == '__main__':
    bot.polling()
