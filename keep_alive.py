from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)

@app.route('/')
def home():
    logging.info("🔁 GET-запрос на / — всё работает!")
    return "Бот активен!"

def run():
    logging.info("🚀 Запуск Flask-сервера на порту 8080...")
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    logging.info("⏳ Инициализация потока Flask-сервера...")
    t = Thread(target=run)
    t.start()
