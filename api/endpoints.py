from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, Session, select
from sqlalchemy import text, Sequence

from api.seed import seed_data
from database.crud import create_user, add_new_steam_account, new_rent_create, delete_user, update_user, \
    update_steam_account, delete_steam_account, update_rent, delete_rent, get_all_users, get_user, \
    get_all_steam_accounts, get_steam_account, get_all_rents, get_rent, create_payment, update_payment, delete_payment, \
    get_payment, get_all_payments, get_all_accounts_by_game_name, add_steam_account_email_address, \
    update_steam_account_email_address
from database.engine import create_db_and_tables, SessionDep, engine, get_session
from database.models import UserRead, UserCreate, User, SteamAccountCreate, SteamAccountRead, SteamAccount, RentRead, \
    RentCreate, Rent, RentUpdate, SteamAccountUpdate, UserUpdate, PaymentRead, PaymentCreate, Payment, PaymentUpdate, \
    SteamAccountEmailAddressRead, SteamAccountEmailAddressCreate, SteamAccountEmailAddress, \
    SteamAccountEmailAddressUpdate


def reset_db(engine):
    with engine.connect() as connection:
        # Отключаем ограничения внешних ключей
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
        connection.commit()
    SQLModel.metadata.create_all(engine)

def run():
    reset_db(engine)
    with Session(engine) as session:
        seed_data(session)

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    create_db_and_tables()
    # run()
    yield

app = FastAPI(lifespan=lifespan)


# --- USER ---

@app.post('/create-user/', response_model=UserRead)
async def create_user_endpoint(user: UserCreate, session: SessionDep) -> User:
    new_user = create_user(user, session)
    return new_user

@app.patch('/update-user/{user_id}', response_model=UserRead)
async def update_user_endpoint(user_id: int, user: UserUpdate, session: SessionDep):
    return update_user(user_id, user, session)

@app.delete('/delete-user/{user_id}')
async def delete_user_endpoint(user_id: int, session: SessionDep):
    delete_user(user_id, session)
    return {"detail": "User deleted successfully"}

@app.get('/users/', response_model=list[UserRead])
async def read_all_users(session: SessionDep):
    return get_all_users(session)

@app.get('/users/{user_id}', response_model=UserRead)
async def read_user(user_id: int, session: SessionDep):
    return get_user(user_id, session)


# --- STEAM ACCOUNT ---

@app.post('/add-steam-account-email-address/', response_model=SteamAccountEmailAddressRead)
async def add_steam_acc_email_add(
        account: SteamAccountEmailAddressCreate,
        session: SessionDep
) -> SteamAccountEmailAddress:
    email = add_steam_account_email_address(account, session)
    return email

@app.patch('/update-steam-account-email-address/{account_id}', response_model=SteamAccountEmailAddressRead)
async def update_steam_acc_email_add(
        account_id: int,
        account: SteamAccountEmailAddressUpdate,
        session: SessionDep
) -> SteamAccountEmailAddress:
    update_email = update_steam_account_email_address(account_id, account, session)
    return update_email

@app.post('/add-new-account/', response_model=SteamAccountRead)
async def add_new_account_endpoint(account: SteamAccountCreate, session: SessionDep) -> SteamAccount:
    new_account = add_new_steam_account(account, session)
    return new_account

@app.patch('/update-account/{account_id}', response_model=SteamAccountRead)
async def update_steam_account_endpoint(account_id: int, account: SteamAccountUpdate, session: SessionDep):
    return update_steam_account(account_id, account, session)

@app.delete('/delete-account/{account_id}')
async def delete_steam_account_endpoint(account_id: int, session: SessionDep):
    delete_steam_account(account_id, session)
    return {"detail": "Steam account deleted successfully"}

@app.get('/accounts/', response_model=list[SteamAccountRead])
async def read_all_accounts(session: SessionDep):
    return get_all_steam_accounts(session)

@app.get('/accounts/{account_id}', response_model=SteamAccountRead)
async def read_account(account_id: int, session: SessionDep):
    return get_steam_account(account_id, session)

@app.get('/get_accounts_by_game_name/{game}', response_model=list[SteamAccountRead])
async def get_accounts_by_game_name(game: str, session: SessionDep) -> Sequence[SteamAccount]:
    accounts = get_all_accounts_by_game_name(game, session)

    return accounts

@app.get('/get-all-games/')
async def get_all_games(session: SessionDep) -> list:
    get_all_account = session.scalars(
        select(SteamAccount)
        .where(SteamAccount.in_use == False)
        .where(SteamAccount.status == 'active')
    ).all()

    games = {game.game_name for game in get_all_account}

    return list(games)


# --- RENT ---

@app.post('/create-new-rent/', response_model=RentRead)
async def new_rent_create_endpoint(rent: RentCreate, session: SessionDep) -> Rent:
    new_rent = new_rent_create(rent, session)
    return new_rent

@app.patch('/update-rent/{rent_id}', response_model=RentRead)
async def update_rent_endpoint(rent_id: int, rent: RentUpdate, session: SessionDep):
    return update_rent(rent_id, rent, session)

@app.delete('/delete-rent/{rent_id}')
async def delete_rent_endpoint(rent_id: int, session: SessionDep):
    delete_rent(rent_id, session)
    return {"detail": "Rent deleted successfully"}

@app.get('/rents/', response_model=list[RentRead])
async def read_all_rents(session: SessionDep):
    return get_all_rents(session)

@app.get('/rents/{rent_id}', response_model=RentRead)
async def read_rent(rent_id: int, session: SessionDep):
    return get_rent(rent_id, session)

@app.get('/user-rents/{user_id}', response_model=list[RentRead])
async def get_user_rents(user_id: int, session: SessionDep, status: str = 'active'):
    user_exists = session.get(User, user_id)

    if not user_exists:
        raise HTTPException(status_code=404, detail='User does not exists')

    if status in ('active', 'ended'):
        user_rents = session.scalars(
            select(Rent)
            .where(Rent.user_id == user_id)
            .where(Rent.status == status)
        ).all()
        return user_rents
    elif status == 'all':
        user_rents = session.scalars(
            select(Rent)
            .where(Rent.user_id == user_id)
        ).all()
        return user_rents

@app.get('/is-rent-available-for-extend/{user_id}/')
async def is_available_rent_for_extend(user_id: int, session: SessionDep):
    user_rents = session.scalars(
        select(Rent)
        .where(Rent.user_id == user_id)
    ).all()

    rent_availability = []

    for rent in user_rents:
        rent_data = rent.dict()
        if rent.status == 'active' or rent.steam_account.in_use != True:
            rent_data['available'] = True
        else:
            rent_data['available'] = False
        rent_data['steam_account'] = rent.steam_account.dict()
        rent_availability.append(rent_data)


    return rent_availability

@app.get('/drop-db/')
async def drop_db() -> dict:
    reset_db(engine)
    return {'status': 'success'}

# --- PAYMENT ---

@app.post("/create-payment/", response_model=PaymentRead)
async def create_payment_endpoint(payment: PaymentCreate, session: SessionDep) -> Payment:
    return create_payment(payment, session)

@app.patch("/update-payment/{payment_id}", response_model=PaymentRead)
async def update_payment_endpoint(payment_id: int, payment: PaymentUpdate, session: SessionDep) -> Payment:
    return update_payment(payment_id, payment, session)

@app.delete("/payment/{payment_id}")
async def delete_payment_endpoint(payment_id: int, session: SessionDep) -> dict:
    delete_payment(payment_id, session)
    return {'detail': 'Payment deleted successfully'}

@app.get("/payments/{payment_id}", response_model=PaymentRead)
async def get_payment_endpoint(payment_id: int, session: SessionDep) -> Payment:
    return get_payment(payment_id, session)

@app.get("/payments/", response_model=list[PaymentRead])
async def get_all_payments_endpoint(session: SessionDep) -> Sequence[Payment]:
    return get_all_payments(session)