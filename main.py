from dotenv import load_dotenv
import os
import telebot
import random as rand

from telebot import types

from sqlalchemy import desc

from data import db_session
from data.users import User

load_dotenv()

ADMINS = [
    i.strip() for i in os.getenv("ADMINS").split(",")
]  # please write admin names in env settings like (example, example2)

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode=None)


def admin_check(user: str) -> bool:
    return user in ADMINS


@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Регистрация")
    item2 = types.KeyboardButton("Условия")
    markup.add(item1)
    markup.add(item2)
    bot.reply_to(
        message,
        "Нажми: \nРегистрация - для того что бы зарегестрироваться в конкурсе\nУсловия — для того что бы вывести условия конкурса ",
        reply_markup=markup,
    )


@bot.message_handler(commands=["results"])
def reuslts(message, res=False):
    if admin_check(message.from_user.username):
        db_sess = db_session.create_session()
        winner = db_sess.query(User).filter(User.won).first()
        if not winner:
            users = []
            for user in db_sess.query(User):
                users.append(user.telegram_username)
            winner = rand.choice(users)
            winner.won = True
        bot.reply_to(message, winner)

    else:
        bot.reply_to(
            message, f"Для вас {message.from_user.username} данная функция недоступна"
        )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    answer = "Команда не распознана"
    if message.text.strip() == "Регистрация":
        db_sess = db_session.create_session()
        if (
            db_sess.query(User)
            .filter(User.telegram_username == f"@{message.from_user.username}")
            .first()
        ):
            answer = "Уже зарегестрирован"
        else:
            user = User()
            user.telegram_username = f"@{message.from_user.username}"
            db_sess.add(user)
            db_sess.commit()
            answer = "Успешно зарегестрирован!"
    elif message.text.strip() == "Условия":
        answer = "Условия конкурса"
    bot.reply_to(message, answer)


def main():
    db_session.global_init("db/mainDB.sqlite")
    bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    main()
