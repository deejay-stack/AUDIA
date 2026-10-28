"""Module: audia.routes.catalog.__init__.

Purpose: Expose the existing catalog package components without creating an application.
Main components: catalog, search_filter.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .catalog import catalog
# Register search/filter endpoints on this same blueprint before app registration.
from ..search_filter import search_filter
