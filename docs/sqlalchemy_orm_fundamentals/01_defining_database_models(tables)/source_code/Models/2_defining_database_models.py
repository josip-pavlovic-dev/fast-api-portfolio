from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "category"
    pass


class PromotionEvent(Base):
    __tablename__ = "promotion_event"
    pass


class Product(Base):
    __tablename__ = "product"
    pass


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
