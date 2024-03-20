from secret_token import token
import telebot

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "Привет, я бот для определения общего времени для группы людей")

bot.infinity_polling()