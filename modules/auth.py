"""Password authentication, revocable sessions, CSRF, and account recovery."""
import hashlib
import re
import secrets
from datetime import timedelta, timezone
from functools import wraps
from flask import Blueprint, current_app, g, jsonify, request, session
from sqlalchemy import case, delete, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from .database import db
from .models import LoginSession, RateLimit, ResetToken, User, now

auth = Blueprint('auth', __name__, url_prefix='/api/auth')
DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(32))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def expired(value):
    return value.replace(tzinfo=timezone.utc) <= now()


def payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('Please send a valid form.')
    return data


def string(data, key, maximum=200, minimum=0):
    value = data.get(key, '')
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ValueError(f'Please enter a valid {key.replace("_", " ")}.')
    return value.strip()


def validate_email(value):
    if not isinstance(value, str) or len(value) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value.strip()):
        raise ValueError('Please enter a valid email address.')
    return value.strip().lower()


def validate_password(value):
    if not isinstance(value, str) or not 10 <= len(value) <= 128:
        raise ValueError('Use a password between 10 and 128 characters.')
    return value


def require_user(admin=False):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return jsonify(error='Please sign in to continue.'), 401
            if admin and g.user.role != 'admin':
                return jsonify(error='Administrator access is required.'), 403
            return function(*args, **kwargs)
        return wrapped
    return decorate


def limit(action, identity='', maximum=8):
    """Atomic persistent counters, shared across workers; raw identities are not stored."""
    key = digest(f'{action}:{request.remote_addr}:{identity}')
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    insert = pg_insert if db().bind.dialect.name == 'postgresql' else sqlite_insert
    current = now()
    statement = insert(RateLimit).values(key=key, count=1, expires_at=current + timedelta(minutes=15))
    statement = statement.on_conflict_do_update(index_elements=['key'], set_={
        'count': case((RateLimit.expires_at <= current, 1), else_=RateLimit.count + 1),
        'expires_at': case((RateLimit.expires_at <= current, current + timedelta(minutes=15)), else_=RateLimit.expires_at),
    }).returning(RateLimit.count)
    count = db().execute(statement).scalar_one()
    db().commit()
    if count > maximum:
        from werkzeug.exceptions import TooManyRequests
        raise TooManyRequests('Too many attempts. Try again in 15 minutes.')


def begin_session(user, remember=False):
    if session.get('sid'):
        db().execute(delete(LoginSession).where(LoginSession.token_hash == digest(session['sid'])))
    session.clear()
    token = secrets.token_urlsafe(32)
    session.update(sid=token, csrf=secrets.token_urlsafe(32))
    session.permanent = remember
    db().add(LoginSession(token_hash=digest(token), user_id=user.id,
                         expires_at=now() + (timedelta(days=30) if remember else timedelta(hours=12))))
    db().commit()
    return jsonify(user=user.public(), csrf_token=session['csrf'])


def install_security(app):
    @app.before_request
    def security():
        g.user = None
        if not request.path.startswith('/api/'):
            return
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            token = request.headers.get('X-CSRF-Token', '')
            if not token or not secrets.compare_digest(token, session.get('csrf', '')):
                return jsonify(error='Your session has changed. Refresh the page and try again.'), 403
        if session.get('sid') and 'engine' in app.extensions:
            record = db().get(LoginSession, digest(session['sid']))
            if record is not None and not expired(record.expires_at):
                g.user = db().get(User, record.user_id)
            else:
                session.pop('sid', None)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(ValueError)
    def invalid(error):
        db_session = g.get('db')
        if db_session:
            db_session.rollback()
        return jsonify(error=str(error)), 400

    @app.errorhandler(429)
    def throttled(error):
        return jsonify(error=error.description), 429, {'Retry-After': '900'}


@auth.get('/session')
def current_session():
    session.setdefault('csrf', secrets.token_urlsafe(32))
    return jsonify(user=g.user.public() if g.user else None, csrf_token=session['csrf'],
                   services_ready='engine' in current_app.extensions)


@auth.post('/register')
def register():
    data = payload()
    email = validate_email(data.get('email'))
    password = validate_password(data.get('password'))
    name = string(data, 'name', 100, 2)
    limit('register', maximum=10)
    user = User(name=name, email=email, password_hash=generate_password_hash(password), role='customer')
    db().add(user)
    try:
        db().flush()
    except IntegrityError:
        db().rollback()
        return jsonify(error='An account with that email already exists. Sign in or reset your password.'), 409
    return begin_session(user)


@auth.post('/login')
def login():
    data = payload()
    email = validate_email(data.get('email'))
    password = data.get('password', '')
    if not isinstance(password, str) or len(password) > 128:
        raise ValueError('Please enter a valid password.')
    limit('login-ip', maximum=40)
    limit('login', email)
    user = db().scalar(select(User).where(User.email == email))
    valid = check_password_hash(user.password_hash if user else DUMMY_HASH, password)
    if not valid or not user or (data.get('role') == 'admin' and user.role != 'admin'):
        return jsonify(error='Incorrect email or password.'), 401
    return begin_session(user, data.get('remember') is True)


@auth.post('/logout')
def logout():
    if session.get('sid'):
        db().execute(delete(LoginSession).where(LoginSession.token_hash == digest(session['sid'])))
        db().commit()
    session.clear()
    session['csrf'] = secrets.token_urlsafe(32)
    return jsonify(message='Signed out.', csrf_token=session['csrf'])


@auth.patch('/profile')
@require_user()
def profile():
    data = payload()
    g.user.name = string(data, 'name', 100, 2)
    g.user.address = string(data, 'address', 500)
    g.user.phone = string(data, 'phone', 30)
    db().commit()
    return jsonify(user=g.user.public())


@auth.post('/password')
@require_user()
def change_password():
    data = payload()
    password = validate_password(data.get('password'))
    limit('change-password', str(g.user.id))
    current = data.get('current_password', '')
    if not isinstance(current, str) or not check_password_hash(g.user.password_hash, current):
        return jsonify(error='Your current password is incorrect.'), 400
    g.user.password_hash = generate_password_hash(password)
    db().execute(delete(LoginSession).where(LoginSession.user_id == g.user.id))
    db().execute(delete(ResetToken).where(ResetToken.user_id == g.user.id))
    return begin_session(g.user, session.permanent)


@auth.post('/forgot-password')
def forgot_password():
    from .mail import send_reset
    data = payload()
    email = validate_email(data.get('email'))
    limit('recovery', maximum=8)
    if current_app.config['MAIL_BACKEND'] == 'disabled':
        return jsonify(error='Password recovery is unavailable. Please contact the store.'), 503
    user = db().scalar(select(User).where(User.email == email))
    if user:
        token = secrets.token_urlsafe(32)
        db().execute(delete(ResetToken).where(ResetToken.user_id == user.id))
        db().add(ResetToken(token_hash=digest(token), user_id=user.id, expires_at=now() + timedelta(minutes=30)))
        send_reset(user.email, token)
        db().commit()
    return jsonify(message='If an account exists for that email, a password reset link has been sent.')


@auth.post('/reset-password')
def reset_password():
    data = payload()
    password = validate_password(data.get('password'))
    token = string(data, 'token', 100, 20)
    limit('reset', maximum=10)
    record = db().scalar(select(ResetToken).where(ResetToken.token_hash == digest(token)).with_for_update())
    if not record or expired(record.expires_at):
        return jsonify(error='This reset link is invalid or expired. Request a new one.'), 400
    user = db().get(User, record.user_id)
    user.password_hash = generate_password_hash(password)
    db().execute(delete(LoginSession).where(LoginSession.user_id == user.id))
    db().execute(delete(ResetToken).where(ResetToken.user_id == user.id))
    db().commit()
    session.clear()
    session['csrf'] = secrets.token_urlsafe(32)
    return jsonify(message='Password updated. You can now sign in.', csrf_token=session['csrf'])
