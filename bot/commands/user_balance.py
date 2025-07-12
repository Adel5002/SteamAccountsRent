from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

rt = Router()

@rt.message(Command('balance'))
async def balance_handler(message: Message):
    await message.answer("Ваш текущий баланс: ...")