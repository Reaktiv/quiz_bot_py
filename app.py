import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from utils.notify_admins import bot_start_up, bot_shut_down
from handlers import *

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


dp.include_routers(register_router, start_router)




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(bot_start_up)
    dp.shutdown.register(bot_shut_down)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())