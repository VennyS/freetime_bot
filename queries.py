# Импортируем объект pool
from connection_pool import pool

import hashlib

# Регистрация пользователя
def register(telegramid, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO user_info(telegramid) VALUES ({telegramid})")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Функция для проверки наличия telegramid в БД
def is_telegramid_exist(telegramid, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM user_info WHERE telegramid = {telegramid})")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def is_team_exists(name, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM team WHERE name = '{name}')")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Проверка состоит ли пользователь в группе
def is_user_joined(telegramid, name, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid} AND name = '{name}')")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Регистрация пользователя в группу
def registerInGroup(telegramid, name, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO view_member(telegramid, name) VALUES ('{telegramid}', '{name}')")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Зашифровывает название группы
def md5_lower_32bit(name):
    # Вычисляем хеш MD5
    hash_md5 = hashlib.md5(name.encode())

    # Получаем 16-битное значение хеша
    hash_value = hash_md5.digest()

    # Переводим в строку и возвращаем в нижнем регистре
    return hash_value.hex()

# Добавляет группу и её хэш в таблицу team
def createGroup(name, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO team(name, hash) VALUES ('{name}', '{md5_lower_32bit(name)}')")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Получаем все группы в которых состоит пользователь
def get_groups_list_of_user(telegramid, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT team.name, team.hash "
                       f"FROM team JOIN member ON team.id = member.teamid "
                       f"JOIN user_info ON member.userid = user_info.id "
                       f"WHERE user_info.telegramid = {telegramid};")
        list_of_users_group = cursor.fetchall()
        return list_of_users_group
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


