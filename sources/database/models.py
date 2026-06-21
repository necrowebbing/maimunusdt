from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Float, DateTime, JSON
from typing import List, Optional
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime

class Base(DeclarativeBase):
    pass

class UserBase(Base):
    __tablename__ = "UsersTable"

    id: Mapped[int] = mapped_column(primary_key=True)
    tgId: Mapped[int] = mapped_column(Integer())
    username: Mapped[str] = mapped_column(String(), nullable=True)
    balance: Mapped[int] = mapped_column(Integer())
    referrerId: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    referrals: Mapped[int] = mapped_column(Integer(), default=0)
    lastBonus: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    isBanned: Mapped[bool] = mapped_column(Boolean(), default=False)
    brought: Mapped[int] = mapped_column(Integer())
    alreadyWarned: Mapped[bool] = mapped_column(Boolean(), default=False)

class PromocodesBase(Base):
    __tablename__ = "PromoTable"

    id: Mapped[int] = mapped_column(primary_key=True)
    promocode: Mapped[str] = mapped_column(String())
    maxActivates: Mapped[int] = mapped_column(Integer())
    activated: Mapped[int] = mapped_column(Integer())
    prize: Mapped[int] = mapped_column(Integer())
    activated_by: Mapped[Optional[List[int]]] = mapped_column(
        MutableList.as_mutable(JSON), 
        default=list
    )

class WithdrawsBase(Base):
    __tablename__ = "WithdrawTable"

    id: Mapped[int] = mapped_column(primary_key=True)
    tgId: Mapped[int] = mapped_column(Integer())
    isAccepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    requestDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    verificationDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True, default=None)
    sum: Mapped[int] = mapped_column(Integer())

class SponsorsBase(Base):
    __tablename__ = "SponsorsTable"

    id: Mapped[int] = mapped_column(primary_key=True)
    tgid: Mapped[int] = mapped_column(Integer())
    link: Mapped[str] = mapped_column(String())
    startDate: Mapped[datetime] = mapped_column(DateTime())
    finishDate: Mapped[datetime] = mapped_column(DateTime())
