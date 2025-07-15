import os
from datetime import datetime, timedelta

import requests
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
load_dotenv()

rt = Router()

class Extend(StatesGroup):
    rent_id = State()
    num_of_days = State()

@rt.message(Command('extend_rent'))
async def extend_rent_handler(message: Message, state: FSMContext):
    rents = requests.get(url=f'{os.getenv("MY_API_BASE")}/is-rent-available-for-extend/{message.from_user.id}/').json()
    if rents:

        format_rents = '\n'.join(
            f'id {rent["id"]} - '
            f'{rent["steam_account"]["game_name"]} - '
            f'аренда до {datetime.fromisoformat(rent["use_end_datetime"]).strftime("%Y-%m-%d")} - '
            f'{rent["status"]} - '
            f'{"Свободен" if rent["available"] else "Недоступен"}'
            for rent in rents
        )
        await message.answer(f"Все ваши аренды. Помните что если вы хотите продлить уже истекшую аренду что она может быть занята уже другим человеком \n\n"
                             f"{format_rents}\n\n"
                             f"Выберите одну из списка, скиньте в чат ее id")

        await state.set_state(Extend.rent_id)
    else:
        await message.answer(f"У вас еще не было аренд")

@rt.message(Extend.rent_id)
async def get_rent_id(message: Message, state: FSMContext):
    rents = requests.get(url=f'{os.getenv("MY_API_BASE")}/is-rent-available-for-extend/{message.from_user.id}/').json()

    for rent in rents:
        if message.text.isdigit() and int(message.text) == rent['id']:
            if rent['available']:
                await state.update_data(rent_id=message.text)
                await state.set_state(Extend.num_of_days)
                await message.answer(
                    'Отлично, теперь введите желаемое кол-во дней доп аренды.(Каждый доп день также 200 руб)')
            else:
                await message.answer('К сожалению эта аренда не доступна в данный момент')
        else:
            await message.answer(
                'Вы ввели неопознанное значение или такого id нет в вашей истории аренд, пожалуйста повторите ввод')


@rt.message(Extend.num_of_days)
async def num_of_extend_days(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(num_of_days=message.text)
        data = await state.get_data()

        previous_rent = requests.get(url=f'{os.getenv("MY_API_BASE")}/rents/{data["rent_id"]}').json()
        start_datetime = datetime.fromisoformat(previous_rent['use_end_datetime'])
        end_datetime = start_datetime + timedelta(int(data['num_of_days']))


        await message.answer('Перейдем к оплате')
        # Сначала будет логика по оформлению оплаты
        # Дальше будет логика по оформлению продления аренды

        await message.answer(
            f'Оплата прошла успешно ✅\n'
            f'Аренда будет продлена с {start_datetime.strftime("%Y-%m-%d")} по {end_datetime.strftime("%Y-%m-%d")}'
        )

        await state.clear()
    else:
        await message.answer('Введенное вами значение не является числом, пожалуйста повторите ввод')