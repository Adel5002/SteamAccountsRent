import dramatiq
from dramatiq.brokers.redis import RedisBroker
from sqlmodel import Session
from fastapi import HTTPException

from database.crud import update_steam_account, update_rent
from database.models import SteamAccountUpdate, RentUpdate

redis_broker = RedisBroker(url="redis://redis:6379")
dramatiq.set_broker(redis_broker)

@dramatiq.actor(max_retries=0)
def release_account(account_id: int, rent_id: int):
    from database.engine import engine

    with Session(engine) as session:
        try:
            update_rent(rent_id, RentUpdate(status='ended'), session)
            update_steam_account(account_id, SteamAccountUpdate(in_use=False), session)
            print(f"[OK] Аккаунт {account_id} освобождён")
        except HTTPException as e:
            if e.status_code == 404:
                print(f"[SKIP] Rent {rent_id} не найдена (404). Таска завершена.")
                return
            raise
        except Exception as e:
            print(f"[ERROR] release_account({account_id}, {rent_id}): {e}")
            raise
