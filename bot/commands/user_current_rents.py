import os
from datetime import datetime

import requests
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

rt = Router()

@rt.message(Command('my_active_rents'))
async def my_rents_handler(message: Message):
    rents = requests.get(url=f'{os.getenv("MY_API_BASE")}/user-rents/{message.from_user.id}?status=active').json()
    if rents:
        format_rents = '\n'.join(
            f'{rent["id"]} - '
            f'{rent["steam_account"]["game_name"]} - '
            f'аренда до {datetime.fromisoformat(rent["use_end_datetime"]).strftime("%Y-%m-%d")} - '
            f'{rent["status"]}'
            for rent in rents
        )
        await message.answer(f"Ваши текущие аренды\n\n{format_rents}")
    else:
        await message.answer("На данный момент у вас нет активных аренд")

