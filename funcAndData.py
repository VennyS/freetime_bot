import queries

available_commands = [
    "/start - Начать",
    "/help - Получить справку",
]

def get_list_of_groups_with_links_from_db_of_user(user_id):
    list_of_groups = queries.get_groups_list_of_user_with_hash(user_id)
    # Преобразование списка в строку формата "название группы - ссылка"
    formatted_groups = '\n'.join([f'{group[0]} - {generateLink(group[1])}' for group in list_of_groups])
    return formatted_groups

 #Создаем ссылку
def generateLink(name): return f"https://t.me/schledule_bot?start={name}"