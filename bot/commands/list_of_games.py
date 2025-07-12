from aiogram.filters import  Command
from aiogram import Router
from aiogram.types import Message

rt = Router()

@rt.message(Command('games'))
async def command_start_handler(message: Message) -> None:
    await message.answer('Здесь будет каталог...')