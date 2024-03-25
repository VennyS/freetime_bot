import telebot
from telebot import types
import data
from messages import *
import queries

bot = telebot.TeleBot(data.token)
waiting_for_groupname = {}

def send_main_keyboard(chat_id): # Функция для вывода основного выбора дейстий
    keyboard = types.InlineKeyboardMarkup()
    sendInfoButton = types.InlineKeyboardButton(text="INFO", callback_data="Info")
    createGroupButton = types.InlineKeyboardButton(text="Новая группа", callback_data="CreateGroup")
    intervalsEditingButton = types.InlineKeyboardButton(text="Доступность", callback_data="Intervals")
    keyboard.add(intervalsEditingButton, createGroupButton, sendInfoButton)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)

def send_entery_group_keyboard(chat_id, groupname):
    keyboard = types.InlineKeyboardMarkup()
    yesButton = types.InlineKeyboardButton(text="Да, хочу", callback_data="Yes")
    noButton = types.InlineKeyboardButton(text="Нет", callback_data="No")
    keyboard.add(yesButton, noButton)
    bot.send_message(chat_id, f"Ты хочешь вступить в группу {groupname}?", reply_markup=keyboard)

def create_callback_handler(groupname): # Обработчик колбэк запроса с параметром группы
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
            
            send_main_keyboard(call.message.chat.id)
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


@bot.message_handler(commands=['start']) # Обработчик команды /start или перехода по ссылке
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

@bot.message_handler(commands=['help']) # Обработчик команды /help
def send_help(message): # Функция вывода описания бота (Используется также при команде /start, если пользователь не зареган)
    bot.send_message(message.chat.id,  HELP_MESSAGE)


@bot.callback_query_handler(func=lambda call: call.data == "Info") # Обработчик колбэк запроса на кнопу info
def handle_info_callback(call):
    bot.send_message(call.message.chat.id, "Список групп с ссылками, а также какая либо служебная информаци")


@bot.callback_query_handler(func=lambda call: call.data == "CreateGroup") # Обработчик колбэка на создание новой группы
def handle_create_group_callback(call):                                                                                 # Реалезовать логику отмены из любого действия
    keyboard = types.InlineKeyboardMarkup()
    cancelButton = types.InlineKeyboardButton(text="Отмена", callback_data="Cancel")
    keyboard.add(cancelButton)
    bot.send_message(call.message.chat.id, "Напишите название группы, которую вы хотите создать:", reply_markup=keyboard)
    # Устанавливаем состояние ожидания названия группы
    waiting_for_groupname[call.message.chat.id] = True


@bot.message_handler(func=lambda message: waiting_for_groupname.get(message.chat.id)) # Обработчик колбэка на ввод названия новой группы
def handle_groupname_input(message):
    groupname = message.text

    if groupname_exists(groupname): # Функция проверки существования такой группы
        bot.send_message(message.chat.id, "Группа с таким названием уже существует. Попробуйте еще раз")
        return

                                                                                                                        # Если название прошло все проверки, можно продолжать создание группы
    # Удаляем состояние ожидания названия группы
    waiting_for_groupname.pop(message.chat.id)
                                                                                                                        # Логика создания ссылки а также шифрование

@bot.callback_query_handler(func=lambda call: call.data == "Cancel") # Колбэк на отмену создания новой группы
def handle_cancel_callback(call):
    # Отменяем текущее действие
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Создание новой группы отменено")
    # Удаляем состояние ожидания названия группы
    waiting_for_groupname.pop(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "Intervals") # Обработчик колбэка на нажатия на кнопку редактирнования интервалов
def handle_info_callback(call):
    bot.send_message(call.message.chat.id, "Открытие web приложения")


# Запуск бота
if __name__=='__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)