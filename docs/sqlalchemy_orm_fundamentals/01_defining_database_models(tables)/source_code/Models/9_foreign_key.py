from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(55), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=False)
    level = Column(SmallInteger, nullable=False, default=0)

    product = relationship("Product", back_populates="category")


class PromotionEvent(Base):
    __tablename__ = "promotion_event"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(50), nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    price_reduction = Column(Integer, nullable=False)


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id: Column[int] = Column(ForeignKey("category.id"), nullable=False)

    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(55), nullable=False, unique=True)
    description = Column(Text, nullable=False)  # No length limit
    is_digital = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # 10 digits, 2 decimal places

    category = relationship("Category", back_populates="product")


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"

    id = Column(Integer, primary_key=True, autoincrement=True)


class StockManagement(Base):
    __tablename__ = "stock_management"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=0)
    last_checked_at = Column(DateTime(timezone=True), nullable=False)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Column[int] = Column(ForeignKey("user.id"), nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="orders")


class OrderProduct(Base):
    __tablename__ = "order_product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id: Column[int] = Column(ForeignKey("order.id"), nullable=False)
    product_id: Column[int] = Column(ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
