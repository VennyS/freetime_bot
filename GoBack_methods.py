from freetime_bot import bot
from telebot import types
import keyboardsButtons
import functions_

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
        # case 'backButtonFromChosenUserToListOfUsers':
            # groupList = queries.get_groups_list_of_user(call.from_user.id)
            # if groupList:
            #     formatted_groupList = [item[0] for item in groupList]  # список из строк
            #     keyboard = types.InlineKeyboardMarkup()
            #     keyboard.row_width = 1
            #     for group in formatted_groupList:
            #         keyboard.add(types.InlineKeyboardButton(group, callback_data=f'group_{group}'))
            #     keyboard.add(keyboardsButtons.backButtonFromCreatingGroupToMain)
            #     bot.edit_message_text(
            #         chat_id=call.message.chat.id,
            #         message_id=call.message.message_id,
            #         text=f'Выбери нужную для управления группу:\n',
            #         reply_markup=keyboard
            #     )





