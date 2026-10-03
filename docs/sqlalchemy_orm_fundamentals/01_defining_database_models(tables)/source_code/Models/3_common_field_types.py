from sqlalchemy import Boolean, Column, Integer, Numeric, SmallInteger, String, Text
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
    price_reduction = Column(Integer)


class Product(Base):
    __tablename__ = "product"
    name = Column(String(50))
    slug = Column(String(55))
    description = Column(Text)  # No length limit
    is_digital = Column(Boolean)
    is_active = Column(Boolean)
    price = Column(Numeric(10, 2))  # 10 digits, 2 decimal places


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"
    pass


class StockManagement(Base):
    __tablename__ = "stock_management"
    quantity = Column(Integer)


class User(Base):
    __tablename__ = "user"
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(100), nullable=False)


class Order(Base):
    __tablename__ = "order"
    pass


class OrderProduct(Base):
    __tablename__ = "order_product"
    quantity = Column(Integer, nullable=False)
