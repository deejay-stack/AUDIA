# AUDIA

A Flask storefront and administration workspace with HTML templates, CSS, and vanilla JavaScript. Run the application from the root `app.py`; no frontend build is required.

The current [full-stack enhancement report](docs/ENHANCEMENT_REPORT.md) covers
customer return/refund requests, paid cancellation review, bank verification,
QR receipts, delivery maps, inventory movements, customer controls, store policies,
database preservation and executed tests. The configured database has received the
additive upgrade; existing accounts and historical records are preserved.

Install the updated `requirements.txt` before starting this version (QR/image
validation uses qrcode/Pillow). Start at `/orders`, `/admin/refunds`,
`/admin/transactions`, `/admin/delivery`, `/admin/inventory` or `/admin/settings`.
Electronic payments and refunds remain store-controlled simulations. Google Maps
is optional; Leaflet/OSM provides the default map with no API key. Use
`TRUSTED_PROXY_HOPS` only behind a known trusted reverse proxy.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Use the project interpreter shown above even if your terminal has not activated
`.venv`. The AI module requires `google-genai` (which provides `google.genai`)
and NumPy; both are included in `requirements.txt`. A `No module named 'google'`
error usually means the command is using another Python installation or the
dependencies have not been installed there.

Open **http://localhost:5000**. Visitors see a public landing page with a system overview, four guitar-family previews, and a short guide to using AUDIA. The full catalog, Guitar Finder, cart and checkout are available after sign-in. PostgreSQL credentials are required for account creation and shopping; the public overview still works without a database. There are no demo login bypasses or default administrator credentials.

PostgreSQL is the application database. Configuration is loaded from the root `.env`; SQLite is used only by isolated tests.

## PostgreSQL setup

1. Create a dedicated PostgreSQL database and application user.
2. Copy `.env.example` to `.env` and set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and `DB_PASSWORD`. Alternatively, leave those credentials unset and use `DATABASE_URL`. The separate fields safely handle special characters in passwords. Set `SECRET_KEY` to a long random secret, or leave it empty to use the persistent local key in `instance/`. Keep `.env` private.
3. Initialize the schema and catalog, then provision the first administrator only if none exists:

```powershell
python -m flask --app app init-db
python -m flask --app app create-admin
```

The administrator command prompts for an email, name, and password and refuses a second administrator. The existing administrator is preserved by the single-admin database constraint. Public registration always creates a customer and redirects to `/login` with a success message. Creating an account does not sign the customer in; they must enter their password on the login page. `init-db` creates missing tables and seeds an empty catalog; it does not delete existing records or overwrite products. Future changes to an existing schema should use explicit database migrations rather than dropping tables.

For an HTTPS deployment, set `COOKIE_SECURE=true` and set `APP_URL` to the public origin. `FLASK_DEBUG` defaults to off. Use a production WSGI server for deployment.

## Modules

| Area | Implemented flows |
| --- | --- |
| Authentication | Customer registration, customer/admin sign-in, remembered sessions, logout, current-session restoration, password changes, recovery and single-use reset links |
| Account | Profile and delivery details, saved instruments, saved Finder preferences, order history and order details |
| Public landing | System overview, category studio photos, how it works, and account entry points |
| Storefront (sign-in required) | Search, categories, sorting, stock availability, sound previews, cart quantities, bundles, accessories, and support information |
| Checkout | COD and six electronic payment simulations, server prices, inventory checks, duplicate protection and receipts |
| Tracking | Signed-in customers can retrieve only their own orders; administrators can inspect store orders |
| Administration | Inventory create/edit/archive/restore, customer directory/search, sales search/filter/pagination, CSV export, fulfillment status changes, store settings, and stock/order notifications |
| Reporting | Collection-date revenue minus refunds, POS/online channels, date filters, chart grouping, supporting transactions, CSV and printing |
| Assistance | Four-step Guitar Finder and the AUDI chatbot connected to the existing Flask AI/RAG service |

Payments support GCash, Maya, BDO, BPI, Metrobank, LandBank and Cash on Delivery. All new collections run in **Test Mode - No real funds transferred**. Admin counter POS supports cash and electronic simulations through the same ledger. COD counts only after explicit collection; refunds reduce revenue and do not automatically restock goods. See [the commerce delivery report](docs/COMMERCE_DELIVERY.md) for architecture, formulas, database changes, workflows, tests and limits.

The interface uses violet/mint accents, light/dark themes, responsive catalog and administration layouts, and a split sign-in screen. The uploaded guitars are served locally from `assets/images/{electric,acoustic,bass,classical}/`; `guitar_performance.jpg` appears on the authentication screen. `guitar_front.jpg` is the landing image, and the four `*_studio.jpg` files illustrate guitar families. Inventory accepts existing `/static/images/` paths and HTTPS image URLs. If an image fails, an uploaded studio photograph is shown with alternative text explaining that it is illustrative.

Guests do not fetch the full catalog. Opening `/shop` while signed out redirects to `/login`; signing in opens the shop, and signing out returns to the landing page and clears the local cart. Server authorization also protects product lists, individual products, recommendations and checkout, including expired sessions. Category previews can carry the selected category through sign-in. Old bookmarks such as `/#storefront` still redirect to the corresponding page.

## School-project catalog

`database/catalog.json` contains 40 guitars (10 per category), the starter bundle and the accessory pack. Guitar product names use `ELECTRIC_001` through `ELECTRIC_010`, `ACOUSTIC_001` through `ACOUSTIC_010`, `BASS_001` through `BASS_010` and `CLASSICAL_001` through `CLASSICAL_010`. The existing integer primary keys remain unchanged in structure for cart, order and saved-item relationships. Search by these codes in the store or inventory screen.

`AUDIA Demo` is an illustrative brand. Prices, stock and experience tiers are school-project sample data, not real inventory. Descriptions identify each image's appearance and suggest general playing uses; manufacturer, construction and performance specifications have not been verified. Replace the demo values through **Administration > Products** before real use. Image-to-code mappings are listed in `assets/images/SOURCES.md`; existing codes should not be renumbered when adding products.

The initial import uses the existing `init-db` command. Re-running it preserves an existing catalog, including edited prices and stock. Editing the JSON after initialization does not overwrite database records; use the inventory editor for subsequent updates. Check `/api/health` for database connectivity; `/api/products`, individual product endpoints and `/api/finder` require an authenticated session. No administrator account is created automatically.

## Password recovery

Configure one of these mail backends in `.env`:

- `MAIL_BACKEND=smtp`: supply `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM`. Delivery uses STARTTLS.
- `MAIL_BACKEND=file`: local development only. Reset messages appear in `instance/mail/*.eml`; they are not exposed through the website.
- `MAIL_BACKEND=disabled`: recovery reports that the service is unavailable. This is the default until mail is configured.

Reset requests use a generic response for unknown accounts. Links expire after 30 minutes and work once. Changing or resetting a password revokes other sessions. Passwords are hashed with scrypt; session tokens and reset tokens are stored as hashes. API mutations require a CSRF token. Login and recovery attempts are rate-limited in the database. Administration is authorized on the server.

## Structure

Start with CSS_EDITING_GUIDE.md (historical guide not included in this checkout) for beginner steps
to find a component, change its appearance, and understand dynamic text.

Use FRONTEND_COMPONENT_MAP.md (historical guide not included in this checkout) for the current
HTML/CSS/JavaScript file pairs and student debugging steps. The frontend now uses
traditional component CSS, with no Tailwind utilities or build dependency.
See UPGRADE_NOTES.md (historical guide not included in this checkout) for the current features and verification results.

See PROJECT_STRUCTURE.md (historical guide not included in this checkout) for the current folder tree,
backend responsibilities and a guide to editing each feature.
Use DEBUGGING_GUIDE.md (historical guide not included in this checkout) to find the files/functions for a broken component.

```text
app.py                       Flask app, settings, @app.route pages, CLI, entry point
audia/
  routes/                    Feature blueprints; auth keeps existing security hooks
    auth/ catalog/ search_filter/ orders/ admin/ chatbot/ tuner/ lessons/
  services/                  AI/RAG in ai/, reset mail in mail.py, order transitions in orders.py
  database/                  Shared connection lifecycle, initialization, and models
  config/                    Existing database URL builder
database/catalog.json        School-project catalog seed
templates/
  shared/                    Shared document, icons, dialogs, and practice layout
  landing/                   Public overview and account entry points
  auth/                      Login, registration and password recovery
  catalog/                   Shop, product cards, cart and checkout fragments
  search_filter/             Search/sort controls, type filters and Finder fragments
  account/                   Profile, password, saved instruments and orders
  admin/                     Dashboard, inventory, sales, customers and settings
  chatbot/                   Existing AUDI chat window
  tuner/                     Existing microphone tuner interface
  lessons/                   Existing basics, chord diagrams, and strumming lessons
assets/
  css/                       Shared styles and feature-specific folders
  js/                        Shared startup/helpers/theme and feature controllers
  images/                    Uploaded guitar and studio photos, plus source notes
docs/                        Current editing guides, component map and upgrade notes
instance/                    Ignored local secret key and development mail outbox
.env.example                 PostgreSQL, session, and mail configuration example
requirements.txt             Python runtime dependencies
```

## Where to edit

Start with `app.py`. It creates `app = Flask(...)`, registers the existing feature blueprints, and declares the existing `@app.route(...)` entry pages. Navigation uses normal URLs and full page loads. Each page extends `shared/base.html`, which loads `shared/shared.css` plus that page's matching stylesheet.

| Page URL | HTML in `templates/` | CSS in `assets/css/` | JavaScript in `assets/js/` |
| --- | --- | --- | --- |
| `/` | `landing/landing.html` | `landing/landing.css` | `shared/app.js` |
| `/login`, `/register`, `/reset-password` | `auth/auth.html` | `auth/auth.css` | `auth/auth.js` |
| `/shop` | `catalog/catalog.html` | `catalog/catalog.css` | `catalog/catalog.js` |
| `/account` | `account/account.html` | `account/account.css` | `account/account.js` |
| `/admin` | `admin/admin.html` | `admin/admin.css` | `admin/admin.js` |
| `/tuner` | `tuner/tuner.html` | `tuner/tuner.css` | `tuner/tuner.js`, `tuner/tuner_pitch.js` |
| `/lessons` and lesson details | `lessons/lessons.html` and `lessons_*.html` | `lessons/lessons.css` | Static Jinja pages; no separate controller |

For a product card, edit the PRODUCT CARD section in `templates/catalog/catalog.html` and `assets/css/catalog/catalog.css`. The same files contain catalog layout, cart, checkout, bundles, and tracking. Search, sorting, type chips, and Guitar Finder are together in `templates/search_filter/search_filter.html` and `assets/css/search_filter/search_filter.css`. Search for `SECTION:` to navigate. Shared layout, chatbot, and other features keep their own files. Repeated cards and popups retain their HTML `<template>` blocks; JavaScript fills them with API data.

`templates/shared/components.html`, `assets/css/shared/shared.css`, and `assets/js/shared/shared.js` contain elements used by several pages. `assets/js/shared/app.js` starts the current page and handles navigation, sign-out, and theme controls. `assets/js/shared/theme.js` applies the saved theme before the page appears. Flask still serves assets at `/static/`. Templates do not contain inline CSS; shared animation helpers apply movement styles at runtime.

Each backend feature has a folder under `audia/routes/`, with a small `__init__.py` exposing its existing blueprint or services. Forms and interactive controls call the unchanged `/api/...` endpoints. To change account creation, edit `audia/routes/auth/auth.py`; to change an existing entry page's template, edit `app.py`. Database credentials stay in `.env`. Shared order transitions and payment auditing are in `audia/services/orders.py`.

## Chatbot: where to edit

The existing chat design is available on the public landing page and in the signed-in shop. Its markup is in `templates/chatbot/chatbot.html`, included by both pages. Chat styling lives in `assets/css/chatbot/chatbot.css`; shared utility and panel tokens remain in shared CSS. The public chat does not unlock the catalog, cart or checkout.

All chatbot JavaScript is grouped under `assets/js/chatbot/` (Flask serves the `assets` folder as `/static`):

| File | Purpose and functions to look at |
| --- | --- |
| `chatbot_api.js` | Flask requests only. `getSession()` loads the session and CSRF token; `refreshCsrfToken()` reloads it; `sendChatMessage()` posts the message and retries a rejected CSRF request once. `requestJson()` handles JSON, timeouts and network failures. |
| `chatbot_ui.js` | DOM only. `addUserMessage()` and `addAssistantMessage()` display safe text; `showTypingIndicator()`, `hideTypingIndicator()` and `setChatLoading()` control the waiting state; `showError()` displays a friendly error. |
| `chatbot.js` | `initChatbot()` connects existing buttons and the form. Its `sendMessage()` validates input, prevents duplicate submissions, calls the API and restores the form in `finally`. |

`assets/js/shared/app.js` calls `initChatbot()` after the page starts. The controller obtains `/api/auth/session`, then sends `{ "message": "..." }` to the existing `/api/chat` route with same-origin cookies, a CSRF header and UTF-8 JSON. Flask's existing `audia/routes/chatbot/chatbot.py` calls `audia/services/ai/ai.py`; only the returned `answer` appears in the chat. Sources, SQL filters and internal errors are not rendered. Gemini credentials stay on the server. CSRF tokens stay in JavaScript memory.

To test manually, run the configured Flask app, open `/`, and click **Ask AUDI, Our AI Assistant**. Try **Hello**, **I am a beginner and I want a black acoustic guitar with a cutaway.**, **I am a beginner looking for an acoustic guitar under ₱10,000. What do you recommend?**, and **How much is ACOUSTIC_001 and is it still available?** Send with the button or Enter. Check the immediate message, typing indicator, answer and enabled input afterward. Blank messages should do nothing. Repeat in `/shop` after signing in. Close and reopen chat while waiting to check that the conversation is preserved. Use the browser's offline mode after opening chat to check the friendly error, then restore connectivity and send again.

## Orders, payments and learning updates

Authenticated customers can open **My Orders** at `/orders`. Order and payment
history, retry, cancellation and receipts use persisted backend records. Admins
have **Point of sale**, **Payments & transactions**, order fulfillment and COD
collection controls. Successful internal collections count toward revenue; pending
and failed payments do not. Refunds have separate audited records. Overview and
ledger views refresh while visible. Details and verification results are in
[COMMERCE_DELIVERY.md](docs/COMMERCE_DELIVERY.md).

The tuner uses real microphone input, with acoustic/electric sensitivity and
manual/automatic standard-string targets. Learning now includes 20 chord shapes,
nine courses, six strumming patterns, three original song studies and account-backed
lesson completion.

For an existing database, apply the additive migration before starting this version:

```powershell
.venv\Scripts\python.exe -m flask --app app upgrade-db
```

The configured database in this workspace has already been upgraded. The command
is repeatable and saves a private pre-upgrade row snapshot under `instance/backups/`.
It adds commerce tables/columns, normalizes legacy payment labels, and records missing historical balances as unpaid without inventing collection evidence. Fresh databases continue
to use `init-db`. Restart an already-running server to load Python changes.

See UPGRADE_NOTES.md (historical guide not included in this checkout) for features, bug fixes, database changes,
historical verification results and remaining limits. Current payment and security
tests are retained in `tests/`; browser screenshots and results are generated under
`test-results/commerce/`. Physical microphone and live external-service checks remain
manual. Existing startup commands and runtime dependencies are unchanged.

## Separate login portals and security regressions

Customers sign in at `/login` using `/api/auth/login`. The administrator signs in
at `/admin/login` using `/api/auth/admin/login`. Cross-role credentials are rejected
with the same generic error. The legacy `/login?role=admin` link redirects to the
administrator page. The server checks database identity and role on every protected
request; changing the URL, form fields or browser storage cannot change privileges.

Exactly one existing administrator is retained. Public registration is customer-only,
role assignment through public/profile forms is rejected, and a partial unique
index blocks a second administrator. `upgrade-db` applies this guard on other existing
checkouts after a private backup and refuses duplicate-admin databases without
changing accounts. It has already been applied to this workspace.

Restart the server after updating. Existing cookies must sign in once through the
correct portal; existing passwords and account records were not changed. Shared
profile/password and practice features remain available, while customer-only shopping
state and admin management are separated.

Run the retained security and payment regression suites:

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

See SECURITY_REVIEW.md (historical guide not included in this checkout) for every modified file, the test
matrix, shared color/spacing tokens, recovery checkpoints and verification limits.
