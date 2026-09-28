"""Run the Flask website and existing AUDIA API from the project root."""
from backend.app import app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
