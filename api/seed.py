from datetime import datetime, timedelta
import random
from database.models import User, SteamAccount, Rent
from sqlalchemy.orm import Session

def seed_data(session: Session):
    # Users
    users = [User(username=f"user_{i}") for i in range(1, 6)]
    session.add_all(users)
    session.commit()

    # Steam accounts
    game_names = ["Dota 2", "CS:GO", "GTA V", "Elden Ring", "Minecraft"]

    accounts = [
        SteamAccount(
            login=f"acc{i}",
            password="pass",
            game_name=random.choice(game_names)  # случайная игра
        )
        for i in range(1, 16)
    ]
    session.add_all(accounts)
    session.commit()

    # Rents (привязка user ↔ account)
    # rents = [
    #     Rent(
    #         user_id=users[i % len(users)].id,
    #         steam_account_id=accounts[i % len(accounts)].id,
    #         use_start_datetime=datetime.utcnow(),
    #         use_end_datetime=datetime.utcnow() + timedelta(days=7)
    #     )
    #     for i in range(5)
    # ]
    # session.add_all(rents)
    # session.commit()
