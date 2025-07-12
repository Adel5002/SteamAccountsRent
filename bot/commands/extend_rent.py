from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

rt = Router()

@rt.message(Command('extend_rent'))
async def extend_rent_handler(message: Message):
    await message.answer("Здесь вы сможете продлить аренду.")