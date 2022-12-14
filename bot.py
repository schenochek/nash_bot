from telebot import TeleBot
import pymysql

from config import token, db_host, db_user, db_password, db_name
from panels import admin_panel, worker_panel #, user_panel
bot = TeleBot(token)


def connect_to_db():
    try:
        connection = pymysql.connect(
            host=db_host,
            port=3306,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor)
        print('Success!')
        print('#' * 20)
        return connection
    except Exception as ex:
        print('Connection lost')
        print(ex)


def new_user_db(ch_id, usr_name):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            query = f'INSERT INTO `users` (username, chat_id) VALUES (\'{usr_name}\', \'{ch_id}\')' \
                    f'ON DUPLICATE KEY UPDATE username=\'{usr_name}\';'
            cursor.execute(query)
            connection.commit()
    finally:
        connection.close()


def check_admin(usr):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            try:
                query = 'SELECT username, user_group FROM tg_bot.internal_users JOIN tg_bot.users ON' \
                        f' users.chat_id = internal_users.chat_id WHERE internal_users.chat_id = \'{usr}\';'
                cursor.execute(query)
                data = cursor.fetchall()
                for data_temp in data:
                    print(data_temp['username'])
            except Exception as ex:
                print('Проблема поиска check_admin')
                print(ex)
                bot.send_message(usr, "<b>Проблема поиска check_admin</b>", parse_mode="html")
    finally:
        connection.close()
        return data_temp


def db_all_users():
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            try:
                query = 'SELECT chat_id, username FROM tg_bot.users;'
                cursor.execute(query)
                data = cursor.fetchall()
            except Exception as ex:
                print('Проблема поиска check_admin')
                print(ex)
    finally:
        connection.close()
        return data


@bot.message_handler(commands=['start'])
def start(message):
    new_user_db(message.chat.id, message.from_user.username)
    bot.send_message(message.chat.id, "<b>Дарова епта!</b>", parse_mode="html")


@bot.message_handler(commands=['admin_tools'])
def admin_(message):
    temp_check = check_admin(message.chat.id)
    if temp_check['user_group'] == 'admin':
        admin_panel(message, temp_check['username'], bot)
    elif temp_check['user_group'] == 'worker':
        worker_panel(message, temp_check['username'], bot)
    else:
        bot.send_message(message.chat.id, "<b>У вас нет прав доступа к этому разделу!</b>", parse_mode='html')


@bot.message_handler(commands=['alert'])
def alert(message):
    temp_check = check_admin(message.chat.id)
    if temp_check['user_group'] == 'admin':
        bot.send_message(message.chat.id, '<b>Введите сообщение:</b>', parse_mode='html')
        bot.register_next_step_handler(message, get_alert)
    else:
        bot.send_message(message.chat.id, "<b>У вас нет прав доступа к этому разделу!</b>", parse_mode='html')


def get_alert(message):
    temp_users = db_all_users()
    for usr in temp_users:
        bot.send_message(usr['chat_id'], f'<b>{message.text}</b>', parse_mode='html')


bot.infinity_polling()
