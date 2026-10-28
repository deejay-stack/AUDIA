"""Module: audia.routes.orders.__init__.

Purpose: Expose the existing orders package components without creating an application.
Main components: orders.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .orders import orders
