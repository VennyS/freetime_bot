import telebot
from telebot import types
import data
from messages import *
import queries
import keyboards

bot = telebot.TeleBot(data.token)

# Функция для вывода основного выбора действий
# ЕСТЬ ВОПРОСЫ! Убрать кнопку Новая группа, вставить ее в INFO
def send_main_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboards.intervalsEditingButton, keyboards.manageGroupsButton, keyboards.sendInfoButton)
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
    user = queries.is_telegramid_exist(telegramid=message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id,  ERROR_MESSAGE)
    else:
        if (not user): queries.register(telegramid=message.from_user.id)

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

@bot.callback_query_handler(func=lambda call: call.data in  ["ManageGroups", "Back_from_creatingGroup"])
def handle_create_group_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboards.createGroupButton,keyboards.chooseGroupButton, keyboards.backButton)
    list_of_groups = queries.get_groups_list_of_user_with_hash(call.from_user.id)
    # Преобразование списка в строку формата "название группы - ссылка"
    formatted_groups = '\n'.join([f'{group[0]} - {generateLink(group[1])}' for group in list_of_groups])
    # chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Создание новой группы отменено"
    # Отправка сообщения с отформатированным списком групп
    if formatted_groups:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Это группы, в которых ты состоишь:\n{formatted_groups}',
            reply_markup=keyboard
        )
    else:
        bot.send_message(call.message.chat.id, 'Ты пока не состоишь в какой-либо группе')
        send_main_keyboard(call.message.chat.id)

# Обработчик колбэка на создание новой группы
@bot.callback_query_handler(func=lambda call: call.data in ["CreateGroup"])
def handle_create_group_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    cancelButton = types.InlineKeyboardButton(text="Отмена", callback_data="Cancel")
    backButton = types.InlineKeyboardButton(text='Назад', callback_data="Back_from_creatingGroup")
    keyboard.add(cancelButton, backButton)
    # Сообщение пользователя, которое передается в validTeamName
    mesg = bot.send_message(call.message.chat.id, TEAM_NAME_MESSAGE, reply_markup=keyboard)
    bot.register_next_step_handler(mesg, validTeamName)

def handle_create_group_callback2(message):
    keyboard = types.InlineKeyboardMarkup()
    cancelButton = types.InlineKeyboardButton(text="Отмена", callback_data="Cancel")
    keyboard.add(cancelButton)
    # Сообщение пользователя, которое передается в validTeamName
    mesg = bot.send_message(message.chat.id, TEAM_NAME_MESSAGE, reply_markup=keyboard)
    bot.register_next_step_handler(mesg, validTeamName)

# Проверка существование группы
def validTeamName(message):
    if not queries.is_team_exists(message.text):
        queries.createGroup(message.text)
        # добавляем пользователя в группу после её создания
        queries.registerInGroup(message.from_user.id, message.text)
        bot.send_message(message.chat.id, f"Группа с именем «{message.text}» создана "
                                          f"\nСсылка на вступления в группу: {generateLink(queries.md5_lower_32bit(message.text))}")
        send_main_keyboard(message.chat.id)
    else:
        bot.send_message(message.chat.id, f"Группа с именем {message.text} уже существует. Попробуйте ещё раз")
        handle_create_group_callback2(message)


# Создаем ссылку
def generateLink(name): return f"https://t.me/schledule_bot?start={name}"

def get_list_of_groups_with_links_from_db_of_user(user_id):
    list_of_groups = queries.get_groups_list_of_user_with_hash(user_id)
    # Преобразование списка в строку формата "название группы - ссылка"
    formatted_groups = '\n'.join([f'{group[0]} - {generateLink(group[1])}' for group in list_of_groups])
    return formatted_groups
@bot.callback_query_handler(func=lambda call: call.data == "Back_to_main_menu")
def handle_GoBack_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboards.sendInfoButton, keyboards.manageGroupsButton, keyboards.intervalsEditingButton)

    groups_of_user = get_list_of_groups_with_links_from_db_of_user(call.from_user.id)
    if groups_of_user:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Это группы, в которых ты состоишь:\n{groups_of_user}'
        )
    else:
        bot.send_message(call.message.chat.id, 'Ты пока не состоишь в какой-либо группе')
    bot.send_message(call.message.chat.id, text='Выберите действие:',   reply_markup=keyboard)

# Колбэк на отмену создания новой группы
@bot.callback_query_handler(func=lambda call: call.data == "Cancel")
def handle_cancel_callback(call):
    # Отменяем текущее действие
    # Нужно что-то сделать с тем, что оно остаётся
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Создание новой группы отменено")

# Обработчик наажания на кнопку Выбрать, то есть выбор группы для дальнейших действий именно с этой группой
@bot.callback_query_handler(func=lambda call: call.data == "chooseGroup")
def handle_choose_group_callback(call):
    groupList = queries.get_groups_list_of_user(call.from_user.id)
    if groupList:
        formatted_groupList = [item[0] for item in groupList] # список из строк
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 1
        for group in formatted_groupList:
            keyboard.add(types.InlineKeyboardButton(group, callback_data=f'group_{group}'))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Выбери нужную для упарвления группу:\n',
            reply_markup=keyboard
        )
    else:
        bot.send_message(call.message.chat.id, text= 'ди нахуй вообще лох')
# Обработчик для выбранной группы
# Благодаря startswitch мы отслеживаем начинается ли строка с заданной
@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def handle_chosen_group_callback(call):
    chosen_group = call.data.split('_', 1)[1] # Достаем название выбранной группы
    bot.send_message(call.message.chat.id, text=f'Вы выбрали группу: {chosen_group}')
# Обработчик колбэка на нажатия на кнопку редактирнования интервалов
# Тут вообще пиздец
@bot.callback_query_handler(func=lambda call: call.data == "Intervals")
def handle_info_callback(call):
    bot.send_message(call.message.chat.id, "Открытие web приложения")

# Запуск бота
if __name__=='__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)

