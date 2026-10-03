from sqlalchemy import (
    Boolean,
    # CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id: Column[int] = Column(
        ForeignKey("category.id", nullable=False, ondelete="RESTRICT")
    )

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

    products = relationship(
        "Product",
        secondary="product_promotion_event",
        back_populates="promotion_event",
    )


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id: Column[int] = Column(
        ForeignKey("category.id"), nullable=False, ondelete="RESTRICT"
    )

    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(55), nullable=False, unique=True)
    description = Column(Text, nullable=False)  # No length limit
    is_digital = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # 10 digits, 2 decimal places

    category = relationship("Category", back_populates="product")

    promotion_event = relationship(
        "PromotionEvent",
        secondary="product_promotion_event",
        back_populates="products",
    )

    stock = relationship(
        "StockManagement",
        uselist=False,
        back_populates="product",
        single_parent=True,
    )


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("product.id", ondelete="RESTRICT"), nullable=False
    )
    promotion_event_id = Column(
        Integer, ForeignKey("promotion_event.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id", "promotion_event_id", name="unique_product_event"
        ),
    )


class StockManagement(Base):
    __tablename__ = "stock_management"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id: Column[int] = Column(
        ForeignKey("product.id", ondelete="RESTRICT"), nullable=False, unique=True
    )

    quantity = Column(Integer, nullable=False, default=0)
    last_checked_at = Column(DateTime(timezone=True), nullable=False)

    product = relationship("Product", back_populates="stock")


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
    user_id: Column[int] = Column(
        ForeignKey("user.id", nullable=False, ondelete="RESTRICT")
    )

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="orders")


class OrderProduct(Base):
    __tablename__ = "order_product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity: Column[int] = Column(Integer, nullable=False)
