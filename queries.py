# Импортируем объект pool
from connection_pool import pool as conn_pool
import inspect
from funcAndData import md5_lower_32bit

def handle_database_exceptions(func):
    def wrapper(*args, **kwargs):
        pool = conn_pool
        conn = pool.get_connection()
        cursor = conn.cursor()
        try:
            if ('conn' in inspect.signature(func).parameters): return func(*args, **kwargs, cursor=cursor, conn=conn)
            else: return func(*args, **kwargs, cursor=cursor)             
        except Exception as e:
            print(e)
            return e
        finally:
            pool.put_connection(conn)
    return wrapper

# Регистрация пользователя
@handle_database_exceptions
def register(telegramid, first_name, nickname, *, cursor, conn):
    cursor.execute(f"INSERT INTO user_info(telegramid, first_name, nickname) VALUES ({telegramid}, '{first_name}', '{nickname}')")
    conn.commit()
    return True


# Функция для проверки наличия telegramid в БД
@handle_database_exceptions
def is_telegramid_exist(telegramid, *, cursor):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM user_info WHERE telegramid = {telegramid})")
    isExist = cursor.fetchone()[0]
    return isExist

# Проверка существует ли группа
@handle_database_exceptions
def is_team_exists(groupname_hash, *, cursor):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM team WHERE hash = '{groupname_hash}')")
    isExist = cursor.fetchone()[0]
    return isExist


# Проверка состоит ли пользователь в группе
@handle_database_exceptions
def is_user_joined(telegramid, groupname, *, cursor):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid} "
                    f"AND name = '{groupname}')")
    isExist = cursor.fetchone()[0]
    return isExist


# Регистрация пользователя в группу
@handle_database_exceptions
def registerInGroup(telegramid, group_name, *, cursor, conn):
    cursor.execute(f"INSERT INTO view_member(telegramid, name) VALUES ({telegramid}, '{group_name}')")
    conn.commit()
    return True


# Добавляет группу и её хэш в таблицу team
@handle_database_exceptions
def createGroup(name, first_name, telegramid, *, cursor, conn):
    cursor.execute(f"INSERT INTO view_team(name, first_name, telegramid, hash) VALUES ('{name}', '{first_name}', "
                    f"{telegramid}, '{md5_lower_32bit(name)}')")
    conn.commit()
    return True

@handle_database_exceptions
def get_groups_list_of_user(telegramid, *, cursor):
    cursor.execute(f"SELECT name FROM view_member WHERE telegramid = {telegramid}")
    list_of_users_groups = cursor.fetchall()
    return list_of_users_groups

@handle_database_exceptions
def get_user_list_of_group(name, *, cursor):
    cursor.execute(f"SELECT first_name, telegramid FROM view_member WHERE name = '{name}'")
    user_list_of_group = cursor.fetchall()
    return user_list_of_group

@handle_database_exceptions
def get_Admin_First_Name(group_name, *, cursor):
    cursor.execute(f"SELECT first_name, telegramid FROM view_team WHERE name = '{group_name}'")
    adminId = cursor.fetchone()
    return adminId

@handle_database_exceptions
def getGroupNameFromHash(hash, *, cursor):
    cursor.execute(f"SELECT name FROM team WHERE hash = '{hash}'")
    list_of_users_groups = cursor.fetchone()[0]
    return list_of_users_groups

@handle_database_exceptions
def getFirstnameAndNicknameFromUser(telegramid, *, cursor):
    cursor.execute(f"SELECT first_name, nickname FROM user_info WHERE telegramid = '{telegramid}'")
    list_of_users_groups = cursor.fetchall()
    return list_of_users_groups

@handle_database_exceptions
def existsAdminIdWithId(telegramid, groupname, *, cursor):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_team WHERE telegramid = {telegramid} AND name = '{groupname}')")
    list_of_users_groups = cursor.fetchone()
    return list_of_users_groups

@handle_database_exceptions    
def deleteUserFromAdmin(telegramid, gpoupname, *, cursor, conn):
    cursor.execute(f"DELETE FROM view_member WHERE telegramid = {telegramid} AND name = '{gpoupname}'")
    conn.commit()

@handle_database_exceptions
def deleteGroup(gpoupname, *, cursor, conn):
    cursor.execute(f"DELETE FROM team WHERE name = '{gpoupname}'")
    conn.commit()

@handle_database_exceptions
def existsGroupFromId(telegramid, *, cursor):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM view_member WHERE telegramid = {telegramid})")
    list_of_users_groups = cursor.fetchone()
    return list_of_users_groups

@handle_database_exceptions
def leaveinGroup(telegramid, gpoupname, *, cursor, conn):
    cursor.execute(f"DELETE FROM view_member WHERE telegramid = {telegramid} and name = '{gpoupname}'")
    conn.commit()

@handle_database_exceptions
def totalTimeWithGroup(gpoupname, *, cursor):
    cursor.execute(f"SELECT * FROM find_group_intersections('{gpoupname}')")
    list_of_users_groups = cursor.fetchone()
    return list_of_users_groups

@handle_database_exceptions
def userTime(telegramid, *, cursor):
    cursor.execute(f"SELECT telegramid, freetime FROM view_freetime WHERE telegramid = {telegramid}")
    list_of_users_groups = cursor.fetchone()
    return list_of_users_groups

# Добавление свободного времени пользователя в freetime
@handle_database_exceptions
def insertIntervals(telegramid, freetime, *, conn, cursor):
    cursor.execute(f"INSERT INTO view_freetime(telegramid, freetime) VALUES ({telegramid}, {freetime});")
    conn.commit()

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