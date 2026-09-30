# AUDIA

A Flask storefront and administration workspace with HTML templates, CSS, and vanilla JavaScript. Run the application from the root `app.py`; no frontend build is required.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

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

The administrator command prompts for an email, name, and password. Public registration always creates a customer. `init-db` creates missing tables and seeds an empty catalog; it does not delete existing records or overwrite products. Future changes to an existing schema should use explicit database migrations rather than dropping tables.

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
| Assistance | Four-step Guitar Finder and a rule-based guitar shopping guide |

Payments are **cash on delivery**. There is no online payment gateway or carrier integration. Admin delivery and refund statuses record the store's actions; they do not charge cards, transfer funds, or call a shipping carrier. Cancellation and refund return the recorded quantities to inventory.

The interface uses violet/mint accents, light/dark themes, responsive catalog and administration layouts, and a split sign-in screen. The uploaded guitars are served locally from `assets/images/{electric,acoustic,bass,classical}/`; `guitar_performance.jpg` appears on the authentication screen. `guitar_front.jpg` is the landing image, and the four `*_studio.jpg` files illustrate guitar families. Inventory accepts existing `/static/images/` paths and HTTPS image URLs. If an image fails, an uploaded studio photograph is shown with alternative text explaining that it is illustrative.

Guests do not fetch the full catalog. Opening `/#storefront` while signed out leads to sign-in; signing in opens the shop, and signing out returns to the landing page and clears the local cart. Server authorization also protects product lists, individual products, recommendations and checkout, including expired sessions. Category previews can carry the selected category through sign-in.

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

```text
app.py                       Application factory, configuration, CLI, root entry point
modules/
  auth.py                    Authentication and request security
  mail.py                    Password reset delivery
  catalog.py                 Catalog, recommendations, saved instruments, support
  orders.py                  Customer checkout and order access
  admin.py                   Protected store operations and reporting
  database.py                Connection lifecycle and initial schema setup
  models.py                  Database records
database/catalog.json        School-project catalog seed
templates/
  layouts/                   Document and template registry
  landing/                   Public overview and account entry points
  storefront/ auth/ account/ Feature screens and components
  cart/ finder/ chat/        Shopping dialogs and assistance
  admin/                     Overview, products, sales, customers, settings, alerts
  shared/                    Reusable dialog and runtime SVG icons
assets/
  css/                       Template-named styles and shared design rules
  js/                        Feature controllers and shared helpers
  images/                    Uploaded guitar and studio photos, plus source notes
tests/                       API/security and browser integration checks
instance/                    Ignored local secret key and development mail outbox
.env.example                 PostgreSQL, session, and mail configuration example
requirements.txt             Python runtime dependencies
```

Flask serves assets at `/static/`. `assets/css/index.css` imports the stylesheets; new feature styles use the corresponding template filename. Templates do not contain inline CSS. Shared animation helpers use runtime styles for movement.

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
