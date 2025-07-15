import json
import os
from datetime import datetime, timedelta, timezone

import requests
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from dotenv import load_dotenv

from utils.release_account import release_account

load_dotenv()

rt = Router()

class Form(StatesGroup):
    game = State()
    num_of_days = State()
    payment = State()


@rt.inline_query()
async def handle_inline_query(query: types.InlineQuery):
    user_text = query.query.lower()

    games = requests.get(url=f'{os.getenv("MY_API_BASE")}/get-all-games/').json()

    # Фильтрация по тексту
    filtered = [g for g in games if user_text in g.lower()]

    results = [
        types.InlineQueryResultArticle(
            id=str(i),
            title=game,
            input_message_content=types.InputTextMessageContent(message_text=game)
        ) for i, game in enumerate(filtered[:20])  # ограничим 20 результатами
    ]

    await query.answer(results, cache_time=1)


@rt.message(Command('rent'))
async def rent_game(message: Message, state: FSMContext) -> None:
    try:
        response = requests.get(url=f'{os.getenv("MY_API_BASE")}/get-all-games/')
        games = response.json()
    except Exception:
        await message.answer("⚠️ Не удалось получить список игр. Попробуйте позже.")
        return

    if not games:
        await message.answer("📭 Пока что игр нет в каталоге. Попробуйте позже.")
        return

    games_and_accounts = {}

    for game in games:
        try:
            g = requests.get(url=f'{os.getenv("MY_API_BASE")}/get_accounts_by_game_name/{game}').json()
            for elem in g:
                games_and_accounts.setdefault(elem['game_name'].lower(), []).append(elem['id'])
        except Exception:
            continue

    await state.update_data(dict_of_games=games_and_accounts)
    game_list = "\n".join(f"🎮 {game}" for game in games)

    await message.answer(
        "Выберите игру из каталога и напишите её название:\n\n"
        "⚠️ ВНИМАНИЕ! Настоятельно рекомендую вписывать название игр таким способом:\n\n"
        "@BestGamesRentBot имя игры — это позволит вам воспользоваться поиском\n\n"
        f"{game_list}"
    )
    await state.set_state(Form.game)


@rt.message(Form.game)
async def handle_game_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    dict_of_games = data.get("dict_of_games", {})
    user_input = message.text.strip()

    if user_input.lower() in dict_of_games and dict_of_games[user_input.lower()]:
        await state.update_data(game=user_input)
        await state.set_state(Form.num_of_days)
        await message.answer("Отлично! Теперь введите количество дней аренды (1 день = 200₽):")
    else:
        await message.answer("❌ Такой игры нет или все аккаунты заняты. Пожалуйста, введите другое название.")


@rt.message(Form.num_of_days)
async def handle_num_of_rent_days(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data(num_of_days=message.text)
        await state.set_state(Form.payment)
        await message.answer(f'Вы выбрали {message.text} дней аренды')
        await message.answer(f'Перейдем к оплате')
    else:
        await message.answer('🚫 Введенное значение не является числом. Попробуйте снова.')


@rt.message(Form.payment)
async def check_payment(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game = data.get('game')
    num_of_rent_days = data.get("num_of_days")

    try:
        get_accounts = requests.get(
            url=f'{os.getenv("MY_API_BASE")}/get_accounts_by_game_name/{game}'
        ).json()
    except Exception:
        await message.answer("⚠️ Не удалось получить аккаунты. Попробуйте позже.")
        return

    if not get_accounts:
        await message.answer("❌ Все аккаунты по этой игре сейчас заняты. Попробуйте позже.")
        return

    if message.text == "Успешно":
        await state.update_data(payment='successful')
        await message.answer('Оплата прошла успешно ✅\n\nСейчас оформим аренду.')

        try:
            release_date = datetime.now(timezone.utc) + timedelta(int(num_of_rent_days))
            delay_seconds = int((release_date - datetime.now(timezone.utc)).total_seconds())
            steam_account_id = get_accounts[0]['id']


            rent_data = {
                'user_id': message.from_user.id,
                'steam_account_id': steam_account_id,
                'use_end_datetime': str(release_date)
            }

            rent_create = requests.post(
                url=f'{os.getenv("MY_API_BASE")}/create-new-rent/',
                data=json.dumps(rent_data),
            )

            if rent_create.status_code != 200:
                raise Exception(f"Ошибка аренды: {rent_create.text}")

            rent = rent_create.json()

            # запускаем таймер — здесь оставлена заглушка на 2 минуты
            release_account.send_with_options(args=(steam_account_id, rent['id']), delay=120 * 1000)

            await message.answer(
                f'🎉 Ваша аренда готова!\n\n'
                f'👤 Логин: \n🔒 Пароль: \n'
                f'⏳ Время аренды: {num_of_rent_days} дней'
            )
        except Exception as e:
            await message.answer(f"❌ Не удалось создать аренду. Подробности: {str(e)}")
        finally:
            await state.clear()
    else:
        await message.answer("⚠️ Ожидаю подтверждение оплаты. Напишите *Успешно*, когда оплатите.", parse_mode='Markdown')





