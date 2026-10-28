# AUDIA project structure

Updated October 29, 2026. The application uses its existing Flask architecture.
Run it from root `app.py`; backend packages live under `audia/` so they do not
shadow the entry point. Frontend files remain grouped by feature.

```text
AUDIA_V2/
|-- app.py                          # Configuration, registration, entry pages, CLI
|-- audia/
|   |-- __init__.py
|   |-- config/
|   |   |-- __init__.py
|   |   `-- database.py             # Existing environment-based PostgreSQL URL
|   |-- database/
|   |   |-- __init__.py
|   |   |-- connection.py           # Engine, request sessions, teardown, seed setup
|   |   |-- models.py               # Existing mappings plus history/payment/progress
|   |   `-- migrations.py           # Additive upgrade with private row backup
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- admin/{__init__.py,admin.py}
|   |   |-- auth/{__init__.py,auth.py}
|   |   |-- catalog/{__init__.py,catalog.py}
|   |   |-- chatbot/{__init__.py,chatbot.py}
|   |   |-- lessons/{__init__.py,lessons.py,lessons_data.py}
|   |   |-- orders/{__init__.py,orders.py}
|   |   |-- search_filter/{__init__.py,search_filter.py}
|   |   `-- tuner/{__init__.py,tuner.py}
|   `-- services/
|       |-- __init__.py
|       |-- orders.py               # Shared transitions, stock restoration, collection
|       |-- mail.py                 # Existing reset delivery backends
|       `-- ai/{__init__.py,ai.py,ai_rag_sync.py}
|-- templates/
|   |-- account/                   # Account components and dedicated orders.html
|   |-- admin/                     # Inventory, orders/payments, sales, settings
|   |-- auth/                      # Login, registration, recovery/reset forms
|   |-- catalog/                   # Shop, cart, payment selection and checkout
|   |-- chatbot/                   # AUDI panel/messages/suggestions
|   |-- landing/                   # Existing public overview and sections
|   |-- lessons/                   # Original pages, chord library, courses and songs
|   |-- search_filter/             # Existing search/type/sort/Finder markup
|   |-- shared/                    # Layout, icons, dialogs, tracking and navigation
|   `-- tuner/                     # Microphone UI, modes, meter and string targets
|-- assets/
|   |-- css/                       # Feature styles and shared primitives/commerce.css
|   |-- js/                        # Feature controllers and shared helpers
|   |-- images/                    # Existing guitar/studio files and source notes
|   `-- icons-LICENSE.txt
|-- database/catalog.json           # Existing seed input
|-- instance/                      # Existing private runtime files and optional mail/
|   `-- backups/                   # Private pre-upgrade source and database snapshots
|-- docs/
|   |-- SECURITY_REVIEW.md          # Role security, constraint, UI tokens and tests
|   |-- UPGRADE_NOTES.md            # Features, migration, checks, cleanup and limitations
|   |-- CSS_EDITING_GUIDE.md
|   |-- FRONTEND_COMPONENT_MAP.md
|   `-- guitar-practice.md
|-- tests/test_security.py          # Retained security regression suite
|-- .env                           # Existing private settings; unchanged
|-- .env.example
|-- .gitignore
|-- requirements.txt               # Existing dependencies; unchanged
|-- README.md
|-- DEBUGGING_GUIDE.md
`-- PROJECT_STRUCTURE.md
```

`.git/`, `.venv/` and `.vscode/` remain in place. Earlier commerce tests, generated results, historical reports and empty stylesheet
files were removed after verification. The current role-security request adds
`tests/test_security.py` for retained regression coverage. Normal Python execution
may regenerate caches. Runtime files, images, licenses and environment settings
were retained. Package `__init__.py` files remain necessary import boundaries.

## Backend responsibilities

| File or package | Responsibility and debugging entry points |
| --- | --- |
| `app.py` | Declares separate customer/admin login pages and role-guarded workspaces; loads root `.env` before backend imports; applies settings; registers eight blueprints and existing security hooks; keeps entry pages, adds `/orders`; owns health/errors and `init-db`, `upgrade-db`, `create-admin`, `sync-rag`. |
| `audia/config/database.py` | Existing `build_database_url()` and DB credential/fallback rules; still imported by `app.py`. |
| `audia/database/connection.py` | `init_database()`, `db()`, request teardown, root seed loading and initialization. |
| `audia/database/models.py` | Existing account/catalog/order/settings mappings and public serializers; new `OrderEvent`, `OrderPayment`, `LessonProgress`; UTC serialization helper. |
| `audia/database/migrations.py` | `upgrade_database()` backs up existing rows privately and creates only missing new tables; repeatable without changing old records; also enforces the single-admin partial index and refuses duplicate admins. |
| `audia/routes/auth/auth.py` | Validators, account/session/password endpoints, `require_user()`, throttling, session creation/revocation, CSRF/security/error hooks. |
| `audia/routes/admin/admin.py` | Protected inventory/sales/export/customer/reporting/settings handlers; calls shared order-update service under an Order row lock. |
| `audia/routes/catalog/catalog.py` | Store metadata, product data/details and saved instruments. |
| `audia/routes/search_filter/search_filter.py` | Search and Finder handlers on the existing catalog blueprint; endpoint names stay `catalog.products` and `catalog.finder`. |
| `audia/routes/orders/orders.py` | Authenticated order history/details and COD checkout; existing row locks, server prices, ownership and idempotency. |
| `audia/services/orders.py` | One authoritative transition map; idempotent status history, cancellation/rejection/return stock restoration, verified COD collection and offline-refund audit. |
| `audia/routes/chatbot/chatbot.py` | Validates chat JSON, calls the existing AI service and returns safe error responses. |
| `audia/services/ai/ai.py` | Existing Gemini client, embeddings, filter parsing, SQL/RAG retrieval, ranking, live enrichment, context/prompts and answers. |
| `audia/services/ai/ai_rag_sync.py` | Existing product-document synchronization for `sync-rag`. |
| `audia/services/mail.py` | Existing reset message backends; optional file outbox remains in `instance/mail/`. |
| `audia/routes/tuner/tuner.py` | Signed-in tuner HTML. All microphone analysis stays in browser `tuner.js`/`tuner_pitch.js`. |
| `audia/routes/lessons/lessons.py` | Existing and new learning pages, chord filters, original songs and authenticated `/api/lessons/progress` routes. |
| `audia/routes/lessons/lessons_data.py` | Original lesson content plus 20 chords, six strumming patterns, nine courses and three original song studies. |
| Package `__init__.py` files | Expose existing components without creating another Flask app. Lessons exports page/API blueprints; catalog attaches search/filter before registration. |

Blueprints: `auth`, `catalog`, `orders`, `admin`, `chatbot`, `tuner`, `lessons`,
`lessons_api`. All 45 original route entries remain; the commerce additions brought the
total to 50 before the security pass. The new administrator page/API login
entries bring the current total to 52. Existing route names, HTTP methods and API paths were preserved.

## Frontend ownership

`assets/js/shared/app.js` starts the server-selected page, manages navigation,
logout, session revalidation and global cart badges. `shared/shared.js` owns
safe DOM helpers, API/CSRF requests, cart storage, visible-page polling and order
details/tracking. CSS for new checkout/payment/timeline elements is
`assets/css/shared/commerce.css`. Shared layouts, dialogs and inline SVG templates
continue to use `shared.css`; unused placeholder CSS files were removed.

Catalog handles stock-aware cart and checkout UI; account handles My Orders and
profile/saved views; admin handles the order/payment editor and directory.
Chatbot retains separate UI/controller/request helpers. Tuner separates audio
lifecycle/rendering from pure pitch calculations. The new lesson controller
handles account-backed completion; lesson content is rendered by Jinja.

Flask resource locations remain root `templates/`, root `assets/` at `/static`,
root `database/catalog.json` and root `instance/`. Existing images, upload/resource
references, environment variable names and startup conventions remain intact.

## Startup, upgrades and debugging

```powershell
.venv\Scripts\python.exe app.py
.venv\Scripts\python.exe -m flask --app app routes
.venv\Scripts\python.exe -m flask --app app upgrade-db
```

Restart an already running development server to load Python changes. The
configured database was upgraded in this workspace. For another existing checkout,
run `upgrade-db`; for a fresh database, use existing `init-db`. Credentials and
existing records stay intact. Recovery snapshots are private in `instance/backups/`.

For startup failures, inspect `.env` loading and the traceback module. For database
issues, inspect the URL helper, connection lifecycle and `/api/health`. For request
failures, trace the browser Network URL into its route, then into the service.
Check auth `security()`/`require_user()` for CSRF/session/role rejection. For
checkout, inspect the request key, validated payment method and locked inventory;
for tracking, inspect `OrderEvent`, transition validation and polling. For tuner
issues, check secure context, microphone permission, chosen target and actual audio.

[DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) maps symptoms to functions.
[UPGRADE_NOTES.md](docs/UPGRADE_NOTES.md) records all changes, database preservation,
36 passing Python checks, pitch checks, cleanup and verification limits.


## Current role-security pass

See [SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md) for the exact policy and modified
file list. The sole existing administrator and all 14 tables' records were preserved.
`User` declares `uq_users_single_admin`; the reusable API/page guards are exported
from `audia/routes/auth/`. The new denial page is `templates/auth/access_denied.html`.

Customer login is `/login`; administrator login is `/admin/login`. POST endpoints
are `/api/auth/login` and `/api/auth/admin/login` respectively. Customer shop/orders
and admin management are role-restricted; shared profile/password and practice
features remain available to their authenticated users. Sessions now bind the
verified database role; old cookies require one fresh login after server restart.

Shared semantic colors, spacing, typography and radii live in `theme.css` and are
used by existing shared components. New security regressions live in
`tests/test_security.py` and use disposable SQLite with independent cookie jars.
