"""New feature routes use the existing auth/security hooks and disposable data."""
import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from support import create_app
from modules.database import db, initialize
from modules.database.models import User
from werkzeug.security import generate_password_hash


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="audia-practice-")
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "practice-tests-only",
            "DATABASE_URL": f'sqlite:///{Path(self.directory.name) / "test.db"}',
        })
        initialize(self.app)
        with self.app.app_context():
            db().add(User(name="Practice Player", email="practice@example.com",
                          password_hash=generate_password_hash("practice-password-123")))
            db().commit()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.extensions["engine"].dispose()
        self.directory.cleanup()

    def sign_in(self):
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        result = self.client.post("/api/auth/login", json={
            "email": "practice@example.com", "password": "practice-password-123",
        }, headers={"X-CSRF-Token": csrf})
        self.assertEqual(result.status_code, 200)

    def test_guest_redirects_and_security(self):
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords",
                     "/lessons/chords/c-major", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response.location, "/login")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.post("/api/chat", json={"message": "hello"}).status_code, 403)
        self.assertEqual(self.client.get("/api/products").status_code, 401)

    def test_pages_assets_and_navigation(self):
        self.sign_in()
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            html = response.get_data(as_text=True)
            for link in re.findall(r'(?:href|src)="([^"]+)"', html):
                if link.startswith("/"):
                    with self.client.get(link.split("#")[0]) as linked:
                        self.assertEqual(linked.status_code, 200, link)
        for path in ("/", "/shop", "/account"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertIn('href="/tuner"', html)
            self.assertIn('href="/lessons"', html)
        for filename in ("css/shared/practice.css", "css/tuner/tuner.css", "css/lessons/lessons.css", "js/tuner/tuner.js", "js/tuner/tuner_pitch.js"):
            with self.client.get("/static/" + filename) as asset:
                self.assertEqual(asset.status_code, 200)

    def test_all_chord_shapes_and_missing_chord(self):
        self.sign_in()
        shapes = {
            "c-major": (1, 2, 3), "g-major": (0, 3, 3), "d-major": (2, 1, 3),
            "a-major": (1, 2, 3), "e-major": (0, 3, 3), "a-minor": (1, 2, 3),
            "e-minor": (0, 4, 2), "d-minor": (2, 1, 3),
        }
        for slug, (muted, opened, fretted) in shapes.items():
            html = self.client.get("/lessons/chords/" + slug).get_data(as_text=True)
            diagram = ElementTree.fromstring(re.search(r'<svg\s+class="chord-diagram".*?</svg>', html, re.S)[0])
            strings = diagram.findall(".//line[@class='chord-string']")
            self.assertEqual(len(strings), 6, slug)
            self.assertEqual([int(line.attrib["x1"]) for line in strings], [35, 65, 95, 125, 155, 185])
            markers = [(node.text or "").strip() for node in diagram.findall(".//text[@class='chord-open-muted']")]
            self.assertEqual(markers.count("X"), muted, slug)
            self.assertEqual(markers.count("O"), opened, slug)
            self.assertEqual(len(diagram.findall(".//circle")), fretted, slug)
            self.assertIn("Finger placement", html)
        self.assertEqual(self.client.get("/lessons/chords/missing-chord").status_code, 404)

    def test_revoked_session_and_read_only_routes(self):
        self.sign_in()
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        cookie = self.client.get_cookie("session").value
        self.assertEqual(self.client.post("/tuner").status_code, 405)
        self.client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
        self.client.set_cookie("session", cookie)
        self.assertEqual(self.client.get("/tuner").status_code, 302)
        self.assertEqual(self.client.get("/lessons").status_code, 302)


if __name__ == "__main__":
    unittest.main()
