import os

import requests
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from dotenv import load_dotenv

load_dotenv()

rt = Router()

@rt.message(Command('balance'))
async def balance_handler(message: Message):
    get_balance = requests.get(url=f"{os.getenv('MY_API_BASE')}/users/{message.from_user.id}/").json()
    await message.answer(f"Ваш текущий баланс: {get_balance['balance']} Р")