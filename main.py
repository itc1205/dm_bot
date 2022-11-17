from dotenv import load_dotenv
import os
import telebot
import random as rand

from telebot import types

from sqlalchemy import desc

from data import db_session
from data.users import User

load_dotenv()

try:
    ADMINS = [
        i.strip() for i in os.getenv("ADMINS").split(",")
    ]  # please write admin names in .env file (like example, example2)
except AttributeError as e:
    print("The .env file is not found!")
    exit(1)


TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode=None)


def winner_message(winner_tg: str) -> str:
    return f"Поздравляем {winner_tg} с его победой!"


def admin_check(user: str) -> bool:
    return user in ADMINS


@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    item1 = types.InlineKeyboardButton("Регистрация")
    item2 = types.InlineKeyboardButton("Условия")
    markup.add(item1)
    markup.add(item2)
    if admin_check(message.from_user.username):
        item3 = types.InlineKeyboardButton("/results")
        markup.add(item3)
        item4 = types.InlineKeyboardButton("/re_elect")
        markup.add(item4)

    bot.reply_to(
        message,
        "Нажми: \nРегистрация - для того что бы зарегестрироваться в конкурсе\n"
        "Условия — для того что бы вывести условия конкурса ",
        reply_markup=markup,
    )


@bot.message_handler(commands=["results"])
def reuslts(message, res=False):
    if admin_check(message.from_user.username):
        db_sess = db_session.create_session()
        winner = db_sess.query(User).filter(User.won == True).first()
        if not winner:
            users = []

            for user in db_sess.query(User):
                users.append(user)

            if len(users) != 0:
                new_winner = rand.choice(users)
                new_winner.won = True
                db_sess.commit()
                bot.reply_to(message, winner_message(
                    new_winner.telegram_username))
            else:
                bot.reply_to(message, "Никто не учавствует в конкурсе")
        else:
            bot.reply_to(message, winner_message(winner.telegram_username))

    else:
        bot.reply_to(
            message, f"Для вас {message.from_user.username} данная функция недоступна"
        )


@bot.message_handler(commands=["re_elect"])
def re_elect(message, res=False):
    if admin_check(message.from_user.username):
        db_sess = db_session.create_session()
        winner = db_sess.query(User).filter(User.won == True).first()

        if winner:
            winner.won = False
            db_sess.commit()

            users = []
            for user in db_sess.query(User):
                users.append(user)
            if len(users) != 0:

                new_winner = rand.choice(users)
                new_winner.won = True
                db_sess.commit()
                bot.reply_to(message, winner_message(winner.telegram_username))
            else:
                bot.reply_to(message, "Никто не учавствует в конкурсе")
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("/results")
            markup.add(item1)
            bot.reply_to(
                message,
                "Победитель не определен. Для определения победителя напишите /results",
                reply_markup=markup,
            )
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
    bot.reply_to(message, answer, reply_markup=None)


def main():
    db_session.global_init("db/mainDB.sqlite")
    bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    main()
