from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"

    name: Mapped[str | None] = mapped_column(String(50))
    slug: Mapped[str | None] = mapped_column(String(55))
    is_active: Mapped[bool | None] = mapped_column(Boolean)
    level: Mapped[int | None] = mapped_column(SmallInteger)


class PromotionEvent(Base):
    __tablename__ = "promotion_event"

    name: Mapped[str | None] = mapped_column(String(50))
    price_reduction: Mapped[int | None] = mapped_column(Integer)


class Product(Base):
    __tablename__ = "product"

    name: Mapped[str | None] = mapped_column(String(50))
    slug: Mapped[str | None] = mapped_column(String(55))
    description: Mapped[str | None] = mapped_column(
        Text
    )  # Nema ograničenja dužine teksta
    is_digital: Mapped[bool | None] = mapped_column(Boolean)
    is_active: Mapped[bool | None] = mapped_column(Boolean)
    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )  # 10 cifara, 2 decimalna mesta, npr. 12345678.90


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"
    pass


class StockManagement(Base):
    __tablename__ = "stock_management"

    quantity: Mapped[int | None] = mapped_column(Integer)


class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)


class Order(Base):
    __tablename__ = "order"
    pass


class OrderProduct(Base):
    __tablename__ = "order_product"

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
