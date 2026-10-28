"""Module: audia.routes.tuner.__init__.

Purpose: Expose the existing tuner package components without creating an application.
Main components: tuner.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .tuner import tuner
