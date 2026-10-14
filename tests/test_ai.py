"""Exercise the moved chatbot -> AI -> RAG pipeline without a paid API call."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from sqlalchemy import text
from support import create_app
from modules.chatbot.ai import ai
from modules.database import db, initialize
from modules.database.models import Product


class AIPipelineTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "ai-fixture-only", "DATABASE_URL": "sqlite://"})
        initialize(self.app)
        with self.app.app_context():
            # The existing RAG code uses raw SQL; this table exists only in this
            # disposable test database. No application schema is changed.
            db().execute(text("CREATE TABLE rag_documents (id INTEGER PRIMARY KEY, source_type TEXT, source_id TEXT, title TEXT, content TEXT, embedding TEXT)"))
            for row in [
                {"id": 1, "source_type": "manual", "source_id": None, "title": "General advice", "content": "Practice regularly.", "embedding": json.dumps([1, 0, 0])},
                {"id": 2, "source_type": "product", "source_id": "1", "title": "ELECTRIC_001", "content": "Stored product information.", "embedding": json.dumps([0, 1, 0])},
            ]:
                db().execute(text("INSERT INTO rag_documents VALUES (:id, :source_type, :source_id, :title, :content, :embedding)"), row)
            db().commit()

    def tearDown(self):
        self.app.extensions["engine"].dispose()

    def test_chat_endpoint_retrieval_live_enrichment_and_gemini_response(self):
        provider = SimpleNamespace(models=SimpleNamespace(
            embed_content=Mock(return_value=SimpleNamespace(embeddings=[SimpleNamespace(values=[1, 0, 0])])),
            generate_content=Mock(return_value=SimpleNamespace(text="The guitar is available.")),
        ))
        client = self.app.test_client()
        csrf = client.get("/api/auth/session").json["csrf_token"]
        with patch.object(ai, "client", provider):
            response = client.post("/api/chat", json={"message": "How much is ELECTRIC_001 and is it still available?"},
                                   headers={"X-CSRF-Token": csrf})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["answer"], "The guitar is available.")
        self.assertEqual(response.json["sql_match_count"], 1)
        self.assertEqual(response.json["applied_filters"]["product_name"], "ELECTRIC_001")
        self.assertEqual(response.json["sources"][0]["title"], "ELECTRIC_001")
        self.assertTrue(response.json["sources"][0]["exact_match"])
        self.assertTrue(response.json["sources"][0]["has_live_data"])
        embedding = provider.models.embed_content.call_args.kwargs
        self.assertEqual(embedding["model"], ai.EMBED_MODEL)
        self.assertEqual(embedding["config"].output_dimensionality, ai.EMBEDDING_DIMENSIONS)
        generated = provider.models.generate_content.call_args.kwargs
        self.assertEqual(generated["model"], ai.CHAT_MODEL)
        self.assertIn("SQL FILTER RESULTS", generated["contents"])
        self.assertIn("SEMANTIC RAG RESULTS", generated["contents"])
        self.assertIn("CURRENT DATABASE INFORMATION", generated["contents"])
        with self.app.app_context():
            product = db().get(Product, 1).public()
        self.assertIn(f"Current price: ₱{product['price']}", generated["contents"])
        self.assertIn(f"Current stock: {product['stock']}", generated["contents"])

    def test_product_constraints_and_embedding_similarity(self):
        filters = ai.extract_product_filters("I am a beginner looking for an acoustic guitar under ₱10,000.")
        self.assertEqual(filters["category"], "Acoustic")
        self.assertEqual(filters["level"], "Beginner")
        self.assertEqual(filters["max_price"], 10000)
        self.assertTrue(filters["in_stock"])
        with self.app.app_context():
            products = ai.retrieve_products_with_filters(filters)
        self.assertTrue(products)
        self.assertTrue(all(item["category"] == "Acoustic" and item["level"] == "Beginner"
                            and item["price"] <= 10000 and item["stock"] > 0 for item in products))
        self.assertEqual(ai.cosine_similarity([1, 0], [1, 0]), 1)
        self.assertEqual(ai.cosine_similarity([1, 0], [0, 1]), 0)


if __name__ == "__main__":
    unittest.main()
