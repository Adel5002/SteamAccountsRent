from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

rt = Router()

@rt.message(Command('my_rents_history'))
async def my_rents_history_handler(message: Message):
    await message.answer("Здесь будет история ваших аренд.")