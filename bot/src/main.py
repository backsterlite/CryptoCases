from aiogram import Bot, Dispatcher, types
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN", "dummy_token")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.reply("Welcome to CryptoCases Bot!")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
