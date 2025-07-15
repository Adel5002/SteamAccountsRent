import dramatiq
from dramatiq.brokers.redis import RedisBroker
from sqlmodel import Session

from database.crud import update_steam_account, update_rent
from database.models import SteamAccountUpdate, RentUpdate

redis_broker = RedisBroker(url="redis://redis:6379")
dramatiq.set_broker(redis_broker)

@dramatiq.actor
def release_account(account_id: int, rent_id: int):
    from database.engine import engine
    with Session(engine) as session:
        update_rent(rent_id, RentUpdate(status='ended'), session)
        update_steam_account(account_id, SteamAccountUpdate(in_use=False), session)

        # Здесь будет запускаться функция по смене пароля
        print(f"[OK] Аккаунт {account_id} освобождён")
