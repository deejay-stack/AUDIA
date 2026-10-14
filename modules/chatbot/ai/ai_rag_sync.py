import json

from sqlalchemy import select, text

from .ai import create_embedding
from modules.database import db
from modules.database.models import Product


def build_product_document(product):
    """
    Convert a Product into searchable RAG text.

    Intentionally excludes live values such as
    price and stock because those should be read
    directly from PostgreSQL when answering.
    """

    data = product.public()

    parts = [
        f"Product: {data.get('name', '')}",
        f"Brand: {data.get('brand', '')}",
        f"Category: {data.get('category', '')}",
        f"Experience level: {data.get('level', '')}",
    ]

    # Include these fields only if your Product.public()
    # method provides them.
    optional_fields = [
        ("description", "Description"),
        ("model", "Model"),
        ("body", "Body"),
        ("body_shape", "Body shape"),
        ("finish", "Finish"),
        ("strings", "Strings"),
        ("number_of_strings", "Number of strings"),
        ("genre", "Recommended genre"),
    ]

    for key, label in optional_fields:
        value = data.get(key)

        if value not in (None, "", []):
            parts.append(
                f"{label}: {value}"
            )

    return "\n".join(parts)


def sync_products_to_rag():
    """
    Synchronize active AUDIA products with rag_documents.

    - Creates embeddings for active products.
    - Inserts new products.
    - Updates existing products.
    - Removes RAG entries for products that are
      no longer active.
    """

    session = db()

    products = list(
        session.scalars(
            select(Product)
            .where(Product.active.is_(True))
            .order_by(Product.id)
        )
    )

    active_product_ids = {
        str(product.id)
        for product in products
    }

    indexed = 0

    for product in products:

        document = build_product_document(
            product
        )

        print(
            f"Indexing product {product.id}: "
            f"{product.name}"
        )

        embedding = create_embedding(
            document
        )

        session.execute(
            text("""
                INSERT INTO rag_documents (
                    source_type,
                    source_id,
                    title,
                    content,
                    embedding,
                    created_at,
                    updated_at
                )
                VALUES (
                    'product',
                    :source_id,
                    :title,
                    :content,
                    CAST(:embedding AS JSONB),
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (
                    source_type,
                    source_id
                )

                DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                "source_id": str(product.id),
                "title": product.name,
                "content": document,
                "embedding": json.dumps(
                    embedding
                ),
            },
        )

        indexed += 1

    # Find existing product RAG records.
    rag_products = session.execute(
        text("""
            SELECT id, source_id
            FROM rag_documents
            WHERE source_type = 'product'
        """)
    ).mappings()

    removed = 0

    for rag_product in rag_products:

        source_id = str(
            rag_product["source_id"]
        )

        if source_id not in active_product_ids:

            session.execute(
                text("""
                    DELETE FROM rag_documents
                    WHERE id = :id
                """),
                {
                    "id": rag_product["id"]
                },
            )

            removed += 1

    session.commit()

    return {
        "indexed": indexed,
        "removed": removed,
    }
