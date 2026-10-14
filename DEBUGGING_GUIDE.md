# AUDIA debugging map

When your instructor removes code, locate the component first, then trace its
HTML → JavaScript → API/Python flow. CSS controls appearance. Primary files
use the same component name in each language.

| Broken behavior | Start here | Then trace |
| --- | --- | --- |
| Catalog page missing or wrong template | `app.py`: `shop()` → `templates/catalog/catalog.html` | Matching catalog CSS/JS and included `catalog_*.html` fragments |
| Products do not load | `assets/js/catalog/catalog.js`: `/products` request, `renderProducts()` | Network `/api/products` → `modules/search_filter/search_filter.py`: `products()` → `modules/catalog/catalog.py`: `products_data()` |
| Name, description, price, stock or image missing | `templates/catalog/catalog_product_card.html` | `catalog.js`: `renderProducts()`; `Product.public()` in `modules/database/models.py` |
| Add to Cart or quantity buttons fail | `assets/js/catalog/catalog.js`: `addToCart()`, `renderCart()`, `changeQuantity()` | `templates/catalog/catalog_cart.html`; stock limits; shared cart storage |
| Purchase/checkout fails | `templates/catalog/catalog_checkout.html`, `catalog.js`: `openCheckout()` | POST `/api/orders` → `modules/orders/orders.py`; inspect CSRF, request key, stock and order data |
| Search, type filtering or sorting fails | `assets/js/search_filter/search_filter.js`: `filterProducts()`, `handleAction()`, input/change listeners | `search_filter.html`, `search_filter_types.html`; server `products()` handles API query/type filtering |
| Budget/skill Finder stops advancing or returns no results | `search_filter.js`: `renderFinder()`, `finishFinder()` | `search_filter_finder.html`; POST `/api/finder` → `search_filter.py`: `finder()`; profile restoration |
| Search/Finder layout broken | `assets/css/search_filter/search_filter.css` | Its templates plus shared input/button utility styles; catalog includes these fragments |
| Chat window does not open/send | `assets/js/chatbot/chatbot.js`: `initChatbot()` | `chatbot.html`, `chatbot_ui.js`, `chatbot_api.js`; shared startup calls the initializer |
| Chat returns an error or wrong recommendation | POST `/api/chat` → `modules/chatbot/chatbot.py` | `modules/chatbot/ai/ai.py`: `ask_audia()`, `extract_product_filters()`, `retrieve_products_with_filters()`, `retrieve_documents()`, `enrich_documents_with_live_data()` |
| Chat wrapping/size/busy controls broken | `assets/css/chatbot/chatbot.css` | `templates/shared/base.html` loads it; shared panel/utility tokens apply too |
| Product knowledge not indexed | `modules/chatbot/ai/ai_rag_sync.py` | `build_product_document()`, `sync_products_to_rag()`, embeddings in `ai.py`; existing `sync-rag` CLI |
| Tuner page or controls missing | `modules/tuner/tuner.py`, `templates/tuner/tuner.html` | `assets/js/tuner/tuner.js`: `mountTuner()`, `startTuner()`, `stopTuner()`, `renderPitch()` |
| Wrong guitar note/flat/sharp indication | `assets/js/tuner/tuner_pitch.js` | `detectPitch()`, `describePitch()`, `PitchStabilizer`; run `node tests/tuner-pitch.cjs` |
| Tuner microphone does not start/stop | `assets/js/tuner/tuner.js` | Secure context, permission, stream tracks/AudioContext and lifecycle handlers; no server audio upload |
| Lesson page/link fails | `modules/lessons/lessons.py`: `lesson_page()` and page handlers | `templates/lessons/lessons.html` and named `lessons_*.html` subpages |
| Missing/wrong chord fingers or diagram | `modules/lessons/lessons_data.py`: `CHORDS` | `lessons_chords.html`, `lessons_chord_detail.html`, `lessons_chord_diagram.html`: `chord_diagram()` |
| Strumming beats/content wrong | `modules/lessons/lessons_data.py`: `STRUMMING_PATTERNS` | `templates/lessons/lessons_strumming.html` and `assets/css/lessons/lessons.css` |
| Multiple components lose theme/layout/navigation | `assets/js/shared/theme.js`, `shared/app.js`, `shared/shared.js` | `templates/shared/base.html`, `practice_base.html`, `practice_links.html`; shared CSS |
| Login, profile, passwords or CSRF fail | `modules/auth/auth.py` | Auth/account templates/controllers; reset mail in `auth_mail.py`; shared session/API helpers |
| Admin inventory, sales or order status fail | `modules/admin/admin.py` | `templates/admin/admin.html`, `assets/js/admin/admin.js`, `assets/css/admin/admin.css` |

The search field currently matches product names/brands. Type chips filter
guitar category, sorting supports price/rating, and Finder handles budget and
skill. AI recommendations are a separate flow from the deterministic Finder.
This grouping preserves those existing controls and behaviors.

## Check in this order

1. Read the Flask traceback and the browser Console for the failing filename.
2. Check Network for a missing static file or failing `/api/...` response.
3. Open the matching component HTML/JS/Python above; verify the relevant
   `data-action`, `data-field`, template ID and handler agree.
4. For appearance problems, check the matching CSS and its load in shared base.
5. For all components failing at startup, check `app.py`, package imports,
   the `.venv` interpreter and installed requirements.
6. Run the relevant existing tests, then the full suite after repairing code.

```powershell
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
node tests/tuner-pitch.cjs
```

Browser checks use `.venv/Scripts/python.exe tests/serve.py` with disposable
data, followed by `node tests/browser.cjs`, `node tests/chatbot.cjs`, or
`node tests/practice.cjs`. See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
for the full file map and unchanged routes.
