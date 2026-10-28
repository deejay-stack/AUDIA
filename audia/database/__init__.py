"""Module: audia.database.__init__.

Purpose: Expose the existing database package components without creating an application.
Main components: db, init_database, initialize, seed_catalog.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .connection import db, init_database, initialize, seed_catalog
