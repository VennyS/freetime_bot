import data
import telebot
import psycopg2

bot = telebot.TeleBot(data.token)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, f"Привет, я бот для определения общего времени для группы людей.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, f"Я помогу Вам с подбором общего времени с Вашими друзьями/коллегами/знакомыми, с кем бы то ни было. Для Вас есть возможность вступить в какую-либо группу, если Вы знаете ее название и пароль, или создать новую. После этого, Вам и вашим единомышленикам в индивидуальном порядке будет необходимо ввести даты и временные интервалы, которые Вы можете посвятитить друг другу. А далее я предоставлю вам интервалы, которые совпали у всех для того, чтобы Вы могли организовать встречу.")

# def register(telegramid):


def execute_query(message):
    try:
        connection = psycopg2.connect(user=data.user,
                                    password=data.password,
                                    host = data.host,
                                    port = data.port,
                                    database = data.database)
        cursor = connection.cursor()
        # records = method(cursor)
        cursor.execute("SELECT * FROM view_joined_groups")
        records = cursor.fetchall()
    except (Exception, psycopg2.Error):
        bot.reply_to(message, "Произошла непредвиденная ошибка. Попробуйте ещё раз.")
        return 0
    finally:
        if connection:
            connection.close()
            return records


bot.infinity_polling()