
import hashlib
import re
import secrets
from datetime import timedelta, timezone
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    request,
    session,
)
from sqlalchemy import case, delete, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from ..database import db
from ..database.models import (
    LoginSession,
    RateLimit,
    ResetToken,
    User,
    now,
)


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth",
)


# A fake hash used during failed login attempts so that
# checking a nonexistent email takes roughly the same amount
# of work as checking a real account.
DUMMY_HASH = generate_password_hash(
    secrets.token_urlsafe(32)
)


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def digest(value):
    """Create a SHA-256 hash for session/reset identifiers."""

    return hashlib.sha256(
        value.encode()
    ).hexdigest()


def expired(value):
    """Return True when a stored expiration time has passed."""

    return (
        value.replace(tzinfo=timezone.utc)
        <= now()
    )


def payload():
    """Read and validate a JSON request body."""

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Please send a valid form."
        )

    return data


def string(
    data,
    key,
    maximum=200,
    minimum=0,
):
    """Read and validate a string field from request data."""

    value = data.get(
        key,
        "",
    )

    if (
        not isinstance(value, str)
        or not minimum
        <= len(value.strip())
        <= maximum
    ):
        raise ValueError(
            f"Please enter a valid "
            f'{key.replace("_", " ")}.'
        )

    return value.strip()


def validate_email(value):
    """Validate and normalize an email address."""

    if (
        not isinstance(value, str)
        or len(value) > 254
        or not re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+",
            value.strip(),
        )
    ):
        raise ValueError(
            "Please enter a valid email address."
        )

    return value.strip().lower()


def validate_password(value):
    """Validate password length."""

    if (
        not isinstance(value, str)
        or not 10 <= len(value) <= 128
    ):
        raise ValueError(
            "Use a password between "
            "10 and 128 characters."
        )

    return value


# ---------------------------------------------------------
# Authentication decorator
# ---------------------------------------------------------

def require_user(admin=False):
    """
    Require a logged-in user.

    When admin=True, the user must also have
    the admin role.
    """

    def decorate(function):

        @wraps(function)
        def wrapped(*args, **kwargs):

            if g.user is None:
                return jsonify(
                    error="Please sign in to continue."
                ), 401

            if (
                admin
                and g.user.role != "admin"
            ):
                return jsonify(
                    error=(
                        "Administrator access "
                        "is required."
                    )
                ), 403

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorate


# ---------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------

def limit(
    action,
    identity="",
    maximum=8,
):
    """
    Atomic persistent counters shared across workers.

    Raw IP addresses / identities are not stored.
    """

    key = digest(
        f"{action}:"
        f"{request.remote_addr}:"
        f"{identity}"
    )

    from sqlalchemy.dialects.postgresql import (
        insert as pg_insert,
    )

    from sqlalchemy.dialects.sqlite import (
        insert as sqlite_insert,
    )

    insert = (
        pg_insert
        if db().bind.dialect.name == "postgresql"
        else sqlite_insert
    )

    current = now()

    statement = insert(
        RateLimit
    ).values(
        key=key,
        count=1,
        expires_at=(
            current
            + timedelta(minutes=15)
        ),
    )

    statement = statement.on_conflict_do_update(
        index_elements=["key"],
        set_={
            "count": case(
                (
                    RateLimit.expires_at
                    <= current,
                    1,
                ),
                else_=RateLimit.count + 1,
            ),
            "expires_at": case(
                (
                    RateLimit.expires_at
                    <= current,
                    current
                    + timedelta(minutes=15),
                ),
                else_=RateLimit.expires_at,
            ),
        },
    ).returning(
        RateLimit.count
    )

    count = (
        db()
        .execute(statement)
        .scalar_one()
    )

    db().commit()

    if count > maximum:

        from werkzeug.exceptions import (
            TooManyRequests,
        )

        raise TooManyRequests(
            "Too many attempts. "
            "Try again in 15 minutes."
        )


# ---------------------------------------------------------
# Login session creation
# ---------------------------------------------------------

def begin_session(
    user,
    remember=False,
):
    """
    Create a new authenticated session.

    A new CSRF token is generated whenever
    a new login session begins.
    """

    if session.get("sid"):

        db().execute(
            delete(
                LoginSession
            ).where(
                LoginSession.token_hash
                == digest(session["sid"])
            )
        )

    session.clear()

    token = secrets.token_urlsafe(32)

    session.update(
        sid=token,
        csrf=secrets.token_urlsafe(32),
    )

    session.permanent = remember

    db().add(
        LoginSession(
            token_hash=digest(token),
            user_id=user.id,
            expires_at=(
                now()
                + (
                    timedelta(days=30)
                    if remember
                    else timedelta(hours=12)
                )
            ),
        )
    )

    db().commit()

    return jsonify(
        user=user.public(),
        csrf_token=session["csrf"],
    )


# ---------------------------------------------------------
# Global security hooks
# ---------------------------------------------------------

def install_security(app):
    """
    Install session authentication, CSRF protection,
    security headers, and common error handlers.
    """

    @app.before_request
    def security():

        g.user = None

        # Static files do not require API security checks.
        if request.endpoint == "static":
            return

        # ---------------------------------------------
        # CSRF protection
        # ---------------------------------------------
        #
        # GET, HEAD, and OPTIONS do not modify server
        # state, so they do not require a CSRF token.
        #
        # POST, PUT, PATCH, DELETE, etc. must include:
        #
        # X-CSRF-Token: <token>
        #
        # The token must match the token stored inside
        # the user's Flask session.
        # ---------------------------------------------

        if (
            request.path.startswith("/api/")
            and request.method
            not in (
                "GET",
                "HEAD",
                "OPTIONS",
            )
        ):

            token = request.headers.get(
                "X-CSRF-Token",
                "",
            )

            stored_token = session.get(
                "csrf",
                "",
            )

            if (
                not token
                or not stored_token
                or not secrets.compare_digest(
                    token,
                    stored_token,
                )
            ):

                return jsonify(
                    error=(
                        "Your session has changed. "
                        "Refresh the page and try again."
                    )
                ), 403

        # ---------------------------------------------
        # Restore authenticated user
        # ---------------------------------------------

        if (
            session.get("sid")
            and "engine"
            in app.extensions
        ):

            record = db().get(
                LoginSession,
                digest(
                    session["sid"]
                ),
            )

            if (
                record is not None
                and not expired(
                    record.expires_at
                )
            ):

                g.user = db().get(
                    User,
                    record.user_id,
                )

            else:

                # Session ID is no longer valid.
                session.pop(
                    "sid",
                    None,
                )

    # -------------------------------------------------
    # Security headers
    # -------------------------------------------------

    @app.after_request
    def headers(response):

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "SAMEORIGIN"

        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        if (
            request.path.startswith("/api/")
            or response.mimetype == "text/html"
        ):

            response.headers[
                "Cache-Control"
            ] = "no-store"

        return response

    # -------------------------------------------------
    # Validation errors
    # -------------------------------------------------

    @app.errorhandler(ValueError)
    def invalid(error):

        db_session = g.get(
            "db"
        )

        if db_session:
            db_session.rollback()

        return jsonify(
            error=str(error)
        ), 400

    # -------------------------------------------------
    # Rate-limit errors
    # -------------------------------------------------

    @app.errorhandler(429)
    def throttled(error):

        return jsonify(
            error=error.description
        ), 429, {
            "Retry-After": "900"
        }


# ---------------------------------------------------------
# Session / CSRF initialization
# ---------------------------------------------------------

@auth.get("/session")
def current_session():
    """
    Return the currently signed-in user and initialize
    a CSRF token for this browser session.

    This endpoint can also be used by guests before
    sending POST requests such as /api/chat.
    """

    session.setdefault(
        "csrf",
        secrets.token_urlsafe(32),
    )

    return jsonify(
        user=(
            g.user.public()
            if g.user
            else None
        ),
        csrf_token=session["csrf"],
        services_ready=(
            "engine"
            in current_app.extensions
        ),
    )


# ---------------------------------------------------------
# Registration
# ---------------------------------------------------------

@auth.post("/register")
def register():

    data = payload()

    email = validate_email(
        data.get("email")
    )

    password = validate_password(
        data.get("password")
    )

    name = string(
        data,
        "name",
        100,
        2,
    )

    limit(
        "register",
        maximum=10,
    )

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(
            password
        ),
        role="customer",
    )

    db().add(user)

    try:

        db().flush()

    except IntegrityError:

        db().rollback()

        return jsonify(
            error=(
                "An account with that email "
                "already exists. "
                "Sign in or reset your password."
            )
        ), 409

    # Creating an account does not automatically
    # sign the customer in.
    db().commit()

    return jsonify(
        message=(
            "Account created successfully. "
            "Please sign in."
        )
    ), 201


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@auth.post("/login")
def login():

    data = payload()

    email = validate_email(
        data.get("email")
    )

    password = data.get(
        "password",
        "",
    )

    if (
        not isinstance(password, str)
        or len(password) > 128
    ):

        raise ValueError(
            "Please enter a valid password."
        )

    limit(
        "login-ip",
        maximum=40,
    )

    limit(
        "login",
        email,
    )

    user = db().scalar(
        select(
            User
        ).where(
            User.email == email
        )
    )

    valid = check_password_hash(
        (
            user.password_hash
            if user
            else DUMMY_HASH
        ),
        password,
    )

    if (
        not valid
        or not user
        or (
            data.get("role") == "admin"
            and user.role != "admin"
        )
    ):

        return jsonify(
            error=(
                "Incorrect email or password."
            )
        ), 401

    return begin_session(
        user,
        data.get("remember") is True,
    )


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@auth.post("/logout")
def logout():

    if session.get("sid"):

        db().execute(
            delete(
                LoginSession
            ).where(
                LoginSession.token_hash
                == digest(
                    session["sid"]
                )
            )
        )

        db().commit()

    session.clear()

    # Immediately provide a new CSRF token so that
    # the browser can continue making guest requests.
    session["csrf"] = (
        secrets.token_urlsafe(32)
    )

    return jsonify(
        message="Signed out.",
        csrf_token=session["csrf"],
    )


# ---------------------------------------------------------
# Profile
# ---------------------------------------------------------

@auth.patch("/profile")
@require_user()
def profile():

    data = payload()

    g.user.name = string(
        data,
        "name",
        100,
        2,
    )

    g.user.address = string(
        data,
        "address",
        500,
    )

    g.user.phone = string(
        data,
        "phone",
        30,
    )

    db().commit()

    return jsonify(
        user=g.user.public()
    )


# ---------------------------------------------------------
# Change password
# ---------------------------------------------------------

@auth.post("/password")
@require_user()
def change_password():

    data = payload()

    password = validate_password(
        data.get("password")
    )

    limit(
        "change-password",
        str(g.user.id),
    )

    current = data.get(
        "current_password",
        "",
    )

    if (
        not isinstance(current, str)
        or not check_password_hash(
            g.user.password_hash,
            current,
        )
    ):

        return jsonify(
            error=(
                "Your current password "
                "is incorrect."
            )
        ), 400

    g.user.password_hash = (
        generate_password_hash(
            password
        )
    )

    # Revoke every existing login session
    # belonging to this account.
    db().execute(
        delete(
            LoginSession
        ).where(
            LoginSession.user_id
            == g.user.id
        )
    )

    # Revoke active password-reset tokens.
    db().execute(
        delete(
            ResetToken
        ).where(
            ResetToken.user_id
            == g.user.id
        )
    )

    # Create a fresh session.
    return begin_session(
        g.user,
        session.permanent,
    )


# ---------------------------------------------------------
# Forgot password
# ---------------------------------------------------------

@auth.post("/forgot-password")
def forgot_password():

    from .auth_mail import send_reset

    data = payload()

    email = validate_email(
        data.get("email")
    )

    limit(
        "recovery",
        maximum=8,
    )

    if (
        current_app.config[
            "MAIL_BACKEND"
        ]
        == "disabled"
    ):

        return jsonify(
            error=(
                "Password recovery is unavailable. "
                "Please contact the store."
            )
        ), 503

    user = db().scalar(
        select(
            User
        ).where(
            User.email == email
        )
    )

    if user:

        token = (
            secrets.token_urlsafe(32)
        )

        db().execute(
            delete(
                ResetToken
            ).where(
                ResetToken.user_id
                == user.id
            )
        )

        db().add(
            ResetToken(
                token_hash=digest(
                    token
                ),
                user_id=user.id,
                expires_at=(
                    now()
                    + timedelta(
                        minutes=30
                    )
                ),
            )
        )

        send_reset(
            user.email,
            token,
        )

        db().commit()

    # Same response whether or not the email exists.
    return jsonify(
        message=(
            "If an account exists for that email, "
            "a password reset link has been sent."
        )
    )


# ---------------------------------------------------------
# Reset password
# ---------------------------------------------------------

@auth.post("/reset-password")
def reset_password():

    data = payload()

    password = validate_password(
        data.get("password")
    )

    token = string(
        data,
        "token",
        100,
        20,
    )

    limit(
        "reset",
        maximum=10,
    )

    record = db().scalar(
        select(
            ResetToken
        )
        .where(
            ResetToken.token_hash
            == digest(token)
        )
        .with_for_update()
    )

    if (
        not record
        or expired(
            record.expires_at
        )
    ):

        return jsonify(
            error=(
                "This reset link is invalid "
                "or expired. "
                "Request a new one."
            )
        ), 400

    user = db().get(
        User,
        record.user_id,
    )

    user.password_hash = (
        generate_password_hash(
            password
        )
    )

    # Revoke all existing sessions.
    db().execute(
        delete(
            LoginSession
        ).where(
            LoginSession.user_id
            == user.id
        )
    )

    # Revoke reset tokens.
    db().execute(
        delete(
            ResetToken
        ).where(
            ResetToken.user_id
            == user.id
        )
    )

    db().commit()

    session.clear()

    # Create a new guest CSRF token after reset.
    session["csrf"] = (
        secrets.token_urlsafe(32)
    )

    return jsonify(
        message=(
            "Password updated. "
            "You can now sign in."
        ),
        csrf_token=session["csrf"],
    )
