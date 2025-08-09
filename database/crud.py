from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import Sequence

from sqlmodel import Session, select

from database.models import UserCreate, User, SteamAccountCreate, SteamAccount, RentCreate, Rent, RentUpdate, \
    SteamAccountUpdate, UserUpdate, PaymentCreate, Payment, PaymentUpdate, SteamAccountEmailAddressCreate, \
    SteamAccountEmailAddress, SteamAccountEmailAddressUpdate


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

def add_steam_account_email_address(account: SteamAccountEmailAddressCreate, session: Session) -> SteamAccountEmailAddress:
    new_account = SteamAccountEmailAddress(
        email=account.email,
        password=account.password
    )

    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    return new_account

def update_steam_account_email_address(
        account_id: int,
        account: SteamAccountEmailAddressUpdate,
        session: Session
) -> SteamAccountEmailAddress:
    get_account = session.get(SteamAccountEmailAddress, account_id)

    if not get_account:
        raise HTTPException(status_code=404, detail='Account does not exists...')

    account_data_update = account.model_dump(exclude_unset=True)
    get_account.sqlmodel_update(account_data_update)

    session.add(get_account)
    session.commit()
    session.refresh(get_account)

    return get_account


def delete_steam_account_email_address(
        account_id: int,
        session: Session
) -> SteamAccountEmailAddress:
    get_account = session.get(SteamAccountEmailAddress, account_id)

    if not get_account:
        raise HTTPException(status_code=404, detail='Account does not exists...')

    session.delete(get_account)
    session.commit()


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
        game_name=account.game_name,
        steam_account_email_address_id=account.steam_account_email_address_id
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


def get_all_accounts_by_game_name(game: str, session: Session) -> Sequence[SteamAccount]:
    accounts = session.scalars(
        select(SteamAccount)
        .where(SteamAccount.game_name == game)
        .where(SteamAccount.in_use == False)
        .where(SteamAccount.status == 'active')
    ).all()

    if not accounts:
        raise HTTPException(status_code=404, detail='Game does not exists')

    return accounts

# --- RENT ---

def new_rent_create(rent: RentCreate, session: Session) -> Rent:
    account_has_active_rent = session.scalars(
        select(Rent)
        .where(Rent.steam_account_id == rent.steam_account_id)
        .where(Rent.status == 'active')
    ).all()

    rent_exists = session.scalar(
        select(Rent)
        .where(Rent.user_id == rent.user_id)
        .where(Rent.steam_account_id == rent.steam_account_id)
        .where(Rent.status == 'active')
    )

    user_exists = session.get(User, rent.user_id)

    steam_account_exists = session.get(SteamAccount, rent.steam_account_id)

    if account_has_active_rent:
        raise HTTPException(
            status_code=409,
            detail='Account already have active rent. You cannot rent account with already active rent'
        )
    elif rent_exists:
        raise HTTPException(status_code=409, detail='You cannot rent the same account twice')
    elif not user_exists:
        raise HTTPException(status_code=404, detail='User does not exists')
    elif not steam_account_exists:
        raise HTTPException(status_code=404, detail='Specified steam account does not exists')


    new_rent = Rent(
        user_id=rent.user_id,
        steam_account_id=rent.steam_account_id,
        use_start_datetime=datetime.now(timezone.utc),
        use_end_datetime=rent.use_end_datetime
    )

    session.add(new_rent)
    session.commit()
    session.refresh(new_rent)

    steam_acc_update = SteamAccountUpdate(
        in_use=True,
    )

    update_steam_account(rent.steam_account_id, steam_acc_update, session)

    return new_rent

def update_rent(rent_id: int, rent_data: RentUpdate, session: Session) -> Rent:
    db_rent = session.get(Rent, rent_id)

    if rent_data.user_id and rent_data.steam_account_id:
        user_exists = session.get(User, rent_data.user_id)

        steam_account_exists = session.get(SteamAccount, rent_data.steam_account_id)

        if not user_exists:
            raise HTTPException(status_code=404, detail='User does not exists')
        elif not steam_account_exists:
            raise HTTPException(status_code=404, detail='Specified steam account does not exists')

    if not db_rent:
        raise HTTPException(status_code=404, detail="Rent not found")


    rent_data_update = rent_data.model_dump(exclude_unset=True)
    db_rent.sqlmodel_update(rent_data_update)
    session.add(db_rent)
    session.commit()
    session.refresh(db_rent)

    if rent_data.status == "active":
        update_steam_account(db_rent.steam_account_id, SteamAccountUpdate(in_use=True), session)

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


# --- PAYMENT ---

def create_payment(payment: PaymentCreate, session: Session) -> Payment:
    user_exists = session.get(User, payment.user_id)
    steam_account = session.get(SteamAccount, payment.steam_account_id)

    if not user_exists:
        raise HTTPException(status_code=404, detail='User does not exists')
    elif not steam_account:
        raise HTTPException(status_code=404, detail='Provided account id does not exists')

    new_payment = Payment(
        user_id=payment.user_id,
        steam_account_id=payment.steam_account_id,
        sum=payment.sum
    )

    session.add(new_payment)
    session.commit()
    session.refresh(new_payment)

    return new_payment

def update_payment(payment_id: int, payment: PaymentUpdate, session: Session) -> Payment:
    get_payment = session.get(Payment, payment_id)

    if not get_payment:
        raise HTTPException(status_code=404, detail='Payment does not exists')

    payment_data = payment.model_dump(exclude_unset=True)
    get_payment.sqlmodel_update(payment_data)

    session.add(get_payment)
    session.commit()
    session.refresh(get_payment)

    return get_payment

def delete_payment(payment_id: int, session: Session) -> None:
    get_payment = session.get(Payment, payment_id)

    if not get_payment:
        raise HTTPException(status_code=404, detail='Provided payment id not found')

    session.delete(payment_id)
    session.commit()

def get_payment(payment_id: int, session: Session) -> Payment:
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail='Provided payment id not found')

    return payment


def get_all_payments(session: Session) -> Sequence[Payment]:
    payments = session.scalars(select(Payment)).all()
    return payments