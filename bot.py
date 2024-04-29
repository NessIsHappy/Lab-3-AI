import telebot

token = '7088127624:AAH6hA1c1sZ6fCMedrXDAIvus2xYj8WN07Q'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.reply_to(message, 'Серега - гей.')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, 'Получено сообщение: ' + message.text)


bot.polling()
