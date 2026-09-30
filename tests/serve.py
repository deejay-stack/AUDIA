"""Run the browser fixture on localhost with disposable data, not the real database."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import create_app
from modules.database import db, initialize
from modules.models import User
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='audia-browser-') as directory:
        app = create_app({'TESTING': True, 'SECRET_KEY': 'browser-fixture-only',
                          'DATABASE_URL': f'sqlite:///{Path(directory) / "browser.db"}', 'MAIL_BACKEND': 'memory'})
        initialize(app)
        with app.app_context():
            db().add(User(name='Test Admin', email='admin@example.com', role='admin',
                          password_hash=generate_password_hash('admin-password-123')))
            db().commit()
        try:
            app.run(host='127.0.0.1', port=int(os.getenv('TEST_PORT', '5056')), use_reloader=False)
        finally:
            app.extensions['engine'].dispose()
