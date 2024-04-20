from keyboardsButtons import createGroupButton, backButtonFromCreatingGroupToMain
from telebot import types
import hashlib

available_commands = [
    "/start - Начать",
    "/help - Получить справку",
]

 #Создаем ссылку
def generateLink(name): return f"https://t.me/schledule_bot?start={name}"
        
# Зашифровывает название группы
def md5_lower_32bit(name):
    # Вычисляем хеш MD5
    hash_md5 = hashlib.md5(name.encode())

    # Получаем 16-битное значение хеша
    hash_value = hash_md5.digest()

    # Переводим в строку и возвращаем в нижнем регистре
    return hash_value.hex()