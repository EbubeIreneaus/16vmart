from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Enum
from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.sql import func
from schemas.user import ROLE, STATUS


class User(Base):
    __tablename__ ="users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[EmailStr] = mapped_column(String(40), unique=True, nullable=False)
    email_verified: Mapped[Boolean] = mapped_column(Boolean, default=False)
    role: Mapped[ROLE] = mapped_column(Enum(ROLE), default=ROLE.USER)
    status: Mapped[STATUS] = mapped_column(Enum(STATUS), default=STATUS.ACTIVE)
    password: Mapped[str] = mapped_column(String, nullable=True)
    sessions: Mapped[List['Session']] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[User] = relationship(back_populates="sessions")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    device: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    refresh_token_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

