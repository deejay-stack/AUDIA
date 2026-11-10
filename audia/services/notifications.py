"""Persist customer activity in the same transaction as its business operation."""
from audia.database import db
from audia.database.models import Notification


def notify(order, message):
    from audia.services.settings import settings
    if order.channel == 'online' and settings()['notifications_enabled'] == 'true':
        db().add(Notification(user_id=order.user_id, order_id=order.id, message=message[:300]))
