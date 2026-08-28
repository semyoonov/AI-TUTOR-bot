#тут бот (может еще сайт напишем, но не факт)
#тут хватит одного файла это просто обычный бот в тг будет он будет брать все функции из других папок по большей части

print("=== BOT.PY НАЧАЛ РАБОТУ ===", flush=True)
import logging
logging.basicConfig(level=logging.INFO)

import asyncio
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from config import TG_TOKEN
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/chat")

@dp.message(Command("start"))
async def start(message : types.Message):
    await message.answer("Бот запущен. Что изучаем сегодня?")

@dp.message()
async def handle_message(message : types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(API_URL, json={"user_id" : message.from_user.id, "message" : message.text})
            await message.answer(res.json())
    except Exception as e:
        print(f"Ошибка API: {e}")
        await message.answer("Произошла ошибка. Попробуй позже.")

async def main():
    print("--- Бот успешно запущен и готов к работе ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())