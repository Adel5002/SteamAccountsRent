import asyncio
import logging
import sys

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