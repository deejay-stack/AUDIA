"""Module: audia.routes.chatbot.chatbot.

Purpose: Validate chat requests and translate AI pipeline failures into HTTP responses.
Main components: chat_status, chat.
Related: services.ai.ask_audia, audia.database, and app-wide CSRF hooks.
Debugging: Check request validation and the logged exception before investigating AI retrieval.
"""
from flask import Blueprint, current_app, g, jsonify, request

from audia.services.ai import ask_audia

chatbot = Blueprint(
    "chatbot",
    __name__,
    url_prefix="/api"
)


@chatbot.get("/chat")
def chat_status():
    return jsonify({
        "status": "ok",
        "service": "AUDIA Assistant",
        "message": "AUDIA chatbot API is running."
    })


@chatbot.post("/chat")
def chat():

    """Read the message from request JSON and return the existing AI response.

    Invalid message lengths return 400. Pipeline exceptions trigger rollback,
    a logged traceback, and the existing 503 response.
    """
    data = request.get_json(
        silent=True
    )
    if not isinstance(data, dict):
        return jsonify(error="Please send a valid message form."), 400
    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify(error="Message must be text."), 400
    message = message.strip()

    if not message:
        return jsonify({
            "error": "Message is required."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "Message is too long."
        }), 400

    try:
        result = ask_audia(message)

        return jsonify(result)

    except Exception:
        if g.get("db"):
            g.db.rollback()

        current_app.logger.exception(
        "AUDIA AI request failed"
        )

        return jsonify({
        "error": (
            "AUDIA Assistant is currently unavailable."
        )
        }), 503
