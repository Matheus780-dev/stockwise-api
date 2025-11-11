from sqlmodel import Session, select
from app.models import User, Product, Sale
from app.auth import hash_password, verify_password
from datetime import datetime


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).one_or_none()


def authenticate_user(db: Session, username: str, password: str) -> User |\
        None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_product(db: Session, name: str, price: float, quantity: int,
                   category: str | None = None) -> Product:
    product = Product(name=name, price=price,
                      quantity=quantity, category=category)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def list_products(db: Session):
    return db.exec(select(Product)).all()


def update_product_quantity(db: Session, product: Product, delta: int)\
        -> Product:
    product.quantity = product.quantity + delta
    if product.quantity < 0:
        raise ValueError("Quantidade do produto não pode ficar negativa")
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def create_sale(db: Session, product_id: int, quantity: int) -> Sale:
    product = get_product(db, product_id)
    if not product:
        raise ValueError("Produto inexistente")
    if product.quantity < quantity:
        raise ValueError("Estoque insuficiente")
    total = quantity * product.price

    product.quantity -= quantity
    sale = Sale(product_id=product_id, quantity=quantity, total_value=total)
    db.add_all([product, sale])
    db.commit()
    db.refresh(sale)
    return sale


def list_sales(db: Session, product_id: int | None = None):
    q = select(Sale)
    if product_id is not None:
        q = q.where(Sale.product_id == product_id)
    return db.exec(q.order_by(Sale.timestamp)).all()


def get_all_sales_for_period(db: Session, start: datetime | None = None, end:
                             datetime | None = None):
    q = select(Sale)
    if start:
        q = q.where(Sale.timestamp >= start)
    if end:
        q = q.where(Sale.timestamp <= end)
    return db.exec(q.order_by(Sale.timestamp)).all()
