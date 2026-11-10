"""Validated store configuration. No financial credentials are accepted."""
import re
from sqlalchemy import select
from audia.database import db
from audia.database.models import Setting
from audia.services.ledger import money

BANKS = {'BDO', 'BPI', 'Metrobank', 'LandBank'}
DEFAULTS = {
    'store_name': 'AUDIA Flagship', 'support_email': 'support@audia.ph', 'contact_phone': '',
    'shipping_fee': '0.00', 'delivery_options': 'School delivery simulation',
    'cancellation_policy': 'Unshipped orders may be cancelled. Paid orders require store approval.',
    'return_policy': 'Request a return within 14 days of delivery. Returned goods require inspection.',
    'return_days': '14', 'allow_cancellation': 'true', 'allow_partial_refunds': 'true',
    'return_required': 'true', 'bank_mode': 'automatic',
    'enabled_methods': 'cod,gcash,maya,bdo,bpi,metrobank,landbank',
    'checkout_instructions': 'Review your order. Payment is simulated; no funds are transferred.',
    'recipient_name': 'AUDIA School Store', 'receipt_footer': 'Thank you for shopping with us.',
    'notifications_enabled': 'true', 'cod_refund_destination': 'Store credit (simulated)',
    'categories': 'Electric,Acoustic,Bass,Classical,Accessories,Bundles',
    'map_provider': 'leaflet', 'google_maps_key': '',
    'map_tile_url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
}
for bank in BANKS:
    DEFAULTS['test_account_' + bank.lower()] = 'TEST-' + bank.upper() + '-001'


def settings():
    return dict(DEFAULTS, **{r.key: r.value for r in db().scalars(select(Setting))})


def save_settings(data):
    from audia.routes.auth import string, validate_email
    if set(data) - set(DEFAULTS):
        raise ValueError('An unsupported setting was supplied.')
    current = settings()
    for key in data:
        value = string(data, key, 2000)
        if key == 'store_name' or key == 'recipient_name':
            value = string(data, key, 100, 2)
        elif key == 'support_email':
            value = validate_email(value)
        elif key == 'shipping_fee':
            amount = money(value)
            if not 0 <= amount <= 10000:
                raise ValueError('Shipping fee must be between PHP 0 and 10,000.')
            value = str(amount)
        elif key == 'return_days':
            if not value.isdigit() or not 1 <= int(value) <= 90:
                raise ValueError('Return period must be 1–90 days.')
        elif key in ('allow_cancellation', 'allow_partial_refunds', 'return_required', 'notifications_enabled'):
            if value not in ('true', 'false'):
                raise ValueError('Choose an enabled or disabled policy value.')
        elif key == 'bank_mode' and value not in ('automatic', 'manual'):
            raise ValueError('Choose automatic simulation or manual bank verification.')
        elif key == 'enabled_methods':
            if not value or set(value.split(',')) - {'cod','gcash','maya','bdo','bpi','metrobank','landbank'}:
                raise ValueError('Choose supported payment method codes, separated by commas.')
        elif key == 'categories':
            names = value.split(',')
            if not 1 <= len(names) <= 30 or len(set(names)) != len(names) or any(not re.fullmatch(r'[\w &-]{1,30}', n) for n in names):
                raise ValueError('Enter unique category names separated by commas.')
        elif key.startswith('test_account_'):
            if not re.fullmatch(r'TEST-[A-Z]+-[A-Z0-9-]{1,20}', value):
                raise ValueError('Use a fictional TEST-BANK-identifier; never a real account number.')
        elif key == 'map_provider' and value not in ('leaflet', 'google'):
            raise ValueError('Choose Leaflet or Google Maps.')
        elif key == 'google_maps_key' and value and not re.fullmatch(r'[A-Za-z0-9_-]{20,200}', value):
            raise ValueError('Enter a restricted Google Maps browser API key.')
        elif key == 'map_tile_url':
            if not value.startswith('https://') or any(x not in value for x in ('{z}','{x}','{y}')):
                raise ValueError('Use an HTTPS tile URL containing {z}, {x}, {y}.')
        current[key] = value
    for key in data:
        db().merge(Setting(key=key, value=current[key]))
    return current


def payment_profile(order):
    config = settings()
    return dict(store_name=config['store_name'], recipient=config['recipient_name'],
                bank_mode=config['bank_mode'], instructions=config['checkout_instructions'],
                test_account=config.get('test_account_' + order.payment.lower(), ''),
                masked_account='•••• •••• TEST' if order.payment in BANKS else '',
                disclosure='Test environment — payment is simulated. No funds are transferred.')
