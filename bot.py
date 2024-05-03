import telebot
import sqlite3

from lab3humanfox import identify_picture

token = '7088127624:AAH6hA1c1sZ6fCMedrXDAIvus2xYj8WN07Q'
bot = telebot.TeleBot(token)

name = None
flagLogin = False


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.username}!')


@bot.message_handler(commands=['register'])
def handle_register(message):
    conn = sqlite3.connect('lab3.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    global name
    name = message.from_user.username

    for el in users:
        if el[1] == name:
            bot.send_message(message.chat.id, 'Пользователь уже зарегистрирован!')
            return

    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Для регистрации введите пароль: ')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('lab3.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Регистрация успешна!', reply_markup=markup)
    global flagLogin
    flagLogin = True


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('lab3.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)


@bot.message_handler(commands=['login'])
def handle_login(message):
    global flagLogin
    if flagLogin:
        bot.send_message(message.chat.id, 'Вы уже прошли аутентификацию!')
        return

    bot.send_message(message.chat.id, 'Введите пароль: ')
    bot.register_next_step_handler(message, process_login)


def process_login(message):
    password = message.text.strip()

    conn = sqlite3.connect('lab3.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    username = message.from_user.username

    for el in users:
        if el[1] == username:
            if el[2] == password:
                global flagLogin
                flagLogin = True
                bot.send_message(message.chat.id, 'Вы успешно аутентифицировались!')
                break
            else:
                bot.send_message(message.chat.id, 'Вы неправильно ввели пароль!')
                break
        bot.send_message(message.chat.id, 'Вы не зарегистрированы!')

    cur.close()
    conn.close()


@bot.message_handler(commands=['logout'])
def handle_logout(message):
    global flagLogin
    flagLogin = False
    bot.send_message(message.chat.id, 'Вы успешно вышли из системы!')


@bot.message_handler(commands=['predict'])
def handle_predict(message):
    global flagLogin
    if flagLogin:
        bot.register_next_step_handler(message, human_or_fox)
    else:
        bot.send_message(message.chat.id, 'Сначала вам нужно пройти регистрацию/аутентификацию!')


@bot.message_handler(content_types=['photo'])
def human_or_fox(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'photo.jpg'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, identify_picture('train2/', 'valid2/', 'photo.jpg'))


bot.polling()
