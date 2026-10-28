"""Module: audia.services.ai.__init__.

Purpose: Expose the existing ai package components without creating an application.
Main components: ask_audia, create_embedding.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .ai import ask_audia, create_embedding
