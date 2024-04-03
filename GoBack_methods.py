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






