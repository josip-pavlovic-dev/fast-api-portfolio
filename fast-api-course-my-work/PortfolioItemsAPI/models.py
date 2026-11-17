from datetime import datetime
from decimal import Decimal
from enum import Enum as PythonEnum

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .db.base import Base


class ItemStatus(str, PythonEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    city_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cities.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

class Cities(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)


class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Items(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[ItemStatus] = mapped_column(
        SQLAlchemyEnum(
            ItemStatus,
            name="item_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        default=ItemStatus.DRAFT,
        server_default=ItemStatus.DRAFT.value,
        nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
