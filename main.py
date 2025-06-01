import os
import logging
from datetime import datetime
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from pytz import timezone
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("TOKEN")
scheduler = BackgroundScheduler()

daily_data = {
    1: {"fact": "1 июня — Международный день защиты детей 🌍👶"},
    2: {"fact": "2 июня 1953 — коронация королевы Елизаветы II 👑"},
    3: {"fact": "3 июня 1965 — первый выход американца в открытый космос 🚀"},
    4: {"fact": "4 июня — День рождения Ангелы Меркель 🇩🇪"},
    5: {"fact": "5 июня — Всемирный день охраны окружающей среды 🌱"},
    6: {"fact": "6 июня — Пушкинский день России ✍️"},
    7: {"fact": "7 июня 1494 — подписание Тордесильясского договора 🗺️"},
    8: {"fact": "8 июня — Всемирный день океанов 🌊"},
    9: {"fact": "9 июня — Международный день друзей 🤝"},
    10: {"fact": "10 июня 1829 — день рождения химика Александра Бутлерова ⚗️"},
    11: {"fact": "11 июня — День архитектуры в России 🏛️"},
    12: {"fact": "12 июня — День России 🇷🇺"},
    13: {"fact": "13 июня 1895 — открытие национального парка Банф в Канаде 🏞️"},
    14: {"fact": "14 июня — Всемирный день донора крови 💉"},
    15: {"fact": "15 июня 1215 — подписание Великой хартии вольностей 📜"},
    16: {"fact": "16 июня 1963 — первая женщина в космосе Валентина Терешкова 👩‍🚀"},
    17: {"fact": "17 июня — Всемирный день борьбы с опустыниванием 🌵"},
    18: {"fact": "18 июня — День устойчивой гастрономии 🌽"},
    19: {"fact": "19 июня — День создания Вены как города 🏙️"},
    20: {"fact": "20 июня — Всемирный день беженцев 🌍"},
    21: {"fact": "21 июня — летнее солнцестояние, самый длинный день в году ☀️"},
    22: {"fact": "🎉 Сегодня день рождения Данила! Поздравляем его! 🎂🎈"},
}

def send_birthday_countdown(bot: Bot, chat_id: int):
    today = datetime.now().date()
    bday = datetime(2025, 6, 22).date()
    if today.month == 6 and 1 <= today.day <= 22:
        days_left = (bday - today).days
        data = daily_data.get(today.day)
        if data:
            text = data["fact"] if days_left == 0 else f"До дня рождения Данила осталось {days_left} дней!\n\n{data['fact']}"
            bot.send_message(chat_id=chat_id, text=text)

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name or "друг"
    keyboard = [["📆 Осталось дней"], ["🎁 Интересный факт"], ["⛔ Стоп"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(f"👋 Привет, {user}! Я буду каждый день напоминать сколько осталось до дня рождения Данила 🎉", reply_markup=reply_markup)
    job_id = f"bday_{chat_id}"
    if scheduler.get_job(job_id):
        update.message.reply_text("🔁 Уже активировано!")
        return
    scheduler.add_job(
        send_birthday_countdown,
        trigger=CronTrigger(hour=12, minute=0, timezone=timezone("Europe/Moscow")),
        args=[context.bot, chat_id],
        id=job_id,
        replace_existing=True
    )
    update.message.reply_text("✅ Я буду писать тебе каждый день в 12:00!")

def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    job_id = f"bday_{chat_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        update.message.reply_text("⛔ Напоминания отключены.")
    else:
        update.message.reply_text("📥 У тебя и так не было активных напоминаний.")

def days_left(update: Update, context: CallbackContext):
    today = datetime.now().date()
    bday = datetime(2025, 6, 22).date()
    days = (bday - today).days
    if today > bday:
        update.message.reply_text("🎉 День рождения уже прошёл!")
    elif days == 0:
        update.message.reply_text("🎂 Сегодня день рождения Данила!")
    else:
        update.message.reply_text(f"⏳ Осталось {days} дней до дня рождения Данила.")

def fact(update: Update, context: CallbackContext):
    today = datetime.now().date()
    data = daily_data.get(today.day)
    if data:
        update.message.reply_text(data["fact"])
    else:
        update.message.reply_text("😞 Сегодня нет интересного факта.")

def handle_buttons(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "📆 Осталось дней":
        days_left(update, context)
    elif text == "🎁 Интересный факт":
        fact(update, context)
    elif text == "⛔ Стоп":
        stop(update, context)

def main():
    logging.basicConfig(level=logging.INFO)
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("days", days_left))
    dp.add_handler(CommandHandler("fact", fact))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons))

    updater.bot.set_my_commands([
        ("start", "Запустить напоминания"),
        ("stop", "Остановить напоминания"),
        ("days", "Сколько осталось дней"),
        ("fact", "Факт дня")
    ])

    scheduler.start()
    keep_alive()
    updater.start_polling()
    logging.info("🚀 Бот запущен...")
    updater.idle()

if __name__ == '__main__':
    main()
