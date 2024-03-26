import telebot
from telebot import types
import data
from messages import *
import queries

bot = telebot.TeleBot(data.token)
waiting_for_groupname = {}

# Функция для вывода основного выбора действий
# ЕСТЬ ВОПРОСЫ! Убрать кнопку Новая группа, вставить ее в INFO
def send_main_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    sendInfoButton = types.InlineKeyboardButton(text="INFO", callback_data="Info")
    createGroupButton = types.InlineKeyboardButton(text="Новая группа", callback_data="CreateGroup")
    intervalsEditingButton = types.InlineKeyboardButton(text="Доступность", callback_data="Intervals")
    keyboard.add(intervalsEditingButton, createGroupButton, sendInfoButton)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)

# Клавиатура для вступления в группу
def send_entery_group_keyboard(chat_id, groupname):
    keyboard = types.InlineKeyboardMarkup()
    yesButton = types.InlineKeyboardButton(text="Да, хочу", callback_data="Yes")
    noButton = types.InlineKeyboardButton(text="Нет", callback_data="No")
    keyboard.add(yesButton, noButton)
    bot.send_message(chat_id, f"Ты хочешь вступить в группу {groupname}?", reply_markup=keyboard)

# Обработчик колбэк запроса с параметром группы
def create_callback_handler(groupname): 
    def handle_callback(call): # Функция обработки колбэк запроса
        if call.data == "Yes":
            # Логика регистрации группы
            response = team(call, groupname)
            match (response):
                case "Вступил":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Вы успешно вступили в группу {groupname}.")
                case "Ошибка":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text="Ошибка при попытке вступить в группу.")
                case "Состоит":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text=f"Вы уже состоите в группе {groupname}.")
                case "Отсутствует":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Такая группа либо не существует, либо уже удалена.")
        elif call.data == "No":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Вы отклонили предложение на вступление в группу — {groupname}.")
        send_main_keyboard(call.message.chat.id)
    return handle_callback

# Метод проверки и регистрации пользователя
def register(message):
    user = queries.is_telegramid_exist(telegramid = message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id,  ERROR_MESSAGE)
        return False
    else:     
        if (not user):
            queries.register(telegramid = message.from_user.id)
            # Если только что зарегался
            return True
        
# Метод проверки на существование группы и регистрации пользователя в ней        
def team(call, name):
    group = queries.is_team_exists(name)
    # Если группа существует
    if (group):
        # Если пользовать не состоит в этой группе
        if (not queries.is_user_joined(call.from_user.id, name)):
            # Если регистрация прошла успешно
            if (queries.registerInGroup(call.from_user.id, name)):
                return "Вступил"
            else:
                return "Ошибка"
        # Если пользовать уже состоит в этой группе
        else: 
            return "Состоит"
    # Если группа не существует            
    else: 
        return "Отсутствует"

# Обработчик команды /start или перехода по ссылке
# Есть вопросы! Надо обработать любой текст сюда же
@bot.message_handler(commands=['start']) 
def handle_start(message): 
    # Разделяем команду и параметры 
    args = message.text.split()

    firstTime = register(message)

    # Проверка наличия пользователя в БД
    user = queries.is_telegramid_exist(telegramid = message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id,  ERROR_MESSAGE)
    else:     
        if (not user): queries.register(telegramid = message.from_user.id)

    # Проверяем, есть ли параметр после /start. [Переход по ссылке]
    if len(args) > 1: 
        groupname = args[1] # Получаем параметр

        send_entery_group_keyboard(message.chat.id, groupname)

        # Замыкание для передачи параметра группы в обработчик колбэк запросов
        bot.callback_query_handler(func=lambda call: call.data in ["Yes", "No"])(create_callback_handler(groupname))
    # Если /start без ссылки
    else:
        bot.reply_to(message, HELLO_MESSAGE)
        # Если пользователь только что зарегистрировался, то нужно вывести доп.информацию
        if (firstTime):
            send_help(message)

        send_main_keyboard(message.chat.id)

# Обработчик команды /help
@bot.message_handler(commands=['help']) 
def send_help(message): # Функция вывода описания бота (Используется также при команде /start, если пользователь не зареган)
    bot.send_message(message.chat.id,  HELP_MESSAGE)

# Обработчик колбэк запроса на кнопу info
# Надо доработать
@bot.callback_query_handler(func=lambda call: call.data == "Info") 
def handle_info_callback(call):
    bot.send_message(call.message.chat.id, "Список групп с ссылками, а также какая либо служебная информаци")

# Обработчик колбэка на создание новой группы
# Надо доработать.
@bot.callback_query_handler(func=lambda call: call.data == "CreateGroup") 
def handle_create_group_callback(call):                                                                                 
    keyboard = types.InlineKeyboardMarkup()
    cancelButton = types.InlineKeyboardButton(text="Отмена", callback_data="Cancel")
    keyboard.add(cancelButton)
    bot.send_message(call.message.chat.id, TEAM_NAME_MESSAGE, reply_markup=keyboard)
    # Устанавливаем состояние ожидания названия группы
    waiting_for_groupname[call.message.chat.id] = True

# Обработчик колбэка на ввод названия новой группы
# Надо доработать. Добавить шифрование
@bot.message_handler(func=lambda message: waiting_for_groupname.get(message.chat.id))
def handle_groupname_input(message):
    groupname = message.text

    
    if queries.is_team_exists(groupname): # Функция проверки существования такой группы
        bot.send_message(message.chat.id, "Группа с таким названием уже существует. Попробуйте еще раз")

    # Удаляем состояние ожидания названия группы
    waiting_for_groupname.pop(message.chat.id)
    # Логика создания ссылки а также шифрование

# Колбэк на отмену создания новой группы
@bot.callback_query_handler(func=lambda call: call.data == "Cancel") 
def handle_cancel_callback(call):
    # Отменяем текущее действие
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Создание новой группы отменено")
    # Удаляем состояние ожидания названия группы
    waiting_for_groupname.pop(call.message.chat.id)

# Обработчик колбэка на нажатия на кнопку редактирнования интервалов
# Тут вообще пиздец
@bot.callback_query_handler(func=lambda call: call.data == "Intervals")
def handle_info_callback(call):
    bot.send_message(call.message.chat.id, "Открытие web приложения")


# Запуск бота
if __name__=='__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)