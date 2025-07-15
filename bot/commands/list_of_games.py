import os

import requests
from aiogram.filters import  Command
from aiogram import Router, html
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

rt = Router()

@rt.message(Command('games'))
async def command_start_handler(message: Message) -> None:
    games = requests.get(url=f'{os.getenv("MY_API_BASE")}/get-all-games/').json()

    games_and_accounts = {}

    for game in games:
        g = requests.get(url=f'{os.getenv("MY_API_BASE")}/get_accounts_by_game_name/{game}').json()
        for elem in g:
            games_and_accounts.setdefault(elem['game_name'], []).append(elem['id'])

    print(games_and_accounts)

    format_games = '\n'.join(f'{k} - Доступные аккаунты {len(v)}' for k, v in games_and_accounts.items())

    await message.answer(
        f'Каталог игр:\n\n'
        f'{format_games}\n\n'
        f'Вы можете выбрать игру если есть свободные аккаунты. Просто напишите /rent потом название игры и отправьте в чат'
    )