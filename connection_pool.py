import data
import psycopg2
import psycopg2.pool

class ConnectionPool:
    def __init__(self, min_conn, max_conn, **kwargs):
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.conn_params = kwargs
        self.pool = psycopg2.pool.ThreadedConnectionPool(min_conn, max_conn, **kwargs)

    def get_connection(self):
        return self.pool.getconn()

    def put_connection(self, conn):
        self.pool.putconn(conn)

    def close_all_connections(self):
        self.pool.closeall()

db_config = {
        'database': data.database,
        'user': data.user,
        'password': data.password,
        'host': data.host,
        'port': data.port
}

# Создание пула подключений
pool = ConnectionPool(min_conn=1, max_conn=10, **db_config)

# Функция для проверки наличия telegramid в БД
# Пример ее использования в файле usingquery.py
def is_telegramid_exist(pool = pool):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        # Проверка наличия telegramid в user_info
        # Select 1 используется, потому что нам первое значение из кортежа, который мы
        # получим после запроса. Если написать просто Select, то мы получим
        # кортеж вида {true}. А с помощью добавочной 1, мы как раз достаем
        # первое значение.
        cursor.execute("SELECT EXISTS(SELECT 1 telegramid FROM user_info WHERE telegramid = '111111111111')")
        users = cursor.fetchone()
        return users
    except Exception as e:
        return e
    finally:
        pool.put_connection(conn)