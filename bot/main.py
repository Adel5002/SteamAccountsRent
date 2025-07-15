import asyncio
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aiogram import Dispatcher

from bot import bot
from commands.commands_list import commands
from routes.router import router

dp = Dispatcher()

async def main() -> None:
    router(dp)
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())