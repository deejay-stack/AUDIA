"""Persistent records shared by feature modules."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16), default='customer')
    address: Mapped[str] = mapped_column(Text, default='')
    phone: Mapped[str] = mapped_column(String(30), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    def public(self):
        return {key: getattr(self, key) for key in ('id', 'name', 'email', 'role', 'address', 'phone')}


class LoginSession(Base):
    __tablename__ = 'login_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ResetToken(Base):
    __tablename__ = 'password_resets'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RateLimit(Base):
    __tablename__ = 'rate_limits'
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    brand: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    stock: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(30), default='Beginner')
    color: Mapped[str] = mapped_column(String(60), default='')
    badge: Mapped[str] = mapped_column(String(40), default='')
    image: Mapped[str] = mapped_column(Text, default='')
    description: Mapped[str] = mapped_column(Text, default='')
    specs: Mapped[str] = mapped_column(Text, default='[]')
    rating: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def public(self):
        import json
        data = {key: getattr(self, key) for key in ('id', 'name', 'brand', 'category', 'stock', 'level',
                 'color', 'badge', 'image', 'description', 'reviews', 'active')}
        return dict(data, price=float(self.price), rating=float(self.rating), specs=json.loads(self.specs))


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    customer: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))
    address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(30))
    total: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(24), default='Pending')
    payment: Mapped[str] = mapped_column(String(30), default='Cash on delivery')
    request_key: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    items: Mapped[list['OrderItem']] = relationship(cascade='all, delete-orphan', lazy='selectin')
    __table_args__ = (UniqueConstraint('user_id', 'request_key'),)

    def public(self):
        return dict(id=self.id, customer=self.customer, email=self.email, address=self.address,
                    phone=self.phone, amount=float(self.total), status=self.status, payment=self.payment,
                    date=self.created_at.strftime('%b %d, %Y'), created_at=self.created_at.isoformat(),
                    product=', '.join(f'{item.name} × {item.quantity}' for item in self.items),
                    items=[item.public() for item in self.items])


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    name: Mapped[str] = mapped_column(String(150))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(30))

    def public(self):
        return dict(product_id=self.product_id, name=self.name, quantity=self.quantity, price=float(self.price))


class Wishlist(Base):
    __tablename__ = 'wishlist'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)


class FinderProfile(Base):
    __tablename__ = 'finder_profiles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    profile: Mapped[str] = mapped_column(Text)


class Setting(Base):
    __tablename__ = 'settings'
    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
