import telebot
from telebot import types
import data
from messages import *
import queries
import keyboardsButtons
from GoBack_methods import *
import functions_

bot = telebot.TeleBot(data.token)

# Функция для вывода основного выбора действий
# ЕСТЬ ВОПРОСЫ! (Возможно, третья кнопка с выводом общих интервалов добавится)
def send_main_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboardsButtons.intervalsEditingButton, keyboardsButtons.manageGroupsButton)
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
            response = isTeamExistnadUserInIt(call, queries.md5_lower_32bit(groupname))
            print(response)
            match (response):
                case "Вступил": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                       text=f"Вы успешно вступили в группу «{groupname}»")
                    
                case "Ошибка": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                     text="Ошибка при попытке вступить в группу")
                    
                case "Состоит": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text=f"Вы уже состоите в группе «{groupname}»")
                                        
                case "Отсутствует": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                           text="Такая группа либо не существует, либо уже удалена")
            send_main_keyboard(call.message.chat.id)
                         
        elif call.data == "No":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Вы отклонили предложение на вступление в группу — «{groupname}»")
            send_main_keyboard(call.message.chat.id)

        elif call.data.startswith("user_"):
                chosen_userid = call.data.split('_', 1)[1]
                chosen_user = queries.getUsernameAndFirstnameFromUser(chosen_userid)
                if call.from_user.id == queries.get_Admin_First_Name(groupname)[1]:
                    keyboard = types.InlineKeyboardMarkup()
                    backButtonFromChosenUserToListOfUsers = types.InlineKeyboardButton(text="Назад",
                                                                                       callback_data=f"backGroup_{groupname}")
                    button_url = f'https://t.me/{chosen_user[0][1]}'
                    linkToUser = types.InlineKeyboardButton(text="Ссылка", url=button_url)
                    keyboard.add(linkToUser, keyboardsButtons.deleteUser,
                                 backButtonFromChosenUserToListOfUsers)
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,  # идентификатор редактируемого сообщения
                        text=f'Пользователь {chosen_user[0][0]}',
                        reply_markup=keyboard
                    )
                else:
                    keyboard = types.InlineKeyboardMarkup()
                    backButtonFromChosenUserToListOfUsers = types.InlineKeyboardButton(text="Назад",
                                                                                       callback_data=f"backGroup_{groupname}")
                    button_url = f'https://t.me/{chosen_user[0][1]}'
                    linkToUser = types.InlineKeyboardButton(text="Ссылка", url=button_url)
                    keyboard.add(linkToUser, keyboardsButtons.deleteUser,
                                 backButtonFromChosenUserToListOfUsers)
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,  # идентификатор редактируемого сообщения
                        text=f'Пользователь {chosen_user[0][0]}',
                        reply_markup=keyboard
                    )

    return handle_callback

# Метод проверки и регистрации пользователя
def register(message):
    user = queries.is_telegramid_exist(telegramid=message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id,  ERROR_MESSAGE)
        return False
    else:
        if (not user):
            queries.register(telegramid=message.from_user.id, first_name=message.from_user.first_name,
                             nickname=message.from_user.username)
            # Если только что зарегался
            return True

# Метод проверки на существование группы и регистрации пользователя в ней
def isTeamExistnadUserInIt(call, hash):
    group = queries.is_team_exists(hash)
    group_name = queries.getGroupNameFromHash(hash)
    # Если группа существует
    if (group):
        # Если пользовать не состоит в этой группе
        if (not queries.is_user_joined(call.from_user.id, hash)):
            # Если регистрация прошла успешно
            if (queries.registerInGroup(call.from_user.id, group_name)):
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
        if (not user): queries.register(telegramid=message.from_user.id, first_name=message.from_user.first_name)

    # Проверяем, есть ли параметр после /start. [Переход по ссылке]
    if len(args) > 1:
        # Получаем параметр
        # Проверка если пользователь уже состоит в этой группе
        groupname = queries.getGroupNameFromHash(args[1])

        if not queries.is_user_joined(message.from_user.id, groupname):
            send_entery_group_keyboard(message.chat.id, groupname)

            # Замыкание для передачи параметра группы в обработчик колбэк запросов
            bot.callback_query_handler(func=lambda call: call.data in ["Yes", "No"])(create_callback_handler(groupname))
        else:
            bot.send_message(message.chat.id, f'Вы уже состоите в группе "{groupname}"')
            send_main_keyboard(message.chat.id)
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
# @bot.callback_query_handler(func=lambda call: call.data == "Info")
# def handle_info_callback(call):
#     bot.send_message(call.message.chat.id, "Список групп с ссылками, а также какая либо служебная информаци")

@bot.callback_query_handler(func=lambda call: call.data in  ["ManageGroups"] or call.data == "Back_to_main_menu_from_creating_group")
def handle_manage_group_callback(call):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.chooseGroupButton,
                     keyboardsButtons.backButtonFromManageGroupTOMain)

        # Преобразование списка в строку формата "название группы - ссылка"
        formatted_groups = functions_.get_list_of_groups_with_links_from_db_of_user(call.from_user.id)
        
        # Отправка сообщения с отформатированным списком групп, либо сообщение об отсутствие групп
        if formatted_groups:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,  # идентификатор редактируемого сообщения
                text=f'Это группы, в которых ты состоишь:\n{formatted_groups}',
                reply_markup= keyboard
            )
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromManageGroupTOMain)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,  # идентификатор редактируемого сообщения
                text= 'Ты пока не состоишь в какой-либо группе',
                reply_markup=keyboard
            )
# Обработчик колбэка на создание новой группы
@bot.callback_query_handler(func=lambda call: call.data in ["CreateGroup"])
def handle_create_group_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboardsButtons.backButtonFromCreatingGroupToMain)
    # Сообщение пользователя, которое передается в validTeamName
    mesg = bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEAM_NAME_MESSAGE,
                reply_markup=keyboard)
    bot.register_next_step_handler(mesg, validTeamName)

# Проверка существование группы
def validTeamName(message):
    if not queries.is_team_exists(queries.md5_lower_32bit(message.text)):
        queries.createGroup(message.text, message.from_user.first_name, message.from_user.id)
        # добавляем пользователя в группу после её создания
        queries.registerInGroup(message.from_user.id, message.text)
        bot.send_message(message.chat.id, f"Группа с именем «{message.text}» создана "
                                          f"\nСсылка на вступления в группу:"
                                          f" {functions_.generateLink(queries.md5_lower_32bit(message.text))}")
        send_main_keyboard(message.chat.id)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromCreatingGroupToMain)
        bot.send_message(message.chat.id,
                         f"Группа с именем «{message.text}» уже существует. Попробуйте ещё раз", reply_markup=keyboard)


# Обработчик нажатия на кнопку Выбрать, то есть выбор группы для дальнейших действий именно с ней
@bot.callback_query_handler(func=lambda call: call.data == "chooseGroup" or call.data == "backButtonFromChosenGroupToChoose")
def handle_choose_group_callback(call):
    groupList = queries.get_groups_list_of_user(call.from_user.id)
    if groupList:
        formatted_groupList = [item[0] for item in groupList] # список из строк
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 1
        for group in formatted_groupList:
            keyboard.add(types.InlineKeyboardButton(group, callback_data=f'group_{group}'))
        keyboard.add(keyboardsButtons.backButtonFromCreatingGroupToMain)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Выбери нужную для управления группу:\n',
            reply_markup=keyboard
        )

# Обработчик для выбранной группы
# Благодаря startswitch мы отслеживаем начинается ли строка с заданной
@bot.callback_query_handler(func=lambda call: call.data.startswith("group_") or call.data.startswith("backGroup_"))
def handle_chosen_group_callback(call):
    chosen_group = call.data.split('_', 1)[1] # Достаем название выбранной группы
    userList = queries.get_user_list_of_group(chosen_group)
    adminId = queries.get_Admin_First_Name(chosen_group)
    formatted_userList = [item for item in userList if item != adminId]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f"{adminId[0]} - админ", callback_data=f"user_{adminId[1]}"))
    for user in formatted_userList:
        keyboard.add(types.InlineKeyboardButton(user[0], callback_data=f"user_{user[1]}"))
    keyboard.add(keyboardsButtons.backButtonFromChosenGroupToChoose)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Пользователи группы «{chosen_group}»: \n',
        reply_markup=keyboard
    )
    bot.callback_query_handler(func=lambda call: call.data.startswith("user_"))(create_callback_handler(chosen_group))

# Обработка кнопок Назад
@bot.callback_query_handler(func=lambda call: call.data in ["Back_to_main_menu_from_creating_group",
                                                            "Back_to_main_menu_from_manage_group"])
                                              # or call.data.startswith("backGroup_")
def handle_goBack_from_creatingGroup(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    GoBack(call)

# Обработчик колбэка на нажатия на кнопку редактирнования интервалов
# Тут вообще пиздец
@bot.callback_query_handler(func=lambda call: call.data == "Intervals")
def handle_web_callback(call):
    bot.send_message(call.message.chat.id, "Открытие web приложения")

# Запуск бота
if __name__=='__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)

