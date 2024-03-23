import telebot
from telebot import types
import data

bot = telebot.TeleBot(data.token)

@bot.message_handler(commands=['start']) 
def handle_start(message): 
    # Разделяем команду и параметры 
    args = message.text.split() 
    # Проверяем, есть ли параметр после /start 
    if len(args) > 1: 
        groupname = args[1] # Получаем параметр

        keyboard = types.InlineKeyboardMarkup()
        yesButton = types.InlineKeyboardButton(text="Да, хочу", callback_data="Yes")
        noButton = types.InlineKeyboardButton(text="Нет", callback_data="No")
        keyboard.add(yesButton, noButton)
        bot.send_message(message.chat.id, f"Ты хочешь вступить в группу {groupname}?", reply_markup=keyboard)

    else: 
        message.reply(f"Привет, я бот для определения общего времени для группы людей.")
        send_help(message)

@bot.message_handler(commands=['help'])
def send_help(message):
    message.answer(f"Я помогу Вам с подбором общего времени с Вашими друзьями/коллегами/знакомыми, с кем бы то ни было. Для Вас есть возможность вступить в какую-либо группу, если Вы знаете ее название и пароль, или создать новую. После этого, Вам и вашим единомышленикам в индивидуальном порядке будет необходимо ввести даты и временные интервалы, которые Вы можете посвятитить друг другу. А далее я предоставлю вам интервалы, которые совпали у всех для того, чтобы Вы могли организовать встречу.")
 
# Запуск бота 
bot.polling(none_stop=True)