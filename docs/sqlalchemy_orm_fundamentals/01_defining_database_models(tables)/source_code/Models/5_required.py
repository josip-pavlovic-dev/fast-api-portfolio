from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"
    name = Column(String(50), nullable=False)
    slug = Column(String(55), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    level = Column(SmallInteger, nullable=False, default=0)


class PromotionEvent(Base):
    __tablename__ = "promotion_event"
    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    price_reduction = Column(Integer, nullable=False)


class Product(Base):
    __tablename__ = "product"
    name = Column(String(50), nullable=False)
    slug = Column(String(55), nullable=False)
    description = Column(Text, nullable=False)  # No length limit
    is_digital = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # 10 digits, 2 decimal places


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"
    pass


class StockManagement(Base):
    __tablename__ = "stock_management"
    quantity = Column(Integer, nullable=False, default=0)
    last_checked_at = Column(DateTime(timezone=True), nullable=False)


class User(Base):
    __tablename__ = "user"
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(100), nullable=False)


class Order(Base):
    __tablename__ = "order"
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)


class OrderProduct(Base):
    __tablename__ = "order_product"
    quantity = Column(Integer, nullable=False)
