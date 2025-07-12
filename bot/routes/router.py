from aiogram import Dispatcher

from commands import (start, list_of_games, add_balance, extend_rent,
                      user_balance, user_current_rents, user_rents_history)

def router(dp: Dispatcher) -> None:
    dp.include_router(start.rt)
    dp.include_router(list_of_games.rt)
    dp.include_router(add_balance.rt)
    dp.include_router(extend_rent.rt)
    dp.include_router(user_balance.rt)
    dp.include_router(user_current_rents.rt)
    dp.include_router(user_rents_history.rt)