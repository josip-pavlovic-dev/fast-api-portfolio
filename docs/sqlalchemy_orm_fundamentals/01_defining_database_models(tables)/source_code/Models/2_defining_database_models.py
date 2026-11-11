from sqlalchemy import Boolean, ForeignKey, SmallInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(55), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


class PromotionEvent(Base):
    __tablename__ = "promotion_event"
    pass


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220))


class ProductPromotionEvent(Base):
    __tablename__ = "product_promotion_event"
    pass


class StockManagement(Base):
    __tablename__ = "stock_management"
    pass


class User(Base):
    __tablename__ = "user"
    pass


class Order(Base):
    __tablename__ = "order"
    pass


class OrderProduct(Base):
    __tablename__ = "order_product"
    pass
