"""Module: audia.routes.lessons.__init__.

Purpose: Expose the existing lessons package components without creating an application.
Main components: lessons.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .lessons import lessons, lessons_api
