import telebot
from telebot import types
import data

bot = telebot.TeleBot(data.token)

def send_actions_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    sendInfoButton = types.InlineKeyboardButton(text="INFO", callback_data="Info")
    createGroupButton = types.InlineKeyboardButton(text="Новая группа", callback_data="CreateGroup")
    intervalsEditingButton = types.InlineKeyboardButton(text="Доступность", callback_data="Intervals")
    keyboard.add(intervalsEditingButton, createGroupButton, sendInfoButton)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)
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

        # Замыкание для передачик параметра группы в обработчик колбэк запросов
        bot.callback_query_handler(func=lambda call: call.data in ["Yes", "No"])(create_callback_handler(groupname))

        send_actions_keyboard(message.chat.id)
    else: 
        bot.reply_to(message, f"Привет, я бот для определения общего времени для группы людей.")
        if ...: # Если пользователь зарегестрирован в БД, то выводить доп.информацию не нужно
            send_help(message)

        send_actions_keyboard(message.chat.id)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, f"Я помогу вам организовать встречу с вашими друзьями, коллегами или знакомыми, находя удобное общее время для всех участников. Вы можете присоединиться к существующей группе, используя ссылку-приглашение, или создать новую и пригласить других. После того как участники присоединятся, я помогу вам найти время, которое подходит всем, для организации встречи.")

def create_callback_handler(groupname):
    def handle_callback(call):
        if call.data == "Yes":
            # Написать логику проверки такой группы в базе
            # Также проверки возможно этот пользователь уже в этой группе и тд
            bot.send_message(call.message.chat.id, f"Вы присоединились к группе - {groupname}.")
        elif call.data == "No":
            bot.send_message(call.message.chat.id, f"Вы отклонили предложение на вступление в группу -  {groupname}.")
    return handle_callback

@bot.callback_query_handler(func=lambda call: call.data == "Info")
def handle_join_group_callback(call):
    # Обработка нажатия на кнопку "info"
    bot.send_message(call.message.chat.id, "Обработка действия 'info'")

@bot.callback_query_handler(func=lambda call: call.data == "CreateGroup")
def handle_create_group_callback(call):
    # Обработка нажатия на кнопку "Создать новую группу"
    bot.send_message(call.message.chat.id, "Обработка действия 'Создать новую группу'")

@bot.callback_query_handler(func=lambda call: call.data == "Intervals")
def handle_info_callback(call):
    # Обработка нажатия на кнопку "Intervals"
    bot.send_message(call.message.chat.id, "Обработка действия 'intervals'")


# Запуск бота
if __name__=='__main__':
    bot.polling(none_stop=True)