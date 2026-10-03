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
    name = Column(String(50))
    slug = Column(String(55))
    is_active = Column(Boolean)
    level = Column(SmallInteger)


class PromotionEvent(Base):
    __tablename__ = "promotion_event"
    name = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    price_reduction = Column(Integer)


class Product(Base):
    __tablename__ = "product"
    name = Column(String(50))
    slug = Column(String(55))
    description = Column(Text)  # No length limit
    is_digital = Column(Boolean)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    price = Column(Numeric(10, 2))  # 10 digits, 2 decimal places


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"
    pass


class StockManagement(Base):
    __tablename__ = "stock_management"
    quantity = Column(Integer)
    last_checked_at = Column(DateTime(timezone=True))


class User(Base):
    __tablename__ = "user"
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(100))


class Order(Base):
    __tablename__ = "order"
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class OrderProduct(Base):
    __tablename__ = "order_product"
    quantity = Column(Integer)
