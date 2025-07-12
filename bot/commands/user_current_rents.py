from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

rt = Router()

@rt.message(Command('my_rents'))
async def my_rents_handler(message: Message):
    await message.answer("Здесь будут ваши активные аренды.")