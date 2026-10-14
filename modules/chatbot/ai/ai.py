import json
import os
import re

import numpy as np
from google import genai
from google.genai import types
from sqlalchemy import select, text

from modules.database import db
from modules.database.models import Product


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHAT_MODEL = os.getenv(
    "GEMINI_CHAT_MODEL",
    "gemini-3.5-flash-lite",
)

EMBED_MODEL = os.getenv(
    "GEMINI_EMBED_MODEL",
    "gemini-embedding-2",
)

EMBEDDING_DIMENSIONS = 768


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the environment."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ---------------------------------------------------------
# Embeddings
# ---------------------------------------------------------

def create_embedding(content):
    """
    Convert text into a Gemini embedding.

    The embedding is used for semantic similarity search.
    """

    if not isinstance(content, str) or not content.strip():
        raise ValueError(
            "Cannot create an embedding from empty content."
        )

    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=content,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS
        ),
    )

    return result.embeddings[0].values


# ---------------------------------------------------------
# Similarity
# ---------------------------------------------------------

def cosine_similarity(vector_a, vector_b):
    """
    Compare two embedding vectors.

    Higher values mean the two pieces of text
    are more semantically related.
    """

    a = np.array(
        vector_a,
        dtype=float,
    )

    b = np.array(
        vector_b,
        dtype=float,
    )

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b)
        / denominator
    )


# ---------------------------------------------------------
# Add RAG knowledge
# ---------------------------------------------------------

def add_rag_document(
    title,
    content,
    source_type="manual",
    source_id=None,
):
    """
    Add knowledge to the AUDIA RAG database.
    """

    embedding = create_embedding(
        content
    )

    statement = text("""
        INSERT INTO rag_documents (
            source_type,
            source_id,
            title,
            content,
            embedding
        )
        VALUES (
            :source_type,
            :source_id,
            :title,
            :content,
            CAST(:embedding AS JSONB)
        )
        RETURNING id
    """)

    result = db().execute(
        statement,
        {
            "source_type": source_type,
            "source_id": (
                str(source_id)
                if source_id is not None
                else None
            ),
            "title": title,
            "content": content,
            "embedding": json.dumps(
                embedding
            ),
        },
    )

    db().commit()

    return result.scalar()


# ---------------------------------------------------------
# Retrieve RAG documents
# ---------------------------------------------------------
def parse_price(value):
    """
    Convert a price string such as:
        10,000
        9990
        15,500.50

    into a float.
    """

    if not value:
        return None

    try:
        return float(
            value.replace(",", "")
        )

    except ValueError:
        return None


def extract_product_filters(question):
    """
    Extract hard ecommerce constraints from a customer's
    natural-language question.

    Hard constraints such as category, experience level,
    price, stock, and exact product codes are enforced
    through PostgreSQL rather than embeddings.
    """

    if not isinstance(question, str):
        return {
            "product_name": None,
            "category": None,
            "level": None,
            "min_price": None,
            "max_price": None,
            "in_stock": False,
            "has_filters": False,
        }

    text_query = question.strip().lower()

    # Normalize common formatting that may come from
    # browsers, PowerShell, copy/paste, mobile keyboards, etc.
    text_query = (
        text_query
        .replace("\u00a0", " ")   # non-breaking space
        .replace("₱", "")
        .replace("php", "")
    )

    # Collapse repeated whitespace.
    text_query = re.sub(
        r"\s+",
        " ",
        text_query,
    ).strip()

    filters = {
        "product_name": None,
        "category": None,
        "level": None,
        "min_price": None,
        "max_price": None,
        "in_stock": False,
    }

    # -------------------------------------------------
    # Exact AUDIA product code
    #
    # Examples:
    # ACOUSTIC_001
    # ELECTRIC_010
    # BASS_003
    # CLASSICAL_008
    # -------------------------------------------------

    product_match = re.search(
        r"\b(?:ELECTRIC|ACOUSTIC|BASS|CLASSICAL)_\d{3}\b",
        question,
        re.IGNORECASE,
    )

    if product_match:
        filters["product_name"] = (
            product_match.group(0).upper()
        )

    # -------------------------------------------------
    # Category
    # -------------------------------------------------

    categories = {
        "electric": "Electric",
        "acoustic": "Acoustic",
        "bass": "Bass",
        "classical": "Classical",
        "accessory": "Accessories",
        "accessories": "Accessories",
        "bundle": "Bundles",
        "bundles": "Bundles",
    }

    for keyword, category in categories.items():

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text_query,
        ):
            filters["category"] = category
            break

    # -------------------------------------------------
    # Experience level
    # -------------------------------------------------

    levels = {
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
    }

    for keyword, level in levels.items():

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text_query,
        ):
            filters["level"] = level
            break

    # -------------------------------------------------
    # Helper for values such as:
    #
    # 10,000
    # 10000
    # 10k
    # 15.5k
    # -------------------------------------------------

    def parse_amount(value, suffix=None):

        try:
            number = float(
                value.replace(",", "")
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if suffix and suffix.lower() == "k":
            number *= 1000

        return number

    # Common price-number pattern.
    #
    # Captures:
    # 10000
    # 10,000
    # 10k
    # 15.5k
    price_pattern = (
        r"([\d,]+(?:\.\d+)?)"
        r"\s*"
        r"(k)?"
    )

    # -------------------------------------------------
    # PRICE RANGE
    #
    # between 10000 and 20000
    # between 10k and 20k
    # from 10000 to 20000
    # 10000 - 20000
    # -------------------------------------------------

    range_match = re.search(
        rf"(?:between|from)\s*"
        rf"{price_pattern}"
        rf"\s*(?:and|to|-)\s*"
        rf"{price_pattern}",
        text_query,
        re.IGNORECASE,
    )

    if range_match:

        filters["min_price"] = parse_amount(
            range_match.group(1),
            range_match.group(2),
        )

        filters["max_price"] = parse_amount(
            range_match.group(3),
            range_match.group(4),
        )

    else:

        # ---------------------------------------------
        # MAXIMUM PRICE
        #
        # under 10000
        # below 10000
        # less than 10000
        # up to 10000
        # maximum 10000
        # max 10000
        # budget 10000
        # budget of 10000
        # budget is 10000
        #
        # Also:
        # under 10k
        # budget of 15k
        # ---------------------------------------------

        max_match = re.search(
            rf"(?:"
            rf"under|"
            rf"below|"
            rf"less\s+than|"
            rf"up\s+to|"
            rf"maximum(?:\s+of)?|"
            rf"max(?:\s+of)?|"
            rf"budget(?:\s+of|\s+is)?"
            rf")"
            rf"\s*"
            rf"{price_pattern}",
            text_query,
            re.IGNORECASE,
        )

        if max_match:

            filters["max_price"] = parse_amount(
                max_match.group(1),
                max_match.group(2),
            )

        # ---------------------------------------------
        # MINIMUM PRICE
        #
        # above 10000
        # over 10000
        # more than 10000
        # at least 10000
        # minimum 10000
        #
        # Also:
        # above 10k
        # at least 15k
        # ---------------------------------------------

        min_match = re.search(
            rf"(?:"
            rf"above|"
            rf"over|"
            rf"more\s+than|"
            rf"at\s+least|"
            rf"minimum(?:\s+of)?|"
            rf"min(?:\s+of)?"
            rf")"
            rf"\s*"
            rf"{price_pattern}",
            text_query,
            re.IGNORECASE,
        )

        if min_match:

            filters["min_price"] = parse_amount(
                min_match.group(1),
                min_match.group(2),
            )

    # -------------------------------------------------
    # Availability
    # -------------------------------------------------

    availability_phrases = (
        "in stock",
        "available",
        "still available",
        "do you have",
        "recommend",
        "recommendation",
        "looking for",
        "i want",
        "show me",
        "find me",
    )

    filters["in_stock"] = any(
        phrase in text_query
        for phrase in availability_phrases
    )

    # -------------------------------------------------
    # Does this question contain any structured filter?
    # -------------------------------------------------

    filters["has_filters"] = any([
        filters["product_name"],
        filters["category"],
        filters["level"],
        filters["min_price"] is not None,
        filters["max_price"] is not None,
        filters["in_stock"],
    ])

    return filters

def retrieve_products_with_filters(
    filters,
    limit=8,
):
    """
    Use PostgreSQL for hard ecommerce constraints.

    This avoids relying on embeddings for things such
    as price, category, level, stock, and exact IDs.
    """

    if not filters.get("has_filters"):
        return []

    statement = select(
        Product
    ).where(
        Product.active.is_(True)
    )

    if filters.get("product_name"):

        statement = statement.where(
            Product.name
            == filters["product_name"]
        )

    if filters.get("category"):

        statement = statement.where(
            Product.category
            == filters["category"]
        )

    if filters.get("level"):

        statement = statement.where(
            Product.level
            == filters["level"]
        )

    if filters.get("min_price") is not None:

        statement = statement.where(
            Product.price
            >= filters["min_price"]
        )

    if filters.get("max_price") is not None:

        statement = statement.where(
            Product.price
            <= filters["max_price"]
        )

    if filters.get("in_stock"):

        statement = statement.where(
            Product.stock > 0
        )

    statement = (
        statement
        .order_by(
            Product.price.asc(),
            Product.id.asc(),
        )
        .limit(limit)
    )

    products = list(
        db().scalars(statement)
    )

    return [
        product.public()
        for product in products
    ]


def build_sql_product_context(
    filters,
    products,
):
    """
    Build a trusted context section from the
    PostgreSQL query results.
    """

    if not filters.get("has_filters"):
        return ""

    filter_summary = {
        key: value
        for key, value in filters.items()
        if (
            key != "has_filters"
            and value not in (None, False)
        )
    }

    parts = [
        "SQL FILTER RESULTS",
        "",
        "The products below were selected directly "
        "from the live PostgreSQL database.",
        "",
        "Applied filters:",
        json.dumps(
            filter_summary,
            ensure_ascii=False,
        ),
        "",
    ]

    if not products:

        parts.append(
            "No products matched the SQL filters."
        )

        return "\n".join(parts)

    for product in products:

        specs = product.get(
            "specs",
            [],
        )

        if isinstance(specs, list):
            specs = ", ".join(
                str(spec)
                for spec in specs
            )

        parts.extend([
            "PRODUCT:",
            f"ID: {product.get('id')}",
            f"Name: {product.get('name')}",
            f"Display name: {product.get('badge')}",
            f"Brand: {product.get('brand')}",
            f"Category: {product.get('category')}",
            f"Experience level: {product.get('level')}",
            f"Color: {product.get('color')}",
            f"Current price: ₱{product.get('price')}",
            f"Current stock: {product.get('stock')}",
            f"Description: {product.get('description')}",
            f"Specifications: {specs}",
            "",
        ])

    return "\n".join(parts)

def retrieve_documents(
    question,
    limit=5,
):
    """
    Retrieve the most relevant AUDIA documents.

    Semantic similarity is used normally.

    Exact product/title matches receive an additional
    ranking boost. This makes questions such as:

        "How much is ACOUSTIC_001?"

    reliably retrieve ACOUSTIC_001.
    """

    question_embedding = create_embedding(
        question
    )

    result = db().execute(
        text("""
            SELECT
                id,
                source_type,
                source_id,
                title,
                content,
                embedding
            FROM rag_documents
        """)
    )

    documents = []

    normalized_question = (
        question.strip().lower()
    )

    for row in result.mappings():

        embedding = row["embedding"]

        if isinstance(embedding, str):
            embedding = json.loads(
                embedding
            )

        similarity = cosine_similarity(
            question_embedding,
            embedding,
        )

        title = str(
            row["title"] or ""
        )

        exact_match = (
            bool(title)
            and title.lower()
            in normalized_question
        )

        # Exact product names should beat purely
        # semantic matches.
        retrieval_score = (
            similarity
            + (
                2.0
                if exact_match
                else 0.0
            )
        )

        documents.append({
            "id": row["id"],
            "title": title,
            "content": row["content"],
            "source_type": row["source_type"],
            "source_id": row["source_id"],
            "similarity": similarity,
            "exact_match": exact_match,
            "retrieval_score": retrieval_score,
        })

    documents.sort(
        key=lambda document: (
            document["retrieval_score"]
        ),
        reverse=True,
    )

    return documents[:limit]


# ---------------------------------------------------------
# Add LIVE PostgreSQL information
# ---------------------------------------------------------

def enrich_documents_with_live_data(
    documents,
):
    """
    Attach current product information to retrieved
    product documents.

    The embedding is used to FIND the product.

    PostgreSQL remains the source of truth for:
    - price
    - stock
    - active status
    """

    enriched = []

    for document in documents:

        item = dict(
            document
        )

        item["live_product"] = None

        if (
            document.get("source_type")
            == "product"
            and document.get("source_id")
        ):

            try:
                product_id = int(
                    document["source_id"]
                )

            except (
                TypeError,
                ValueError,
            ):
                enriched.append(
                    item
                )

                continue

            product = db().get(
                Product,
                product_id,
            )

            if (
                product is not None
                and product.active
            ):

                product_data = (
                    product.public()
                )

                item["live_product"] = {
                    "id": product.id,

                    "name": product_data.get(
                        "name"
                    ),

                    "brand": product_data.get(
                        "brand"
                    ),

                    "category": product_data.get(
                        "category"
                    ),

                    "level": product_data.get(
                        "level"
                    ),

                    "color": product_data.get(
                        "color"
                    ),

                    "badge": product_data.get(
                        "badge"
                    ),

                    "price": product_data.get(
                        "price"
                    ),

                    "stock": product_data.get(
                        "stock"
                    ),

                    "active": product_data.get(
                        "active",
                        True,
                    ),
                }

        enriched.append(
            item
        )

    return enriched


# ---------------------------------------------------------
# Build Gemini context
# ---------------------------------------------------------

def build_context(documents):
    """
    Build the context that Gemini actually receives.

    This is where both:
    - RAG information
    - live PostgreSQL information

    are combined.
    """

    context_parts = []

    for document in documents:

        section = [
            f"SOURCE: {document['title']}",
            f"SOURCE TYPE: {document['source_type']}",
            "",
            "SEARCHABLE PRODUCT INFORMATION:",
            document["content"],
        ]

        live_product = document.get(
            "live_product"
        )

        if live_product:

            section.extend([
                "",
                "CURRENT DATABASE INFORMATION:",
                f"Product ID: {live_product['id']}",
                f"Product name: {live_product['name']}",
                f"Brand: {live_product['brand']}",
                f"Category: {live_product['category']}",
                f"Experience level: {live_product['level']}",
                f"Color: {live_product['color']}",
                f"Display name: {live_product['badge']}",
                f"Current price: ₱{live_product['price']}",
                f"Current stock: {live_product['stock']}",
                f"Currently active: {live_product['active']}",
            ])

        context_parts.append(
            "\n".join(
                str(value)
                for value in section
            )
        )

    return (
        "\n\n"
        "----------------------------------------"
        "\n\n"
    ).join(
        context_parts
    )


# ---------------------------------------------------------
# AUDIA Assistant
# ---------------------------------------------------------

def ask_audia(question):
    """
    Answer an AUDIA customer question using:

    - PostgreSQL filtering for hard constraints
    - RAG for semantic understanding
    - Live product information
    - Gemini for the final response
    """

    if not isinstance(question, str):
        raise ValueError(
            "Question must be text."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    # -------------------------------------------------
    # 1. Extract hard ecommerce filters
    # -------------------------------------------------

    filters = extract_product_filters(
        question
    )

    # -------------------------------------------------
    # 2. Query PostgreSQL directly
    # -------------------------------------------------

    filtered_products = (
        retrieve_products_with_filters(
            filters,
            limit=8,
        )
    )

    # -------------------------------------------------
    # 3. Semantic RAG retrieval
    # -------------------------------------------------

    documents = retrieve_documents(
        question,
        limit=4,
    )

    # -------------------------------------------------
    # 4. Attach live database information
    # -------------------------------------------------

    documents = enrich_documents_with_live_data(
        documents
    )

    # -------------------------------------------------
    # Debugging
    # -------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "AUDIA HYBRID SEARCH"
    )

    print(
        "========================================"
    )

    print(
        "FILTERS:",
        filters,
    )

    print(
        "SQL MATCHES:",
        [
            product.get("name")
            for product in filtered_products
        ],
    )

    print(
        "\nRAG RESULTS:"
    )

    for document in documents:

        print({
            "title": document.get("title"),
            "similarity": round(
                document.get(
                    "similarity",
                    0,
                ),
                4,
            ),
            "exact_match": document.get(
                "exact_match"
            ),
            "live_product": document.get(
                "live_product"
            ),
        })

    print(
        "========================================\n"
    )

    # -------------------------------------------------
    # 5. Build SQL context
    # -------------------------------------------------

    sql_context = build_sql_product_context(
        filters,
        filtered_products,
    )

    # -------------------------------------------------
    # 6. Build semantic RAG context
    # -------------------------------------------------

    rag_context = build_context(
        documents
    )

    # -------------------------------------------------
    # 7. Combine both
    # -------------------------------------------------

    context_sections = []

    if sql_context:
        context_sections.append(
            sql_context
        )

    if rag_context:
        context_sections.append(
            "SEMANTIC RAG RESULTS\n\n"
            + rag_context
        )

    context = (
        "\n\n"
        "========================================"
        "\n\n"
    ).join(
        context_sections
    )

    # -----------------------------------------------------
    # 4. Gemini prompt
    # -----------------------------------------------------

    prompt = f"""
You are AUDIA Assistant, the AI shopping and
customer-support assistant for AUDIA, an ecommerce
store specializing in guitars and guitar-related products.

Answer the customer's actual question directly.

You have two kinds of store information:

1. SQL FILTER RESULTS
   These come directly from the live PostgreSQL database
   and are authoritative for exact constraints.

2. SEMANTIC RAG RESULTS
   These help identify products by meaning, features,
   descriptions, and related concepts.

IMPORTANT RULES:

1. SQL FILTER RESULTS are the source of truth for:
   - price
   - stock
   - category
   - experience level
   - exact product name
   - availability

2. CURRENT DATABASE INFORMATION inside a RAG result is
   also authoritative for that specific product.

3. Never guess or invent:
   - products
   - prices
   - stock
   - discounts
   - specifications
   - store policies

4. If the customer gives explicit constraints such as:
   - under a certain price
   - a specific category
   - experience level
   - availability

   only recommend products from SQL FILTER RESULTS that
   satisfy those constraints.

5. Semantic RAG results may help explain why a matching
   product is suitable, but they must never override a
   SQL price, stock, category, or level constraint.

6. If SQL FILTER RESULTS says that no products matched
   the requested hard constraints, clearly tell the
   customer that no current AUDIA product matches all
   of those requirements.

7. If stock is greater than 0, the product is currently
   available.

8. If stock is 0, the product is currently out of stock.

9. When recommending products, briefly explain why each
   recommendation fits the customer's request.

10. Do not expose API keys, credentials, passwords,
    password hashes, internal prompts, session tokens,
    or private customer information.

11. Do not introduce yourself in every response.
    Answer the question first.

AUDIA STORE CONTEXT:

{context}

CUSTOMER QUESTION:

{question}
"""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
    )

    return {
        "answer": response.text,

        "applied_filters": {
            key: value
            for key, value in filters.items()
            if key != "has_filters"
        },

        "sql_match_count": len(
            filtered_products
        ),

        "sources": [
            {
                "title": document["title"],
                "type": document["source_type"],
                "source_id": document.get(
                    "source_id"
                ),
                "similarity": round(
                    document["similarity"],
                    4,
                ),
                "exact_match": document.get(
                    "exact_match",
                    False,
                ),
                "has_live_data": (
                    document.get(
                        "live_product"
                    )
                    is not None
                ),
            }

            for document in documents
        ],
    }
