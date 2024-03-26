import data
import psycopg2
import psycopg2.pool

# Класс для пула подключений
class ConnectionPool:
    # Конструктор
    def __init__(self, min_conn, max_conn, **kwargs):
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.conn_params = kwargs
        self.pool = psycopg2.pool.ThreadedConnectionPool(min_conn, max_conn, **kwargs)

    # Достать подключение
    def get_connection(self):
        return self.pool.getconn()

    # Положить подключение
    def put_connection(self, conn):
        self.pool.putconn(conn)

    # Закрыть все подключения
    def close_all_connections(self):
        self.pool.closeall()

# Конфигурация данных для подключения к БД
db_config = {
        'database': data.database,
        'user': data.user,
        'password': data.password,
        'host': data.host,
        'port': data.port
}

# Создание пула подключений
pool = ConnectionPool(min_conn=1, max_conn=10, **db_config)
pool.conn_params