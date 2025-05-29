import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F
import asyncio
import requests
import json
from config import BOT_TOKEN, OPENROUTER_API_KEY

bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

context = []

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Привет! Я AI-помощник. Просто задай вопрос!")

@dp.message(Command("reset"))
async def reset_cmd(message: Message):
    context.clear()
    await message.answer("🔄 Контекст сброшен. Можем начать сначала.")

@dp.message(F.text)
async def handle_message(message: Message):
    user_message = message.text
    context.append({"role": "user", "content": user_message})
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "qwen/qwen3-30b-a3b:free",
            "messages": context
        })
    )
    if response.status_code == 200:
        assistant_reply = response.json()["choices"][0]["message"]["content"]
        context.append({"role": "assistant", "content": assistant_reply})
        await message.answer(assistant_reply)
    else:
        await message.answer("⚠️ Ошибка при обращении к API.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
