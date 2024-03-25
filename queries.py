# Импортируем объект pool
from connection_pool import pool

# Функция для проверки наличия telegramid в БД
# Пример ее использования в файле usingquery.py
def is_telegramid_exist(pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Пробуем сделать запрос
    try:
        # Проверка наличия telegramid в user_info
        # Select 1 используется, потому что нам первое значение из кортежа, который мы
        # получим после запроса. Если написать просто Select, то мы получим
        # кортеж вида {true}. А с помощью добавочной 1, мы как раз достаем
        # первое значение.
        cursor.execute("SELECT EXISTS(SELECT 1 telegramid FROM user_info WHERE telegramid = '111111111111')")
        users = cursor.fetchone()
        return users
    # Если появилась ошибка, то возвращаем ошибку
    except Exception as e:
        return e
    # Отдаем запрос обратно в пулл
    finally:
        pool.put_connection(conn)