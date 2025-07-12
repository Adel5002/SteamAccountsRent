from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import Sequence

from sqlmodel import Session, select

from database.models import UserCreate, User, SteamAccountCreate, SteamAccount, RentCreate, Rent, RentUpdate, \
    SteamAccountUpdate, UserUpdate


# --- USER ---

def create_user(user: UserCreate, session: Session) -> User:
    user_exists = session.get(User, user.id)

    if user_exists:
        raise HTTPException(status_code=409, detail='User with this id already exists')

    user_create = User(
        id=user.id,
        username=user.username
    )

    session.add(user_create)
    session.commit()
    session.refresh(user_create)

    return user_create

def update_user(user_id: int, user_data: UserUpdate, session: Session) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data_update = user_data.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data_update)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def delete_user(user_id: int, session: Session) -> None:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()

def get_user(user_id: int, session: Session) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_all_users(session: Session) -> Sequence[User]:
    return session.scalars(select(User)).all()


# --- STEAM ACCOUNT ---

def add_new_steam_account(account: SteamAccountCreate, session: Session) -> SteamAccount:
    account_exists = session.scalar(
        select(SteamAccount)
        .where(SteamAccount.login == account.login)
        .where(SteamAccount.game_name == account.game_name)
    )

    if account_exists:
        raise HTTPException(status_code=409, detail='Account with these credential already exists!')

    add_account = SteamAccount(
        login=account.login,
        password=account.password,
        game_name=account.game_name
    )

    session.add(add_account)
    session.commit()
    session.refresh(add_account)

    return add_account

def update_steam_account(account_id: int, account_data: SteamAccountUpdate, session: Session) -> SteamAccount:
    db_account = session.get(SteamAccount, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Steam account not found")

    account_data_update = account_data.model_dump(exclude_unset=True)
    db_account.sqlmodel_update(account_data_update)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account

def delete_steam_account(account_id: int, session: Session) -> None:
    db_account = session.get(SteamAccount, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Steam account not found")

    session.delete(db_account)
    session.commit()

def get_steam_account(account_id: int, session: Session) -> SteamAccount:
    account = session.get(SteamAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Steam account not found")
    return account

def get_all_steam_accounts(session: Session) -> Sequence[SteamAccount]:
    return session.scalars(select(SteamAccount)).all()


# --- RENT ---

def new_rent_create(rent: RentCreate, session: Session) -> Rent:
    rent_exists = session.scalar(
        select(Rent)
        .where(Rent.user_id == rent.user_id)
        .where(Rent.steam_account_id == rent.steam_account_id)
    )

    user_exists = session.get(User, rent.user_id)

    steam_account_exists = session.get(SteamAccount, rent.steam_account_id)

    if rent_exists:
        raise HTTPException(status_code=409, detail='You cannot rent the same account twice')
    elif not user_exists:
        raise HTTPException(status_code=404, detail='User does not exists')
    elif not steam_account_exists:
        raise HTTPException(status_code=404, detail='Specified steam account does not exists')

    new_rent = Rent(
        user_id=rent.user_id,
        steam_account_id=rent.steam_account_id,
        use_start_datetime=datetime.today(),
        use_end_datetime=rent.use_end_datetime
    )

    session.add(new_rent)
    session.commit()
    session.refresh(new_rent)

    return new_rent

def update_rent(rent_id: int, rent_data: RentUpdate, session: Session) -> Rent:
    db_rent = session.get(Rent, rent_id)

    user_exists = session.get(User, rent_data.user_id)

    steam_account_exists = session.get(SteamAccount, rent_data.steam_account_id)

    if not db_rent:
        raise HTTPException(status_code=404, detail="Rent not found")
    elif not user_exists:
        raise HTTPException(status_code=404, detail='User does not exists')
    elif not steam_account_exists:
        raise HTTPException(status_code=404, detail='Specified steam account does not exists')

    rent_data_update = rent_data.model_dump(exclude_unset=True)
    db_rent.sqlmodel_update(rent_data_update)
    session.add(db_rent)
    session.commit()
    session.refresh(db_rent)

    return db_rent

def delete_rent(rent_id: int, session: Session) -> None:
    db_rent = session.get(Rent, rent_id)
    if not db_rent:
        raise HTTPException(status_code=404, detail="Rent not found")

    session.delete(db_rent)
    session.commit()


def get_rent(rent_id: int, session: Session) -> Rent:
    rent = session.get(Rent, rent_id)
    if not rent:
        raise HTTPException(status_code=404, detail="Rent not found")
    return rent

def get_all_rents(session: Session) -> Sequence[Rent]:
    return session.scalars(select(Rent)).all()