import os

from aiogram.filters import CommandStart
from aiogram import Router, html
from aiogram.types import Message, FSInputFile

from start_project import BASE_DIR

rt = Router()

@rt.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    welcome_message = (f"Привет {html.bold(message.from_user.username)} 👋 \n\n"
                      f"Я сервис в котором ты сможешь арендовать аккаунты: Steam, EGS и играть в игры которые ты захочешь! \n")
    photo = FSInputFile(path=os.path.join(BASE_DIR, 'bot/media/Welcome_pic.png'))
    await message.answer_photo(
        photo=photo,
        caption=welcome_message
    )