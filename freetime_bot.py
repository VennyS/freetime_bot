import telebot
from telebot import types
import data
from GoBack_methods import *
from messages import *
import queries
import funcAndData
import keyboardsButtons
from timeIntervals import timeIntervals

bot = telebot.TeleBot(data.token)

# Функция для вывода основного выбора действий
# ЕСТЬ ВОПРОСЫ! (Возможно, третья кнопка с выводом общих интервалов добавится)
def send_main_keyboard(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if (len(queries.userTime()) > 0):
        x = timeIntervals(queries.userTime()).hideQuote()
        print(x)
        webAppTest = types.WebAppInfo(f"https://vennys.github.io/?&schedule={x}")
    else: webAppTest = types.WebAppInfo(f"https://vennys.github.io/")
     #создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Страница с расписанием", web_app=webAppTest) #создаем кнопку типа webapp
    keyboard.add(one_butt) #добавляем кнопки в клавиатуру
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)


# Клавиатура для вступления в группу
def send_entery_group_keyboard(chat_id, groupname):
    keyboard = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton(text="Да, хочу", callback_data=f"joinGroup_Yes_{groupname}")
    no_button = types.InlineKeyboardButton(text="Нет", callback_data=f"joinGroup_No_{groupname}")
    keyboard.add(yes_button, no_button)
    bot.send_message(chat_id, f"Ты хочешь вступить в группу {groupname}?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('joinGroup_'))
def handle_join_answer(call):
    answer = call.data.split('_')[1]
    groupname = call.data.split('_')[2]
    if answer == "Yes":
            # Логика регистрации группы
            response = is_team_exist_and_user_in_it(call, queries.md5_lower_32bit(groupname))
            match response:
                case "Вступил":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"Вы успешно вступили в группу «[{groupname}]({funcAndData.generateLink(queries.md5_lower_32bit(groupname))})»",
                                          parse_mode="Markdown")

                case "Ошибка":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Ошибка при попытке вступить в группу")

                case "Состоит":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"Вы уже состоите в группе «{groupname}»")

                case "Отсутствует":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Такая группа либо не существует, либо уже удалена")
            send_main_keyboard(call.message.chat.id)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f"Вы отклонили предложение на вступление в группу — «{groupname}»")
        send_main_keyboard(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('deleteUser_'))
def deleteUser(call):
    userId = call.data.split('_')[1]
    user_firstname = queries.getFirstnameAndNicknameFromUser(userId)[0][0]
    groupname = call.data.split('_')[2]
    adminId = call.from_user.id
    if queries.existsAdminIdWithId(int(adminId), groupname)[0]:
        queries.deleteUserFromAdmin(int(userId), groupname)
        keyboard = types.InlineKeyboardMarkup()
        back_button_from_chosen_user_to_list_of_users = types.InlineKeyboardButton(
            text=f"Вернуться к группе {groupname}",
            callback_data=f"backGroup_{groupname}")
        backButtonFromDeleteUserToChooseGroup = types.InlineKeyboardButton(text='Выбрать другую группу',
                                                                     callback_data="backButtonFromChosenGroupToChoose")
        keyboard.add(back_button_from_chosen_user_to_list_of_users, backButtonFromDeleteUserToChooseGroup)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Пользователь {user_firstname} успешно удалён',
            reply_markup=keyboard
        )

# Метод проверки и регистрации пользователя
def register(message):
    user = queries.is_telegramid_exist(telegramid=message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id, ERROR_MESSAGE)
        return False
    else:
        if not user:
            queries.register(telegramid=message.from_user.id, first_name=message.from_user.first_name,
                             nickname=message.from_user.username)
            # Если только что зарегался
            return True


# Метод проверки на существование группы и регистрации пользователя в ней
def is_team_exist_and_user_in_it(call, groupname_hash):
    group = queries.is_team_exists(groupname_hash)
    group_name = queries.getGroupNameFromHash(groupname_hash)
    # Если группа существует
    if group:
        # Если пользовать не состоит в этой группе
        if not queries.is_user_joined(call.from_user.id, groupname_hash):
            # Если регистрация прошла успешно
            if queries.registerInGroup(call.from_user.id, group_name):
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
    first_time = register(message)

    # Проверка наличия пользователя в БД
    user = queries.is_telegramid_exist(telegramid=message.from_user.id)
    if isinstance(user, Exception):
        bot.send_message(message.chat.id, ERROR_MESSAGE)
    else:
        if not user:
            queries.register(telegramid=message.from_user.id, first_name=message.from_user.first_name,
                             nickname=message.from_user.username)

    # Проверяем, есть ли параметр после /start. [Переход по ссылке]
    if len(args) > 1:
        # Получаем параметр
        # Проверка если пользователь уже состоит в этой группе
        if queries.is_team_exists(args[1]):
            groupname = queries.getGroupNameFromHash(args[1])

            if not queries.is_user_joined(message.from_user.id, groupname):
                send_entery_group_keyboard(message.chat.id, groupname)

            else:
                bot.send_message(message.chat.id, f'Вы уже состоите в группе "{groupname}"')
                send_main_keyboard(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Такой группы не существует, либо вы перешли по несуществующей ссылке")
            send_main_keyboard(message.chat.id)
    # Если /start без ссылки
    else:
        bot.reply_to(message, HELLO_MESSAGE)
        # Если пользователь только что зарегистрировался, то нужно вывести доп.информацию
        if first_time:
            send_help(message)

        send_main_keyboard(message.chat.id)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, HELP_MESSAGE)


# Обработчик колбэк запроса на кнопу info
# Надо доработать
# @bot.callback_query_handler(func=lambda call: call.data == "Info")
# def handle_info_callback(call):
#     bot.send_message(call.message.chat.id, "Список групп с ссылками, а также какая либо служебная информаци")

# @bot.callback_query_handler(func=lambda call: call.data in ["ManageGroups", "Back_to_main_menu_from_creating_group"])
# def handle_manage_group_callback(call):
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.chooseGroupButton,
#                  keyboardsButtons.backButtonFromManageGroupTOMain)
#
#     # Преобразование списка в строку формата "название группы - ссылка"
#     formatted_groups = funcAndData.get_list_of_groups_with_links_from_db_of_user(call.from_user.id)
#
#     # Отправка сообщения с отформатированным списком групп, либо сообщение об отсутствие групп
#     if formatted_groups:
#         bot.edit_message_text(
#             chat_id=call.message.chat.id,
#             message_id=call.message.message_id,  # идентификатор редактируемого сообщения
#             text=f'Это группы, в которых ты состоишь:\n{formatted_groups}',
#             reply_markup=keyboard
#         )
#     else:
#         keyboard = types.InlineKeyboardMarkup()
#         keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromManageGroupTOMain)
#         bot.edit_message_text(
#             chat_id=call.message.chat.id,
#             message_id=call.message.message_id,  # идентификатор редактируемого сообщения
#             text='Ты пока не состоишь в какой-либо группе',
#             reply_markup=keyboard
#         )


# Обработчик колбэка на создание новой группы
@bot.callback_query_handler(func=lambda call: call.data in ["CreateGroup"])
def handle_create_group_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(keyboardsButtons.backButtonFromChosenGroupToChoose)
    # Сообщение пользователя, которое передается в validTeamName
    mesg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=TEAM_NAME_MESSAGE,
        reply_markup=keyboard)
    bot.register_next_step_handler(mesg, valid_team_name)


# Проверка существование группы
def valid_team_name(message):
    if not queries.is_team_exists(queries.md5_lower_32bit(message.text)):
        queries.createGroup(message.text, message.from_user.first_name, message.from_user.id)
        # добавляем пользователя в группу после её создания
        queries.registerInGroup(message.from_user.id, message.text)
        bot.send_message(message.chat.id,
                         f"Группа с именем [{message.text}]({funcAndData.generateLink(queries.md5_lower_32bit(message.text))}) создана ",
                         parse_mode="Markdown")
        send_main_keyboard(message.chat.id)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromCreatingGroupToMain)
        bot.send_message(message.chat.id,
                         f"Группа с именем «{message.text}» уже существует. Попробуйте ещё раз", reply_markup=keyboard)


# Обработчик нажатия на кнопку Выбрать, то есть выбор группы для дальнейших действий именно с ней
@bot.callback_query_handler(func=lambda call: call.data in ["chooseGroup", "backButtonFromChosenGroupToChoose"])
def handle_choose_group_callback(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    group_list = queries.get_groups_list_of_user(call.from_user.id)
    if group_list:
        formatted_group_list = [item[0] for item in group_list]  # список из строк
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 2
        for group in formatted_group_list:
            keyboard.add(types.InlineKeyboardButton(group, callback_data=f'group_{group}'))
        keyboard.add(keyboardsButtons.createGroupButton,keyboardsButtons.backButtonFromManageGroupTOMain)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Выбери нужную для управления группу:\n',
            reply_markup=keyboard
        )
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromManageGroupTOMain)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text='Ты пока не состоишь в какой-либо группе',
            reply_markup=keyboard
        )

# Если ты не админ и нажимаешь на админа
@bot.callback_query_handler(func=lambda call: call.data.startswith("user_"))
def handle_member_actions(call):
    chosen_userid, groupname = call.data.split('_')[1:3]
    chosen_user_username_firstname = queries.getFirstnameAndNicknameFromUser(chosen_userid)

    keyboard = types.InlineKeyboardMarkup()
    back_button_from_chosen_user_to_list_of_users = types.InlineKeyboardButton(text="Назад",
                                                                                    callback_data=f"backGroup_{groupname}")
    button_url = f'https://t.me/{chosen_user_username_firstname[0][1]}'
    link_to_user = types.InlineKeyboardButton(text="Ссылка", url=button_url)

    button_deleteUser = types.InlineKeyboardButton(text="Удалить Пользователя",
                                                        callback_data=f"deleteUser_{chosen_userid}_{groupname}")
    # Если тыкнул на себя
    if (call.from_user.id == int(chosen_userid)):
        keyboard.add(back_button_from_chosen_user_to_list_of_users)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Это ты ЕБЛАН',
            reply_markup=keyboard
        )
    # Если в чужой группе и не админ
    elif not(call.from_user.id == queries.get_Admin_First_Name(groupname)[1]) and not(call.from_user.id == int(chosen_userid)):
        keyboard.add(link_to_user,
                        back_button_from_chosen_user_to_list_of_users)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Пользователь {chosen_user_username_firstname[0][0]}',
            reply_markup=keyboard
        )
    # Если админ и тыкнул на другого
    else:
        keyboard.add(link_to_user, button_deleteUser,
                        back_button_from_chosen_user_to_list_of_users)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Пользователь {chosen_user_username_firstname[0][0]}',
            reply_markup=keyboard
        )

# Обработчик для выбранной группы
# Благодаря startswitch мы отслеживаем начинается ли строка с заданной
@bot.callback_query_handler(func=lambda call: call.data.startswith("group_") or call.data.startswith("backGroup_"))
def handle_chosen_group_callback(call):
    # Достаем название выбранной группы
    chosen_group = call.data.split('_')[1]
    user_list = queries.get_user_list_of_group(chosen_group)
    admin_id = queries.get_Admin_First_Name(chosen_group)
    # Список пользователей группы без админа
    formatted_user_list = [item for item in user_list if item != admin_id]
    keyboard = types.InlineKeyboardMarkup()
    deleteGroupButton = types.InlineKeyboardButton(text='Удалить группу', callback_data=f'deleteGroup_{chosen_group}')
    leaveGroupButton = types.InlineKeyboardButton(text='Выйти из группы', callback_data=f'leaveGroup_{chosen_group}')
    totalTimeButton = types.InlineKeyboardButton(text='Общее время', callback_data=f'totalTime_{chosen_group}')
    keyboard.add(types.InlineKeyboardButton(f"{admin_id[0]} - админ", callback_data=f"user_{admin_id[1]}_{chosen_group}"))

    for user in formatted_user_list:
        keyboard.add(types.InlineKeyboardButton(user[0], callback_data=f"user_{user[1]}_{chosen_group}"))
    # Условие если админ
    userid = call.from_user.id
    # Проверка на админа
    if queries.existsAdminIdWithId(userid, chosen_group)[0]:
        keyboard.add(deleteGroupButton, totalTimeButton, keyboardsButtons.backButtonFromChosenGroupToChoose)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Пользователи группы [{chosen_group}](https://t.me/schledule_bot?start={queries.md5_lower_32bit(chosen_group)}) \n",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        keyboard.add(leaveGroupButton, totalTimeButton, keyboardsButtons.backButtonFromChosenGroupToChoose)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Пользователи группы [{chosen_group}](https://t.me/schledule_bot?start={queries.md5_lower_32bit(chosen_group)}) \n",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('deleteGroup_'))
def deleteGroup(call):
    chosen_group = call.data.split('_')[1]
    queries.deleteGroup(chosen_group)
    # Проверка, остались ли группы, где состоит пользователь
    if queries.existsGroupFromId(call.from_user.id)[0]:
        keyboard = types.InlineKeyboardMarkup()
        backButtonFromDeleteGroupToChooseGroup = types.InlineKeyboardButton(text='Вернуться к группам',
                                                                       callback_data="backButtonFromChosenGroupToChoose")
        keyboard.add(backButtonFromDeleteGroupToChooseGroup)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Группа {chosen_group} успешно удалена',
            reply_markup=keyboard
        )
    else:
        keyboard = types.InlineKeyboardMarkup()
        backButtonFromDeleteGroupToMainMenu = types.InlineKeyboardButton(text='Вернуться в меню',
                                                                       callback_data="Back_to_main_menu_from_manage_group")
        ButtonToCreateGroup = types.InlineKeyboardButton(text='Создать новую группу', callback_data='CreateGroup')
        keyboard.add(ButtonToCreateGroup, backButtonFromDeleteGroupToMainMenu)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'У тебя не осталось групп, в которых ты состоишь',
            reply_markup=keyboard
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("leaveGroup_"))
def leaveinGroup(call):
    chosen_group = call.data.split('_')[1]
    userid = call.from_user.id
    queries.leaveinGroup(userid, chosen_group)
    if queries.existsGroupFromId(call.from_user.id)[0]:
        keyboard = types.InlineKeyboardMarkup()
        backButtonFromDeleteGroupToChooseGroup = types.InlineKeyboardButton(text='Вернуться к группам',
                                                                       callback_data="backButtonFromChosenGroupToChoose")
        keyboard.add(backButtonFromDeleteGroupToChooseGroup)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Вы успешно вышли из группы {chosen_group}',
            reply_markup=keyboard
        )
    else:
        keyboard = types.InlineKeyboardMarkup()
        backButtonFromDeleteGroupToMainMenu = types.InlineKeyboardButton(text='Вернуться в меню',
                                                                       callback_data="Back_to_main_menu_from_manage_group")
        ButtonToCreateGroup = types.InlineKeyboardButton(text='Создать новую группу', callback_data='CreateGroup')
        keyboard.add(ButtonToCreateGroup, backButtonFromDeleteGroupToMainMenu)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # идентификатор редактируемого сообщения
            text=f'Вы успешно вышли из группы {chosen_group}, но у вас не осталось групп, в которых вы состоите',
            reply_markup=keyboard
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('totalTime_'))
def totalTimeFromPeople(call):
    chosen_group = call.data.split('_')[1]
    time = queries.totalTimeWithGroup(chosen_group)
    print(time)


# Обработка кнопок Назад
@bot.callback_query_handler(func=lambda call: call.data in ["Back_to_main_menu_from_manage_group"])
def handle_go_back_from_creating_group(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    GoBack(call)


# Обработчик колбэка на нажатия на кнопку редактирнования интервалов
# Тут вообще пиздец
@bot.callback_query_handler(func=lambda call: call.data == "Intervals")
def handle_web_callback(call):
    bot.send_message(call.message.chat.id, "Открытие web приложения")

import json

@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
    freetime = timeIntervals(webAppMes.web_app_data.data)
    queries.insert(freetime.toTSRange())
    # bot.send_message(webAppMes.chat.id, f"получили инофрмацию из веб-приложения: {webAppMes.web_app_data.data}")
    bot.send_message(webAppMes.chat.id, "Данные получил!")

# Обработка ввода неизвестного сообщения - ответ бота это список команд
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id,
                     "Эта команда неизвестна. "
                     "Список доступных команд:\n" + "\n".join(funcAndData.available_commands))

# Запуск бота
if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
