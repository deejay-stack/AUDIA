"""Module: audia.routes.chatbot.__init__.

Purpose: Expose the existing chatbot package components without creating an application.
Main components: chatbot.
Related: app.py composition root and the sibling implementation modules.
Debugging: Check exported imports and blueprint attachment order for import/registration failures.
"""
from .chatbot import chatbot
