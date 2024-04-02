from freetime_bot import bot
from telebot import types
import keyboardsButtons
import functions_
import queries

def GoBack(call):
    match(call.data):
        case 'Back_to_main_menu_from_manage_group':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(keyboardsButtons.intervalsEditingButton, keyboardsButtons.manageGroupsButton)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Выберите действие:',
                reply_markup=keyboard)

        case "Back_to_main_menu_from_creating_group":
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.chooseGroupButton,
                         keyboardsButtons.backButtonFromManageGroupTOMain)
            groups_of_user = functions_.get_list_of_groups_with_links_from_db_of_user(call.from_user.id)
            if groups_of_user:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text= f'Это группы, в которых ты состоишь:\n{groups_of_user}',
                    reply_markup = keyboard)
            else:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(keyboardsButtons.createGroupButton, keyboardsButtons.backButtonFromManageGroupTOMain)
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='Выберите действие:',
                    reply_markup = keyboard)
        case 'backButtonFromChosenGroupToChoose':
            groupList = queries.get_groups_list_of_user(call.from_user.id)
            if groupList:
                formatted_groupList = [item[0] for item in groupList]  # список из строк
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

    if call.data.startswith("backGroup_"):
        chosen_group = call.data.split('_', 1)[1]  # Достаем название выбранной группы
        userList = queries.get_user_list_of_group(chosen_group)
        adminId = queries.get_Admin_First_Name(chosen_group)
        formatted_userList = [item[0] for item in userList if item != adminId]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(f"{adminId[0]} - админ", callback_data=f"user_{adminId[0]}"))
        for user in formatted_userList:
            keyboard.add(types.InlineKeyboardButton(user, callback_data=f"user_{user}"))
        keyboard.add(keyboardsButtons.backButtonFromChosenGroupToChoose)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Пользователи группы «{chosen_group}»: \n',
            reply_markup=keyboard
        )





