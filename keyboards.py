from telebot import types


sendInfoButton = types.InlineKeyboardButton(text="INFO", callback_data="Info")
manageGroupsButton = types.InlineKeyboardButton(text="Группы", callback_data="ManageGroups")
intervalsEditingButton = types.InlineKeyboardButton(text="Доступность", callback_data="Intervals")

createGroupButton = types.InlineKeyboardButton(text="Создать новую", callback_data="CreateGroup")
backButton = types.InlineKeyboardButton(text="Назад", callback_data="Back_to_main_menu")

chooseGroupButton = types.InlineKeyboardButton(text="Выбрать", callback_data="chooseGroup")