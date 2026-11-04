"""Module: audia.database.models.

Purpose: Define existing SQLAlchemy mappings and public record representations.
Main components: Base, account/catalog/order mappings, OrderEvent, OrderPayment, LessonProgress, UTC serializers.
Related: database.connection and auth/catalog/orders/admin route handlers.
Debugging: Inspect mapping and public() for serialization errors; preserve schema definitions.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now():
    return datetime.now(timezone.utc)


def utc_iso(value):
    """Serialize database timestamps consistently, including SQLite's naive UTC values."""
    return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.astimezone(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    # All current accounts are active. Preserve the sole admin and prevent a second,
    # including concurrent CLI or direct ORM/SQL inserts and role promotions.
    __table_args__ = (Index('uq_users_single_admin', 'role', unique=True,
                           postgresql_where=text("role = 'admin'"),
                           sqlite_where=text("role = 'admin'")),)
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
    events: Mapped[list['OrderEvent']] = relationship(lazy='selectin', order_by='OrderEvent.id')
    payment_record: Mapped['OrderPayment | None'] = relationship(lazy='selectin', uselist=False)
    payment_attempts: Mapped[list['PaymentAttempt']] = relationship(lazy='selectin', order_by='PaymentAttempt.created_at')
    __table_args__ = (UniqueConstraint('user_id', 'request_key'),)

    def public(self):
        from audia.services.orders import TRANSITIONS
        return dict(id=self.id, customer=self.customer, email=self.email, address=self.address,
                    phone=self.phone, amount=float(self.total), status=self.status, payment=self.payment,
                    date=self.created_at.strftime('%b %d, %Y'), created_at=utc_iso(self.created_at),
                    product=', '.join(f'{item.name} × {item.quantity}' for item in self.items),
                    items=[item.public() for item in self.items],
                    subtotal=float(self.total), shipping_fee=0,
                    payment_status=self.payment_record.status if self.payment_record else 'Pending',
                    is_demo=self.payment in ('GCash', 'Maya', 'BPI', 'BDO'),
                    payment_reference=self.payment_record.reference if self.payment_record else '',
                    payment_attempts=[attempt.public() for attempt in self.payment_attempts],
                    can_retry_payment=self.payment in ('GCash', 'Maya', 'BPI', 'BDO') and self.status == 'Pending' and (not self.payment_record or self.payment_record.status == 'Pending'),
                    payment_collected_at=utc_iso(self.payment_record.collected_at) if self.payment_record and self.payment_record.collected_at else None,
                    history=[event.public() for event in self.events],
                    next_statuses=TRANSITIONS.get(self.status, []))


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


class OrderEvent(Base):
    """Append-only fulfillment/payment audit entries; old orders keep their original dates."""
    __tablename__ = 'order_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    status: Mapped[str] = mapped_column(String(24))
    kind: Mapped[str] = mapped_column(String(16), default='status')
    note: Mapped[str] = mapped_column(String(300), default='')
    actor_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    def public(self):
        return dict(status=self.status, kind=self.kind, note=self.note, at=utc_iso(self.created_at))


class OrderPayment(Base):
    """COD collection or explicitly labelled demo settlement; never stores financial credentials."""
    __tablename__ = 'order_payments'
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    status: Mapped[str] = mapped_column(String(16), default='Pending')
    reference: Mapped[str] = mapped_column(String(200), default='')
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)


class PaymentAttempt(Base):
    """Internal simulation only; an immutable outcome and unique retry identity per attempt."""
    __tablename__ = 'payment_attempts'
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    request_key: Mapped[str] = mapped_column(String(80))
    method: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default='Pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint('order_id', 'request_key'),)

    def public(self):
        return dict(id=self.id, method=self.method, status=self.status, is_demo=True,
                    created_at=utc_iso(self.created_at), expires_at=utc_iso(self.expires_at),
                    completed_at=utc_iso(self.completed_at) if self.completed_at else None)


class LessonProgress(Base):
    """Per-user completion flags for the original practice curriculum."""
    __tablename__ = 'lesson_progress'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    lesson_slug: Mapped[str] = mapped_column(String(80), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
