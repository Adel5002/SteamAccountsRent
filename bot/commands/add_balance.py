from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

rt = Router()

@rt.message(Command('add_balance'))
async def add_balance_handler(message: Message):
    await message.answer("Скоро здесь появится возможность пополнить баланс.")