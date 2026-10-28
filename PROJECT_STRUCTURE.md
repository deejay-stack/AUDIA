# AUDIA component structure

AUDIA — Guitar E-Commerce Platform. **Find Your Sound.**

Catalog and search/filter each now use one HTML file and one CSS file, with
`SECTION:` comments for navigation. Their current file pairs are in the table
below. File inventories farther down record the earlier component migration.

The five core functionalities have matching folder names and primary filenames
across Python, HTML, CSS, and JavaScript. Search/filter code has been separated
from catalog display/purchase code. The existing interface, content, API paths,
authorization, CSRF handling, database, Gemini configuration and pitch algorithm
are preserved.

## Five core components

| Functionality | Python in `modules/` | HTML in `templates/` | CSS in `assets/css/` | JavaScript in `assets/js/` |
| --- | --- | --- | --- | --- |
| Guitar Catalog | `catalog/catalog.py` | `catalog/catalog.html` | `catalog/catalog.css` | `catalog/catalog.js` |
| Search and Filter | `search_filter/search_filter.py` | `search_filter/search_filter.html` | `search_filter/search_filter.css` | `search_filter/search_filter.js` |
| AI Chatbot | `chatbot/chatbot.py`; AI engine in `chatbot/ai/ai.py` | `chatbot/chatbot.html` | `chatbot/chatbot.css` | `chatbot/chatbot.js` |
| Guitar Standard Tuner | `tuner/tuner.py` | `tuner/tuner.html` | `tuner/tuner.css` | `tuner/tuner.js` |
| Guitar Lessons | `lessons/lessons.py` | `lessons/lessons.html` | `lessons/lessons.css` | Server-rendered; no lesson controller is needed |

For instructor debugging exercises, start with
[DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md). It maps symptoms to the relevant
files and functions, including dependencies between components.

## What belongs in each folder

**Catalog:** product access, availability, saved instruments, store information,
product cards, cart, checkout, bundles, and order tracking. All catalog markup is in `catalog/catalog.html`, and all catalog CSS is in
`catalog/catalog.css`. Labeled section comments identify each part. Server-side order transactions stay in
`modules/orders/orders.py`; they are shared with account/admin views.

**Search/filter:** existing name/brand text search, guitar-type filters, price
and rating sorting, and the four-question budget/skill/style/type Finder.
All search/filter markup is in `search_filter/search_filter.html`, and its styles
are in `search_filter/search_filter.css`. The template has labeled toolbar, type
chips, banner, and Finder sections, selected where the catalog includes it.
The JavaScript owns query/sort/Finder state, and the Python file owns the
existing `/api/products` list filtering and `/api/finder` handlers. These
handlers attach to the existing `catalog` blueprint before registration,
preserving their `catalog.products` and `catalog.finder` endpoint names.
Product loading is shared through `catalog.catalog.products_data()`.

The existing UI searches brands through its text field and handles budget in
Finder and AI suggestions. Separate brand/price-range dropdowns are not added
by this organization work; price sorting and every existing control are retained.

**Chatbot:** the HTTP handler, included UI, stylesheet, controller,
`chatbot_api.js` request helpers, and `chatbot_ui.js` DOM helpers. Its Gemini,
embeddings, SQL filters, RAG retrieval, live-product enrichment and prompts
are together in `modules/chatbot/ai/ai.py`. Product knowledge synchronization
is `modules/chatbot/ai/ai_rag_sync.py`. The `sync-rag` CLI command is unchanged.
`shared/base.html` loads the chatbot stylesheet in its former position before
page styles, including on tuner/lesson pages where the shared layout includes
the assistant. Cross-page button/utility/panel tokens stay shared.

**Tuner:** the signed-in route, microphone interface and styles. Microphone
start/stop and rendering stay in `tuner.js`; pitch detection, note/cents
calculation and smoothing are in `tuner_pitch.js`. Standard E-A-D-G-B-E,
flat/sharp/in-tune states and browser resource cleanup are unchanged.

**Lessons:** the page routes and static data in `lessons_data.py`.
Subpages are `lessons_getting_started.html`, `lessons_chords.html`,
`lessons_chord_detail.html`, and `lessons_strumming.html`.
`lessons_chord_diagram.html` supplies the SVG macro. Content, chord shapes,
strumming counts, navigation and styling are unchanged.

## Supporting components

Authentication uses `modules/auth/auth.py`, `auth_mail.py`,
`templates/auth/auth.html`, and the existing matching auth assets.
Account forms remain in `templates/account/account.html` with account assets;
their profile/password/session endpoints remain in authentication.
Administration uses `modules/admin/admin.py` with `admin.html/css/js`.
Orders use `modules/orders/orders.py`; catalog/account/admin display their
shared order data. No empty order page or duplicate component is introduced.

Shared layout, navigation, theme and helpers remain in `templates/shared/`,
`assets/css/shared/`, and `assets/js/shared/`. The public landing page keeps
`landing.html` and `landing.css`. Shared SQLAlchemy models/lifecycle remain
in `modules/database/`; catalog seed data stays in `database/catalog.json`.
Images and their URLs are unchanged. `app.py` keeps application configuration,
entry-page routes, blueprint registration, security installation, CLI and
global error handling.

`__init__.py` files expose the same blueprint objects; component Python files
now use component names instead of generic `routes.py`. The old `modules/ai/`
source files were moved under `modules/chatbot/ai/`, retaining its package
entry point and every AI function.

## Moves in this grouping pass

| Previous location | Current location |
| --- | --- |
| `modules/auth/routes.py` | `modules/auth/auth.py` |
| `modules/auth/mail.py` | `modules/auth/auth_mail.py` |
| `modules/admin/routes.py` | `modules/admin/admin.py` |
| `modules/orders/routes.py` | `modules/orders/orders.py` |
| `modules/catalog/routes.py` | `modules/catalog/catalog.py` |
| `modules/chatbot/routes.py` | `modules/chatbot/chatbot.py` |
| `modules/ai/__init__.py` | `modules/chatbot/ai/__init__.py` |
| `modules/ai/services.py` | `modules/chatbot/ai/ai.py` |
| `modules/ai/rag_sync.py` | `modules/chatbot/ai/ai_rag_sync.py` |
| `modules/tuner/routes.py` | `modules/tuner/tuner.py` |
| `modules/lessons/routes.py` | `modules/lessons/lessons.py` |
| `modules/lessons/data.py` | `modules/lessons/lessons_data.py` |
| `templates/catalog/storefront.html` | `templates/catalog/catalog.html` |
| `assets/css/catalog/storefront.css` | `assets/css/catalog/catalog.css` |
| `assets/js/catalog/storefront.js` | `assets/js/catalog/catalog.js` |
| `assets/js/chatbot/chatbot-api.js` | `assets/js/chatbot/chatbot_api.js` |
| `assets/js/chatbot/chatbot-ui.js` | `assets/js/chatbot/chatbot_ui.js` |
| `assets/js/tuner/pitch.js` | `assets/js/tuner/tuner_pitch.js` |
| `templates/lessons/index.html` | `templates/lessons/lessons.html` |
| `templates/lessons/getting_started.html` | `templates/lessons/lessons_getting_started.html` |
| `templates/lessons/chords.html` | `templates/lessons/lessons_chords.html` |
| `templates/lessons/chord_detail.html` | `templates/lessons/lessons_chord_detail.html` |
| `templates/lessons/strumming.html` | `templates/lessons/lessons_strumming.html` |
| `templates/lessons/_chord_diagram.html` | `templates/lessons/lessons_chord_diagram.html` |

The new extracted files are:

- `modules/search_filter/__init__.py`
- `modules/search_filter/search_filter.py`
- `templates/search_filter/search_filter.html`
- `templates/search_filter/search_filter_types.html`
- `templates/search_filter/search_filter_finder_banner.html`
- `templates/catalog/catalog_product_card.html`
- `templates/catalog/catalog_navigation.html`
- `templates/catalog/catalog_bundle.html`
- `templates/catalog/catalog_support.html`
- `templates/catalog/catalog_cart.html`
- `templates/catalog/catalog_checkout.html`
- `templates/search_filter/search_filter_finder.html`
- `assets/css/search_filter/search_filter.css`
- `assets/css/chatbot/chatbot.css`
- `assets/js/search_filter/search_filter.js`

Every existing runtime/test/asset file inventoried before this pass remains at
its original or mapped location. No source, image, lesson content, seed record,
dependency or environment configuration was discarded. The verification test
was updated to today's captured source so your existing tuner-template edit
is preserved. A formatting-only save to `assets/css/lessons/lessons.css`
appeared during final verification; it was retained, with identical selectors
and declarations recorded in the extraction contract. Earlier architecture
reports remain historical snapshots.

## Trees, full source and verification

- [Before source tree](docs/components/tree-before.txt)
- [After source tree](docs/components/tree-after.txt)
- [Complete updated files](docs/components/updated-files.md)
- [Flask routes before](docs/components/routes-before.txt)
- [Flask routes after](docs/components/routes-after.txt)
- [Source inventory](docs/components/before.json)
- [Exact moves/extraction record](docs/components/migration.json)

All **45 route entries** retain their endpoints, URLs, and method sets, including
HEAD/OPTIONS. The same seven blueprint objects are registered once each.
**29 server tests**, the storefront/account/admin browser suite, the chatbot
browser suite, **130 practice layout/theme cases**, and **90 harmonic pitch
cases** pass. **56 before/after screenshots** in both themes at 375/1440 px
match under a strict compositor-rounding tolerance: at most 4/255 per channel
in at most 0.1% of pixels. An unchanged admin badge produced a four-pixel
edge difference of up to 4/255; the test accounts for that rounding without
changing application CSS. The server/source tests check all
existing files and the newly extracted markup, CSS and handlers.

Tests use disposable data and mocked Gemini responses. Physical microphone
quality and Safari/Firefox remain manual checks; no production database or paid
Gemini operation was used for this refactor.

## Run and debug

Use the project Python environment:

```powershell
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe -m flask --app app routes
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
node tests/tuner-pitch.cjs
```

For browser checks, start `.venv/Scripts/python.exe tests/serve.py` in one
terminal and run `node tests/browser.cjs`, `node tests/chatbot.cjs`, and
`node tests/practice.cjs` in another with Playwright available. Source and
route snapshots record this grouping pass; a deliberate future feature change
should update its contract rather than bypass it.
