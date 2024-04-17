# Импортируем объект pool
from connection_pool import pool

import hashlib


# Регистрация пользователя
def register(telegramid, first_name, nickname, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO user_info(telegramid, first_name, nickname) VALUES ({telegramid}, '{first_name}',"
                       f" '{nickname}')")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


# Функция для проверки наличия telegramid в БД
def is_telegramid_exist(telegramid, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM user_info WHERE telegramid = {telegramid})")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


def is_team_exists(groupname_hash, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM team WHERE hash = '{groupname_hash}')")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


# Проверка состоит ли пользователь в группе
def is_user_joined(telegramid, groupname, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid} "
                       f"AND name = '{groupname}')")
        isExist = cursor.fetchone()[0]
        return isExist
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


# Регистрация пользователя в группу
def registerInGroup(telegramid, group_name, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO view_member(telegramid, name) VALUES ({telegramid}, '{group_name}')")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
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
def createGroup(name, first_name, telegramid, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"INSERT INTO view_team(name, first_name, telegramid, hash) VALUES ('{name}', '{first_name}', "
                       f"{telegramid}, '{md5_lower_32bit(name)}')")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


# Получаем все группы в которых состоит пользователь
# def get_groups_list_of_user_with_hash(telegramid, pool=pool):
#     conn = pool.get_connection()
#     cursor = conn.cursor()
#     # Пробуем сделать запрос
#     try:
#         cursor.execute(f"SELECT team.name, team.hash "
#                        f"FROM team JOIN member ON team.id = member.teamid "
#                        f"JOIN user_info ON member.userid = user_info.id "
#                        f"WHERE user_info.telegramid = {telegramid};")
#         list_of_users_groups_with_hash = cursor.fetchall()
#         return list_of_users_groups_with_hash
#     # Если появилась ошибка, то возвращаем ошибку
#     except Exception as e:
#         print(e)
#         return e
#     # Отдаем подключение обратно в пулл
#     finally:
#         pool.put_connection(conn)


def get_groups_list_of_user(telegramid, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT name FROM view_member WHERE telegramid = {telegramid}")
        list_of_users_groups = cursor.fetchall()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


def get_user_list_of_group(name, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT first_name, telegramid FROM view_member WHERE name = '{name}'")
        user_list_of_group = cursor.fetchall()
        return user_list_of_group
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


def get_Admin_First_Name(group_name, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT first_name, telegramid FROM view_team WHERE name = '{group_name}'")
        adminId = cursor.fetchone()
        return adminId
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


def getGroupNameFromHash(hash):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT name FROM team WHERE hash = '{hash}'")
        list_of_users_groups = cursor.fetchone()[0]
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)


def getFirstnameAndNicknameFromUser(telegramid):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT first_name, nickname FROM user_info WHERE telegramid = '{telegramid}'")
        list_of_users_groups = cursor.fetchall()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def existsAdminIdWithId(telegramid, groupname):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_team WHERE telegramid = {telegramid} AND name = '{groupname}')")
        list_of_users_groups = cursor.fetchone()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def deleteUserFromAdmin(telegramid, gpoupname):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM view_member WHERE telegramid = {telegramid} AND name = '{gpoupname}'")
        conn.commit()
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def deleteGroup(gpoupname):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM view_member WHERE name = '{gpoupname}'")
        cursor.execute(f"DELETE FROM team WHERE name = '{gpoupname}'")
        conn.commit()
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def existsGroupFromId(telegramid):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid})")
        list_of_users_groups = cursor.fetchone()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def leaveinGroup(telegramid, gpoupname):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM view_member WHERE telegramid = {telegramid} and name = '{gpoupname}'")
        conn.commit()
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def totalTimeWithGroup(gpoupname):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT * FROM find_group_intersections('{gpoupname}')")
        list_of_users_groups = cursor.fetchone()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

def userTime(telegramid, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        cursor.execute(f"SELECT freetime FROM freetime WHERE userid = {telegramid}")
        list_of_users_groups = cursor.fetchall()
        return list_of_users_groups
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)

# Регистрация пользователя
def insert(telegramid, freetime, pool=pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        print(f"INSERT INTO freetime(userid, freetime) VALUES ({telegramid}, {freetime}) ON CONFLICT (id) DO UPDATE SET freetime = {freetime}")
        cursor.execute(f"INSERT INTO freetime(userid, freetime) VALUES ({telegramid}, {freetime}) ON CONFLICT (userid) DO UPDATE SET freetime = {freetime};")
        conn.commit()
        return True
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        print(e)
        return e
    # Отдаем подключение обратно в пулл
    finally:
        pool.put_connection(conn)