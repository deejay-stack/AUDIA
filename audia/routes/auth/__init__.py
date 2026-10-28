"""Module: audia.routes.auth.__init__.

Purpose: Expose the existing auth package components without creating an application.
Main components: auth, install_security, require_user, require_page, validators and request helpers.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .auth import (
    auth, install_security, payload, require_user, require_page, string,
    validate_email, validate_password,
)
