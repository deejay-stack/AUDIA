from flask import Blueprint, current_app, jsonify, request

from .ai import ask_audia
from modules.database import db

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

    data = request.get_json(
        silent=True
    ) or {}

    message = str(
        data.get("message", "")
    ).strip()

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
        db().rollback()

        current_app.logger.exception(
        "AUDIA AI request failed"
        )

        return jsonify({
        "error": (
            "AUDIA Assistant is currently unavailable."
        )
        }), 503