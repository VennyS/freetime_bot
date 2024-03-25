# Импортируем объект pool
from connection_pool import pool

# Регистрация пользователя
def register(telegramid, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    print(f"INSERT INTO user_info(telegramid) VALUES ({telegramid})")
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
# Пример ее использования в файле usingquery.py
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

def is_user_joined(telegramid, name, pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid} AND name = '{name}')")
        isExist = cursor.fetchone()[0]
        print(isExist)
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