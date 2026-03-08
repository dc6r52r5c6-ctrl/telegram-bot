8663322759:AAHbU0hf9fCPxP65oVAqpkXEoqJBO10WYfQ
import telebot

TOKEN = "ТУТ_НОВЫЙ_ТОКЕН"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Бот работает 🚀")

bot.polling()

