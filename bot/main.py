# bot/main.py

import os
import asyncio
import logging
from datetime import datetime
from typing import NoReturn

from src.config import settings
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import MenuButtonWebApp, WebAppInfo, Message
from aiogram.filters import CommandStart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
)
logger = logging.getLogger(__name__)

# Read configuration from environment
BOT_TOKEN = settings.BOT_TOKEN
if not BOT_TOKEN:
    logger.error("Environment variable BOT_TOKEN is required")
    exit(1)

WEBAPP_URL = settings.WEBAPP_URL
if not WEBAPP_URL:
    logger.error("Environment variable WEBAPP_URL is required")
    exit(1)
print(f"WEBAPP_URL: {WEBAPP_URL}")

async def on_startup(bot: Bot) -> None:
    """
    Called when the bot starts. Here we set up the WebApp menu button
    so that users see it immediately when they open the chat.
    """
    await bot.set_chat_menu_button(menu_button=None) 
    # For private chats (chat_id=None means default)
    await bot.set_chat_menu_button(
        chat_id=None,
        menu_button=MenuButtonWebApp(
            text="🌐 Open Web App",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    logger.info("WebApp menu button configured: %s", WEBAPP_URL)


async def handle_start(message: Message) -> None:
    """
    Handler for /start, just acknowledges the user and reminds
    them to use the WebApp button.
    """
    await message.answer(
        "Welcome! Please use the “Open Web App” button at the bottom\n"
        "to continue in the full interface."
    )


async def main() -> None:
    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register startup hook
    dp.startup.register(on_startup)

    # Register /start handler (optional—WebApp button works without it)
    dp.message.register(handle_start, CommandStart())

    # Start polling
    logger.info("Starting bot polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
