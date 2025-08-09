from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from database.models import User, SteamAccount, SteamAccountEmailAddress, SteamAccountStatus


def seed_data(session: Session):
    # Users
    users = [User(username=f"user_{i}") for i in range(1, 6)]
    session.add_all(users)
    session.commit()

    # Game names
    game_names = ["Dota 2", "CS:GO", "GTA V", "Elden Ring", "Minecraft"]

    accounts = []

    for i in range(1, 16):
        # Создаём email-аккаунт
        email = SteamAccountEmailAddress(
            email=f"steam_email_{i}@example.com",
            password="emailpass"
        )

        # Создаём стим-аккаунт и сразу связываем
        account = SteamAccount(
            login=f"acc{i}",
            password="pass",
            game_name=random.choice(game_names),
            status=SteamAccountStatus.preparation,
            steam_account_email_address=email  # ← привязываем объект, не id
        )

        accounts.append(account)

    session.add_all(accounts)
    session.commit()