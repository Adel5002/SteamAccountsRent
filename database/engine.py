from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session


postgres_url = 'postgresql://adel:1234@db:5432/games_rent'

engine = create_engine(postgres_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

