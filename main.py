import json
import telebot
import openai
from config import *


# Создание экземпляра бота
bot = telebot.TeleBot(telegram_token)

# Установка токена GPT-3
openai.api_key = openai_token

# Функция для отправки запроса модели GPT-3
def  json_to_history(id):
    with open("history.json", "r") as f:
        hist_all: dict = json.load(f)
    return hist_all.get(id, "")

def save_json(id, request, response):
    with open("history.json", "r") as f:
        hist_all: dict = json.load(f)
    with open("history.json", "w") as f:
        if id in hist_all.keys():
            hist_all[id] += f"\nuser: {request}\ngpt: {response}"
        else:
            hist_all[id] = f"\nuser: {request}\ngpt: {response}"
        json.dump(hist_all, f)

def send_to_gpt3(message:telebot.types.Message):
    # Сохранение сообщения пользователя в истории чата
    history = json_to_history(message.from_user.id)
    # Отправка запроса модели GPT-3
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=history + "\n" + message.text + "\n",
        max_tokens=700,
        temperature=0.1,
        n=1,
        stop=None,
    )

    # Получение ответа модели GPT-3
    gpt3_reply = response.choices[0].text

    # Сохранение ответа модели в истории чата
    save_json(message.from_user.id, message.text, gpt3_reply)

    return gpt3_reply

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, 'Привет! Я бот, основанный на GPT-3. Введите сообщение, чтобы начать общение.')

# Обработчик всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"сообщение: {message.text}")
    # Отправка запроса модели GPT-3
    reply = send_to_gpt3(message)

    # Отправка ответа пользователя в чат
    bot.reply_to(message, reply)
    print(f"ответ: {reply}")

# Запуск бота
bot.polling()