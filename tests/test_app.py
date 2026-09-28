"""Flask routes and existing API behavior, without starting a server."""
import unittest

from backend.app import PRODUCTS, SALES, app


class AudiaTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_html_and_static_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="storefront-template"', response.data)
        for path in ("css/styles.css", "css/motion.css", "js/app.js", "js/storefront.js",
                     "js/auth.js", "js/admin.js", "js/dom.js", "js/theme.js", "js/data.js"):
            with self.subTest(path=path):
                asset = self.client.get("/static/" + path)
                self.assertEqual(asset.status_code, 200)
                asset.close()

    def test_health_catalog_and_filtering(self):
        self.assertEqual(self.client.get("/api/health").json["status"], "ok")
        self.assertEqual(self.client.get("/api/products").json["products"], PRODUCTS)
        self.assertEqual(self.client.get("/api/products?category=acoustic&q=yamaha").json["count"], 1)
        self.assertEqual(self.client.get("/api/products?q=missing").json["count"], 0)
        self.assertEqual(self.client.get("/api/products/1").json, PRODUCTS[0])
        self.assertEqual(self.client.get("/api/products/999").status_code, 404)

    def test_finder_ranking(self):
        response = self.client.post("/api/finder", json={
            "budget": 20000, "level": "Beginner", "genre": "Rock", "category": "Electric",
        })
        self.assertEqual([p["id"] for p in response.json["recommendations"]], [1, 2])
        response = self.client.post("/api/finder", json={
            "budget": 15000, "level": "Beginner", "genre": "Pop", "category": "Acoustic",
        })
        self.assertEqual(response.json["recommendations"][0]["id"], 3)

    def test_login_rules(self):
        for role, email, password, code in (
            ("admin", "admin@audia.ph", "admin123", 200),
            ("admin", "admin@audia.ph", "wrong", 401),
            ("customer", "user@audia.ph", "audia123", 200),
            ("customer", "another@example.com", "abcdef", 200),
            ("customer", "user@audia.ph", "short", 401),
        ):
            with self.subTest(role=role, email=email, password=password):
                response = self.client.post("/api/auth/login", json={"email": email, "password": password, "role": role})
                self.assertEqual(response.status_code, code)
                if code == 200:
                    self.assertEqual(response.json["user"]["role"], role)
                    self.assertEqual(response.json["token"], f"audia-demo-{role}-token")

    def test_admin_data(self):
        self.assertEqual(self.client.get("/api/admin/sales").json, {"sales": SALES, "count": len(SALES)})
        self.assertEqual(self.client.get("/api/admin/summary").json, {
            "gross_revenue": 486820, "total_orders": 148, "new_customers": 39, "low_stock_items": 3,
        })

    def test_chat_branches(self):
        for message, expected in (
            ("I am a beginner", "For a beginner"),
            ("My budget is 20k", "Under ₱20,000"),
            ("Acoustic or electric?", "Choose acoustic"),
            ("I play rock", "For rock"),
            ("hello", "I can help"),
        ):
            with self.subTest(message=message):
                reply = self.client.post("/api/chat", json={"message": message}).json["reply"]
                self.assertTrue(reply.startswith(expected))


if __name__ == "__main__":
    unittest.main()
