from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship



# ---------- ENUMS ----------
class SteamAccountStatus(str, Enum):
    active = 'active'
    in_use = 'in_use'
    banned = 'banned'


class RentStatus(str, Enum):
    active = 'active'
    ended = 'ended'
    overdue = 'overdue'


class PaymentStatus(str, Enum):
    successful = 'successful'
    declined = 'declined'
    pending = 'pending'


# ---------- MODELS ----------
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    balance: float = Field(default=0.0)
    rents: Optional[List["Rent"]] = Relationship(back_populates="user", cascade_delete=True)


class SteamAccount(SQLModel, table=True):
    id: int = Field(primary_key=True)
    login: str
    password: str
    game_name: str
    status: SteamAccountStatus = Field(default=SteamAccountStatus.active)
    rent: Optional["Rent"] = Relationship(back_populates="steam_account", cascade_delete=True)


class Rent(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    steam_account_id: int = Field(foreign_key="steamaccount.id")

    use_start_datetime: datetime
    use_end_datetime: datetime
    status: RentStatus = Field(default=RentStatus.active)

    user: User = Relationship(back_populates="rents")
    steam_account: SteamAccount = Relationship(back_populates="rent")


class Payment(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    sum: float
    status: PaymentStatus = Field(default=PaymentStatus.pending)


# ---------- SCHEMAS (DTO) ----------
# USER
class UserCreate(SQLModel):
    id: int
    username: str
    balance: float = 0.0


class UserRead(SQLModel):
    id: int
    username: str
    balance: float


class UserUpdate(SQLModel):
    username: Optional[str] = None
    balance: Optional[float] = None


# STEAM ACCOUNT
class SteamAccountCreate(SQLModel):
    login: str
    password: str
    game_name: str
    status: SteamAccountStatus = SteamAccountStatus.active


class SteamAccountRead(SQLModel):
    id: int
    login: str
    game_name: str
    status: SteamAccountStatus
    rent: Rent | None = None


class SteamAccountUpdate(SQLModel):
    login: Optional[str] = None
    password: Optional[str] = None
    game_name: Optional[str] = None
    status: Optional[SteamAccountStatus] = None


# RENT
class RentCreate(SQLModel):
    user_id: int
    steam_account_id: int
    use_start_datetime: datetime | None = datetime.today()
    use_end_datetime: datetime | None = datetime.today() + timedelta(1)
    status: RentStatus = RentStatus.active


class RentRead(SQLModel):
    id: int
    user_id: int
    steam_account_id: int
    use_start_datetime: datetime
    use_end_datetime: datetime
    status: RentStatus


class RentUpdate(SQLModel):
    user_id: Optional[int] = None
    steam_account_id: Optional[int] = None
    use_start_datetime: Optional[datetime] = None
    use_end_datetime: Optional[datetime] = None
    status: Optional[RentStatus] = None


# PAYMENT
class PaymentCreate(SQLModel):
    user_id: int
    sum: float
    status: PaymentStatus = PaymentStatus.pending


class PaymentRead(SQLModel):
    id: int
    user_id: int
    sum: float
    status: PaymentStatus


class PaymentUpdate(SQLModel):
    user_id: Optional[int] = None
    sum: Optional[float] = None
    status: Optional[PaymentStatus] = None