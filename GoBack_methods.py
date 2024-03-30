from freetime_bot import bot
from telebot import types
import keyboardsButtons
import functions_

def GoBack(call):
    match(call.data):
        case 'Back_to_main_menu_from_manage_group':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(keyboardsButtons.intervalsEditingButton, keyboardsButtons.manageGroupsButton)

            groups_of_user = functions_.get_list_of_groups_with_links_from_db_of_user(call.from_user.id)
            if groups_of_user:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f'Это группы, в которых ты состоишь:\n{groups_of_user}'
                )
            else:
                bot.send_message(call.message.chat.id, 'Ты пока не состоишь в какой-либо группе')
            bot.send_message(call.message.chat.id, text='Выберите действие:', reply_markup=keyboard)

        case "Back_to_main_menu_from_creating_group":
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(keyboardsButtons.intervalsEditingButton, keyboardsButtons.manageGroupsButton)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Выберите действие:',
                reply_markup=keyboard
            )






