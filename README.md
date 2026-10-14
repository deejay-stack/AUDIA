# AUDIA

A Flask storefront and administration workspace with HTML templates, CSS, and vanilla JavaScript. Run the application from the root `app.py`; no frontend build is required.

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
3. Initialize the schema and catalog, then create an administrator:

```powershell
python -m flask --app app init-db
python -m flask --app app create-admin
```

The administrator command prompts for an email, name, and password. Public registration always creates a customer and redirects to `/login` with a success message. Creating an account does not sign the customer in; they must enter their password on the login page. `init-db` creates missing tables and seeds an empty catalog; it does not delete existing records or overwrite products. Future changes to an existing schema should use explicit database migrations rather than dropping tables.

For an HTTPS deployment, set `COOKIE_SECURE=true` and set `APP_URL` to the public origin. `FLASK_DEBUG` defaults to off. Use a production WSGI server for deployment.

## Modules

| Area | Implemented flows |
| --- | --- |
| Authentication | Customer registration, customer/admin sign-in, remembered sessions, logout, current-session restoration, password changes, recovery and single-use reset links |
| Account | Profile and delivery details, saved instruments, saved Finder preferences, order history and order details |
| Public landing | System overview, category studio photos, how it works, and account entry points |
| Storefront (sign-in required) | Search, categories, sorting, stock availability, sound previews, cart quantities, bundles, accessories, and support information |
| Checkout | Cash on delivery orders, server-calculated prices, transactional inventory checks, and duplicate-request protection |
| Tracking | Signed-in customers can retrieve only their own orders; administrators can inspect store orders |
| Administration | Inventory create/edit/archive/restore, customer directory/search, sales search/filter/pagination, CSV export, fulfillment status changes, store settings, and stock/order notifications |
| Reporting | Revenue from delivered orders, date-range totals, category totals, recent orders, and low stock |
| Assistance | Four-step Guitar Finder and the AUDI chatbot connected to the existing Flask AI/RAG service |

Payments are **cash on delivery**. There is no online payment gateway or carrier integration. Admin delivery and refund statuses record the store's actions; they do not charge cards, transfer funds, or call a shipping carrier. Cancellation and refund return the recorded quantities to inventory.

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

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for the full before/after trees,
every file move, the route comparison, and a guide to editing each feature.
Use [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) to find the files/functions for a broken component.

```text
app.py                       Flask app, settings, @app.route pages, CLI, entry point
modules/
  auth/                      Authentication, request security, password reset mail
  catalog/                   Products, availability, saved instruments, support
  search_filter/             Product search, type filters and budget/skill Finder
  orders/                    Customer checkout and order access
  admin/                     Protected store operations and reporting
  chatbot/                   AUDIA Assistant API; Gemini/RAG in chatbot/ai/
  tuner/                     Existing guitar tuner page
  lessons/                   Existing lesson routes and static chord/pattern data
  database/                  Shared connection lifecycle, initialization, and models
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
tests/                       API/security and browser integration checks
docs/components/             Current component moves, route snapshots and complete source
docs/architecture/           Historical first-refactor snapshots
docs/archive/                Original guitar-practice implementation snapshot
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

For example, to change a product card, edit `templates/catalog/catalog_product_card.html` and `assets/css/catalog/catalog.css`. The main `catalog.html` includes the component fragments. Product cards, cart and checkout have matching `catalog_*.html` fragments in the same folder. Search/sort controls, guitar-type filters, and the budget/skill Finder live in `search_filter/`. The chatbot has its own included template. The administration page similarly keeps its related sections together. Comment headings mark the sections. Repeated cards and popups use HTML `<template>` blocks within these component files; JavaScript fills them with data from the API.

`templates/shared/components.html`, `assets/css/shared/shared.css`, and `assets/js/shared/shared.js` contain elements used by several pages. `assets/js/shared/app.js` starts the current page and handles navigation, sign-out, and theme controls. `assets/js/shared/theme.js` applies the saved theme before the page appears. Flask still serves assets at `/static/`. Templates do not contain inline CSS; shared animation helpers apply movement styles at runtime.

Each backend feature has a folder under `modules/`, with a small `__init__.py` exposing its existing blueprint or services. Forms and interactive controls call the unchanged `/api/...` endpoints. To change account creation, edit `modules/auth/auth.py`; to change an existing entry page's template, edit `app.py`. Database credentials stay in `.env`. Test-only app construction is in `tests/support.py`.

## Chatbot: where to edit

The existing chat design is available on the public landing page and in the signed-in shop. Its markup is in `templates/chatbot/chatbot.html`, included by both pages. Chat styling lives in `assets/css/chatbot/chatbot.css`; shared utility and panel tokens remain in shared CSS. The public chat does not unlock the catalog, cart or checkout.

All chatbot JavaScript is grouped under `assets/js/chatbot/` (Flask serves the `assets` folder as `/static`):

| File | Purpose and functions to look at |
| --- | --- |
| `chatbot_api.js` | Flask requests only. `getSession()` loads the session and CSRF token; `refreshCsrfToken()` reloads it; `sendChatMessage()` posts the message and retries a rejected CSRF request once. `requestJson()` handles JSON, timeouts and network failures. |
| `chatbot_ui.js` | DOM only. `addUserMessage()` and `addAssistantMessage()` display safe text; `showTypingIndicator()`, `hideTypingIndicator()` and `setChatLoading()` control the waiting state; `showError()` displays a friendly error. |
| `chatbot.js` | `initChatbot()` connects existing buttons and the form. Its `sendMessage()` validates input, prevents duplicate submissions, calls the API and restores the form in `finally`. |

`assets/js/shared/app.js` calls `initChatbot()` after the page starts. The controller obtains `/api/auth/session`, then sends `{ "message": "..." }` to the existing `/api/chat` route with same-origin cookies, a CSRF header and UTF-8 JSON. Flask's existing `modules/chatbot/chatbot.py` calls `modules/chatbot/ai/ai.py`; only the returned `answer` appears in the chat. Sources, SQL filters and internal errors are not rendered. Gemini credentials stay on the server. CSRF tokens stay in JavaScript memory.

To test manually, run the configured Flask app, open `/`, and click **Open customer support**. Try **Hello**, **I am a beginner and I want a black acoustic guitar with a cutaway.**, **I am a beginner looking for an acoustic guitar under ₱10,000. What do you recommend?**, and **How much is ACOUSTIC_001 and is it still available?** Send with the button or Enter. Check the immediate message, typing indicator, answer and enabled input afterward. Blank messages should do nothing. Repeat in `/shop` after signing in. Close and reopen chat while waiting to check that the conversation is preserved. Use the browser's offline mode after opening chat to check the friendly error, then restore connectivity and send again.

For deterministic browser integration checks, run `python tests/serve.py` and then `node tests/chatbot.cjs`. These checks mock AI responses and cover guests, signed-in users, Unicode, safe rendering, failures and the single CSRF retry. To run the four real prompts against your configured backend in PowerShell (this calls the AI service):

```powershell
$env:AUDIA_BASE_URL = 'http://127.0.0.1:5000'
$env:AUDIA_CHAT_LIVE = '1'
node tests/chatbot.cjs
Remove-Item Env:AUDIA_CHAT_LIVE
Remove-Item Env:AUDIA_BASE_URL
```

## Verification

Server tests create and delete their own database; they never use `DATABASE_URL` from `.env`:

```powershell
python -m unittest discover -s tests -v
```

For browser tests, run the disposable fixture server in one terminal:

```powershell
python tests/serve.py
```

In a second terminal, with Playwright and Chromium available:

```powershell
node tests/browser.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright installation. `AUDIA_BASE_URL` defaults to the fixture at `http://127.0.0.1:5056`. Start a fresh fixture server for each full run. Set `SCREENSHOT_DIR=test-results` to save UI captures. Fixture credentials exist only in the disposable test database.

The tests cover authentication, authorization, CSRF, reset links, session revocation, inventory, idempotent checkout, order ownership, reporting, exports, and the customer/admin browser flows. Core API integration cases have also been checked against PostgreSQL using disposable schemas, with no test users or orders retained in the application tables. Production deployment and load testing are separate from these local checks.
