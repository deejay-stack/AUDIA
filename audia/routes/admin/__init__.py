"""Module: audia.routes.admin.__init__.

Purpose: Expose the existing admin package components without creating an application.
Main components: admin.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .admin import admin
