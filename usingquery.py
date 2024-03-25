import connection_pool

if __name__ == "__main__":
    # Получение всех пользователей
    isExist = connection_pool.is_telegramid_exist()
    if not isinstance(isExist, Exception):
        for i in isExist:
            print(i)
    else: print('err')