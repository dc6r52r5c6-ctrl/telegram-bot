import telebot

TOKEN =8663322759:AAH3H8m-fk95x4CqcOyofmtL9KVyrR8ny5Q

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Бот работает 🚀")

bot.polling()
