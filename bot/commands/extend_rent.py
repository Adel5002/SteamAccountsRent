import json
import os
from datetime import datetime, timedelta, timezone

import requests
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

from utils.release_account import release_account

load_dotenv()

rt = Router()

class Extend(StatesGroup):
    rent_id = State()
    num_of_days = State()

@rt.message(Command('extend_rent'))
async def extend_rent_handler(message: Message, state: FSMContext):
    rents = requests.get(url=f'{os.getenv("MY_API_BASE")}/is-rent-available-for-extend/{message.from_user.id}/').json()
    result = {}
    for item in rents:
        acc_id = item["steam_account"]["id"]
        if acc_id not in result or item["id"] > result[acc_id]["id"]:
            result[acc_id] = item

    if rents:
        format_rents = '\n'.join(
            f'# {rent["id"]} - '
            f'{rent["steam_account"]["game_name"]} #{rent["steam_account"]["id"]} - '
            f'аренда до {datetime.fromisoformat(rent["use_end_datetime"]).strftime("%Y-%m-%d")} - '
            f'{rent["status"]} - '
            f'{"Свободен" if rent["available"] else "Недоступен"}'
            for rent in result.values()
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

    available_ids = {d["id"] for d in rents}

    if message.text.isdigit():
        rent_id = int(message.text)

        if rent_id in available_ids:
            # Находим саму аренду (лучше, чем перебирать в if)
            rent = next((r for r in rents if r["id"] == rent_id), None)

            if rent and rent["available"]:
                await state.update_data(rent_id=rent_id)
                await state.set_state(Extend.num_of_days)
                await message.answer(
                    "Отлично, теперь введите желаемое кол-во дней доп аренды."
                    "(Каждый доп день также 200 руб)"
                )
            else:
                await message.answer("К сожалению эта аренда не доступна в данный момент")
        else:
            await message.answer(
                "Такого id нет в вашей истории аренд, пожалуйста повторите ввод"
            )
    else:
        await message.answer(
            "Вы ввели неопознанное значение, пожалуйста введите число"
        )


@rt.message(Extend.num_of_days)
async def num_of_extend_days(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(num_of_days=message.text)
        data = await state.get_data()

        previous_rent = requests.get(url=f'{os.getenv("MY_API_BASE")}/rents/{data["rent_id"]}').json()
        start_datetime = datetime.fromisoformat(previous_rent['use_end_datetime'])
        end_datetime = start_datetime + timedelta(int(data['num_of_days']))

        await message.answer('Перейдем к оплате')
        # Дальше будет логика по оформлению продления аренды

        update_data = {
            "status": "active",
            "use_start_datetime": str(start_datetime),
            "use_end_datetime": str(end_datetime)
        }

        update_rent_info = requests.patch(
            url=f'{os.getenv("MY_API_BASE")}/update-rent/{data["rent_id"]}',
            data=json.dumps(update_data)
        ).json()

        print(update_rent_info)

        steam_account_login = update_rent_info['steam_account']['login']
        steam_account_password = update_rent_info['steam_account']['password']
        delay_seconds = int((end_datetime - datetime.now()).total_seconds())

        release_account.send_with_options(
            args=(update_rent_info['steam_account']['id'],
                  update_rent_info['id']),
            delay=120 * 1000
        )

        await message.answer(
            f'Оплата прошла успешно ✅\n'
            f'🎉 Ваша аренда готова!\n\n'
            f'👤 Логин: {steam_account_login}\n🔒 Пароль: {steam_account_password}\n'
            f'Аренда будет продлена с {start_datetime.strftime("%Y-%m-%d")} по {end_datetime.strftime("%Y-%m-%d")}'
        )

        await state.clear()
    else:
        await message.answer('Введенное вами значение не является числом, пожалуйста повторите ввод')