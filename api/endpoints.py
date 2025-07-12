from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.crud import create_user, add_new_steam_account, new_rent_create, delete_user, update_user, \
    update_steam_account, delete_steam_account, update_rent, delete_rent, get_all_users, get_user, \
    get_all_steam_accounts, get_steam_account, get_all_rents, get_rent
from database.engine import create_db_and_tables, SessionDep
from database.models import UserRead, UserCreate, User, SteamAccountCreate, SteamAccountRead, SteamAccount, RentRead, \
    RentCreate, Rent, RentUpdate, SteamAccountUpdate, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    create_db_and_tables()
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