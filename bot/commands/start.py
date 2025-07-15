import json
import os
from xml.dom import ValidationErr

import requests
from aiogram.filters import CommandStart
from aiogram import Router, html
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

load_dotenv()

from start_project import BASE_DIR

rt = Router()

MAX_RETIES = 3

@rt.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    welcome_message = (f"Привет {html.bold(message.from_user.username)} 👋 \n\n"
                      f"Я сервис в котором ты сможешь арендовать аккаунты: Steam, EGS и играть в игры которые ты захочешь! \n")
    photo = FSInputFile(path=os.path.join(BASE_DIR, 'bot/media/Welcome_pic.png'))

    user_data = {'id': message.from_user.id, 'username': message.from_user.username}

    for retry in range(MAX_RETIES + 1):
        try:
            create_user = requests.post(url=f'{os.getenv("MY_API_BASE")}/create-user/', data=json.dumps(user_data))

            if retry == MAX_RETIES:
                raise ValidationErr
            elif create_user.status_code == 200:
                await message.answer_photo(
                    photo=photo,
                    caption=welcome_message
                )
                break
            elif create_user.status_code == 409:
                await message.answer('Вы уже зарегистрированы')
                break
            elif not create_user.status_code == 200:
                continue


        except Exception:
            await message.answer('Ошибка при регистрации, попробуйте чуть позже')
