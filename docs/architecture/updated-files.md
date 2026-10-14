# Historical architecture handoff

This is the previous refactor snapshot. For current component filenames and
complete files, see [the component handoff](../components/updated-files.md).

This handoff contains complete current versions of every modified existing
file, every moved runtime file (including unchanged files), and all new
source and architecture support files. The unchanged historical source
snapshot remains in `docs/archive/guitar-practice-source.md`.

See [PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) for the original/final
trees, migration map, responsibilities, routes, and verification.

No environment secrets or local database contents are included.

## File index

- [PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md)
- [README.md](../../README.md)
- [app.py](../../app.py)
- [assets/css/account/account.css](../../assets/css/account/account.css)
- [assets/css/admin/admin.css](../../assets/css/admin/admin.css)
- [assets/css/auth/auth.css](../../assets/css/auth/auth.css)
- [assets/css/catalog/storefront.css](../../assets/css/catalog/storefront.css)
- [assets/css/landing/landing.css](../../assets/css/landing/landing.css)
- [assets/css/lessons/lessons.css](../../assets/css/lessons/lessons.css)
- [assets/css/shared/practice.css](../../assets/css/shared/practice.css)
- [assets/css/shared/shared.css](../../assets/css/shared/shared.css)
- [assets/css/tuner/tuner.css](../../assets/css/tuner/tuner.css)
- [assets/js/account/account.js](../../assets/js/account/account.js)
- [assets/js/admin/admin.js](../../assets/js/admin/admin.js)
- [assets/js/auth/auth.js](../../assets/js/auth/auth.js)
- [assets/js/catalog/storefront.js](../../assets/js/catalog/storefront.js)
- [assets/js/chatbot/chatbot-ui.js](../../assets/js/chatbot/chatbot-ui.js)
- [assets/js/shared/app.js](../../assets/js/shared/app.js)
- [assets/js/shared/shared.js](../../assets/js/shared/shared.js)
- [assets/js/shared/theme.js](../../assets/js/shared/theme.js)
- [assets/js/tuner/pitch.js](../../assets/js/tuner/pitch.js)
- [assets/js/tuner/tuner.js](../../assets/js/tuner/tuner.js)
- [docs/architecture/after.json](../../docs/architecture/after.json)
- [docs/architecture/before.json](../../docs/architecture/before.json)
- [docs/architecture/migration.json](../../docs/architecture/migration.json)
- [docs/architecture/removed-empty-folders.json](../../docs/architecture/removed-empty-folders.json)
- [docs/architecture/routes-after.txt](../../docs/architecture/routes-after.txt)
- [docs/architecture/routes-before.txt](../../docs/architecture/routes-before.txt)
- [docs/architecture/tree-after.txt](../../docs/architecture/tree-after.txt)
- [docs/architecture/tree-before.txt](../../docs/architecture/tree-before.txt)
- [docs/guitar-practice.md](../../docs/guitar-practice.md)
- [modules/admin/__init__.py](../../modules/admin/__init__.py)
- [modules/admin/routes.py](../../modules/admin/routes.py)
- [modules/ai/__init__.py](../../modules/ai/__init__.py)
- [modules/ai/rag_sync.py](../../modules/ai/rag_sync.py)
- [modules/ai/services.py](../../modules/ai/services.py)
- [modules/auth/__init__.py](../../modules/auth/__init__.py)
- [modules/auth/mail.py](../../modules/auth/mail.py)
- [modules/auth/routes.py](../../modules/auth/routes.py)
- [modules/catalog/__init__.py](../../modules/catalog/__init__.py)
- [modules/catalog/routes.py](../../modules/catalog/routes.py)
- [modules/chatbot/__init__.py](../../modules/chatbot/__init__.py)
- [modules/chatbot/routes.py](../../modules/chatbot/routes.py)
- [modules/database/__init__.py](../../modules/database/__init__.py)
- [modules/database/connection.py](../../modules/database/connection.py)
- [modules/database/models.py](../../modules/database/models.py)
- [modules/lessons/__init__.py](../../modules/lessons/__init__.py)
- [modules/lessons/data.py](../../modules/lessons/data.py)
- [modules/lessons/routes.py](../../modules/lessons/routes.py)
- [modules/orders/__init__.py](../../modules/orders/__init__.py)
- [modules/orders/routes.py](../../modules/orders/routes.py)
- [modules/tuner/__init__.py](../../modules/tuner/__init__.py)
- [modules/tuner/routes.py](../../modules/tuner/routes.py)
- [templates/account/account.html](../../templates/account/account.html)
- [templates/admin/admin.html](../../templates/admin/admin.html)
- [templates/auth/auth.html](../../templates/auth/auth.html)
- [templates/catalog/storefront.html](../../templates/catalog/storefront.html)
- [templates/chatbot/chatbot.html](../../templates/chatbot/chatbot.html)
- [templates/landing/landing.html](../../templates/landing/landing.html)
- [templates/lessons/chord_detail.html](../../templates/lessons/chord_detail.html)
- [templates/lessons/chords.html](../../templates/lessons/chords.html)
- [templates/lessons/getting_started.html](../../templates/lessons/getting_started.html)
- [templates/lessons/index.html](../../templates/lessons/index.html)
- [templates/lessons/strumming.html](../../templates/lessons/strumming.html)
- [templates/shared/base.html](../../templates/shared/base.html)
- [templates/shared/components.html](../../templates/shared/components.html)
- [templates/shared/practice_base.html](../../templates/shared/practice_base.html)
- [templates/shared/practice_links.html](../../templates/shared/practice_links.html)
- [templates/tuner/tuner.html](../../templates/tuner/tuner.html)
- [tests/practice.cjs](../../tests/practice.cjs)
- [tests/serve.py](../../tests/serve.py)
- [tests/structure-browser.cjs](../../tests/structure-browser.cjs)
- [tests/test_ai.py](../../tests/test_ai.py)
- [tests/test_app.py](../../tests/test_app.py)
- [tests/test_practice.py](../../tests/test_practice.py)
- [tests/test_structure.py](../../tests/test_structure.py)
- [tests/tuner-pitch.cjs](../../tests/tuner-pitch.cjs)

## PROJECT_STRUCTURE.md

````markdown
# AUDIA project structure

AUDIA now groups its existing backend, templates, and frontend assets by
feature. This migration changes file locations and their imports/resource
references. It does not add features, change routes, redesign pages, alter
database schemas, or rewrite working application logic.

## What was difficult to navigate

- Backend feature files were siblings in `modules/`. Password-reset mail was
  separate from authentication, and RAG synchronization was separate from AI.
- Most templates, stylesheets, and browser controllers were flat files,
  while chatbot JavaScript and lesson templates already used feature folders.
- Shared layout/helpers/theme and feature-specific assets occupied the same
  directories. The shared practice layout was named like a separate feature.
- Existing architecture documentation described flat locations and did not
  provide a complete map of the current tuner, lessons, AI, and chatbot files.
- Auth (1,015 lines), AI (1,201 lines), storefront markup, and shared CSS are
  large, but splitting their logic would exceed a structure-only migration.
  They remain intact inside clear feature/shared folders.

No duplicate or obsolete source file was deleted on suspicion. The only
removed folder was the confirmed-empty `templates/practice/` after its two
shared templates moved. The previous guitar-practice source handoff is kept
unchanged under `docs/archive/`; it is a historical snapshot, not live code.
Existing uncommitted work was used as the baseline and preserved.

## Original project structure

This is the actual relevant tree captured before changes. Environment folders,
Git internals, local instance data, caches, and generated test results are
excluded; environment filenames are shown without their contents.

```text
AUDIA_V2/
|-- .vscode/
|   `-- settings.json
|-- assets/
|   |-- css/
|   |   |-- account.css
|   |   |-- admin.css
|   |   |-- auth.css
|   |   |-- landing.css
|   |   |-- lessons.css
|   |   |-- practice.css
|   |   |-- shared.css
|   |   |-- storefront.css
|   |   `-- tuner.css
|   |-- images/
|   |   |-- acoustic/
|   |   |   |-- Black_Cutaway.png
|   |   |   |-- Figured_Wood.png
|   |   |   |-- Mahogany_Orchestra.png
|   |   |   |-- Mahogany_Parlor.png
|   |   |   |-- Natural_Cutaway.png
|   |   |   |-- Natural_Dreadnought.png
|   |   |   |-- Natural_Orchestra.png
|   |   |   |-- Sunburst_Dreadnought.png
|   |   |   |-- Traditional_Natural.png
|   |   |   `-- Vintage_Sunburst.png
|   |   |-- bass/
|   |   |   |-- Burlwood.png
|   |   |   |-- Crimson_Red.png
|   |   |   |-- Ivory_Semi-Hollow.png
|   |   |   |-- Midnight_Black_Modern.png
|   |   |   |-- Natural_Jazz-Style.png
|   |   |   |-- Natural_Spalted.png
|   |   |   |-- Ocean_Blue_5-String.png
|   |   |   |-- Royal_Purple_5-String.png
|   |   |   |-- Seafoam_Green.png
|   |   |   `-- Sunburst_Vintage.png
|   |   |-- classical/
|   |   |   |-- Amber_Cedar.png
|   |   |   |-- Cream_Spruce.png
|   |   |   |-- Dark_Rosewood.png
|   |   |   |-- Golden_Amber.png
|   |   |   |-- Light_Spruce.png
|   |   |   |-- Natural_Spruce.png
|   |   |   |-- Orange_Cedar.png
|   |   |   |-- Pale_Spruce.png
|   |   |   |-- Walnut_Heritage.png
|   |   |   `-- Warm_Cedar.png
|   |   |-- electric/
|   |   |   |-- Amber_Flame.png
|   |   |   |-- Arctic_White.png
|   |   |   |-- Butterscotch.png
|   |   |   |-- Cherry_Red.png
|   |   |   |-- Cherry_Red_Double-Cut.png
|   |   |   |-- Midnight_Black.png
|   |   |   |-- Ocean_Blue.png
|   |   |   |-- Royal_Purple.png
|   |   |   |-- Seafoam.png
|   |   |   `-- Sunburst_Classic.png
|   |   |-- acoustic_studio.jpg
|   |   |-- bass_studio.jpg
|   |   |-- classical_studio.jpg
|   |   |-- electric_studio.jpg
|   |   |-- essentials.jpeg
|   |   |-- guitar_front.jpg
|   |   |-- guitar_performance.jpg
|   |   `-- SOURCES.md
|   |-- js/
|   |   |-- chatbot/
|   |   |   |-- chatbot-api.js
|   |   |   |-- chatbot-ui.js
|   |   |   `-- chatbot.js
|   |   |-- account.js
|   |   |-- admin.js
|   |   |-- app.js
|   |   |-- auth.js
|   |   |-- shared.js
|   |   |-- storefront.js
|   |   |-- theme.js
|   |   |-- tuner-pitch.js
|   |   `-- tuner.js
|   `-- icons-LICENSE.txt
|-- database/
|   `-- catalog.json
|-- docs/
|   |-- guitar-practice-source.md
|   `-- guitar-practice.md
|-- modules/
|   |-- __init__.py
|   |-- admin.py
|   |-- ai.py
|   |-- auth.py
|   |-- catalog.py
|   |-- chatbot.py
|   |-- database.py
|   |-- lessons.py
|   |-- lessons_content.py
|   |-- mail.py
|   |-- models.py
|   |-- orders.py
|   |-- rag_sync.py
|   `-- tuner.py
|-- templates/
|   |-- lessons/
|   |   |-- _chord_diagram.html
|   |   |-- chord_detail.html
|   |   |-- chords.html
|   |   |-- getting_started.html
|   |   |-- index.html
|   |   `-- strumming.html
|   |-- practice/
|   |   |-- base.html
|   |   `-- feature_links.html
|   |-- tuner/
|   |   `-- tuner.html
|   |-- account.html
|   |-- admin.html
|   |-- auth.html
|   |-- base.html
|   |-- chatbot.html
|   |-- landing.html
|   |-- shared.html
|   `-- storefront.html
|-- tests/
|   |-- browser.cjs
|   |-- chatbot.cjs
|   |-- practice.cjs
|   |-- serve.py
|   |-- support.py
|   |-- test_app.py
|   |-- test_practice.py
|   `-- tuner-pitch.cjs
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- debug.log
|-- README.md
`-- requirements.txt
```

Originally, `modules/` held the backend features, shared security, AI, mail,
and database code as flat siblings. `templates/` held page markup and shared
components, with only lessons and practice already grouped. `assets/css/`
and `assets/js/` combined shared and page-specific files; chatbot JavaScript
was already grouped. `assets/images/` already had useful guitar-category
folders. `database/` contained catalog seed data, `tests/` contained disposable
API/browser fixtures, and `docs/` held the guitar-practice guide and snapshot.
The root `app.py` composed the application and configuration.

## Final project structure

```text
AUDIA_V2/
|-- .vscode/
|   `-- settings.json
|-- assets/
|   |-- css/
|   |   |-- account/
|   |   |   `-- account.css
|   |   |-- admin/
|   |   |   `-- admin.css
|   |   |-- auth/
|   |   |   `-- auth.css
|   |   |-- catalog/
|   |   |   `-- storefront.css
|   |   |-- landing/
|   |   |   `-- landing.css
|   |   |-- lessons/
|   |   |   `-- lessons.css
|   |   |-- shared/
|   |   |   |-- practice.css
|   |   |   `-- shared.css
|   |   `-- tuner/
|   |       `-- tuner.css
|   |-- images/
|   |   |-- acoustic/
|   |   |   |-- Black_Cutaway.png
|   |   |   |-- Figured_Wood.png
|   |   |   |-- Mahogany_Orchestra.png
|   |   |   |-- Mahogany_Parlor.png
|   |   |   |-- Natural_Cutaway.png
|   |   |   |-- Natural_Dreadnought.png
|   |   |   |-- Natural_Orchestra.png
|   |   |   |-- Sunburst_Dreadnought.png
|   |   |   |-- Traditional_Natural.png
|   |   |   `-- Vintage_Sunburst.png
|   |   |-- bass/
|   |   |   |-- Burlwood.png
|   |   |   |-- Crimson_Red.png
|   |   |   |-- Ivory_Semi-Hollow.png
|   |   |   |-- Midnight_Black_Modern.png
|   |   |   |-- Natural_Jazz-Style.png
|   |   |   |-- Natural_Spalted.png
|   |   |   |-- Ocean_Blue_5-String.png
|   |   |   |-- Royal_Purple_5-String.png
|   |   |   |-- Seafoam_Green.png
|   |   |   `-- Sunburst_Vintage.png
|   |   |-- classical/
|   |   |   |-- Amber_Cedar.png
|   |   |   |-- Cream_Spruce.png
|   |   |   |-- Dark_Rosewood.png
|   |   |   |-- Golden_Amber.png
|   |   |   |-- Light_Spruce.png
|   |   |   |-- Natural_Spruce.png
|   |   |   |-- Orange_Cedar.png
|   |   |   |-- Pale_Spruce.png
|   |   |   |-- Walnut_Heritage.png
|   |   |   `-- Warm_Cedar.png
|   |   |-- electric/
|   |   |   |-- Amber_Flame.png
|   |   |   |-- Arctic_White.png
|   |   |   |-- Butterscotch.png
|   |   |   |-- Cherry_Red.png
|   |   |   |-- Cherry_Red_Double-Cut.png
|   |   |   |-- Midnight_Black.png
|   |   |   |-- Ocean_Blue.png
|   |   |   |-- Royal_Purple.png
|   |   |   |-- Seafoam.png
|   |   |   `-- Sunburst_Classic.png
|   |   |-- acoustic_studio.jpg
|   |   |-- bass_studio.jpg
|   |   |-- classical_studio.jpg
|   |   |-- electric_studio.jpg
|   |   |-- essentials.jpeg
|   |   |-- guitar_front.jpg
|   |   |-- guitar_performance.jpg
|   |   `-- SOURCES.md
|   |-- js/
|   |   |-- account/
|   |   |   `-- account.js
|   |   |-- admin/
|   |   |   `-- admin.js
|   |   |-- auth/
|   |   |   `-- auth.js
|   |   |-- catalog/
|   |   |   `-- storefront.js
|   |   |-- chatbot/
|   |   |   |-- chatbot-api.js
|   |   |   |-- chatbot-ui.js
|   |   |   `-- chatbot.js
|   |   |-- shared/
|   |   |   |-- app.js
|   |   |   |-- shared.js
|   |   |   `-- theme.js
|   |   `-- tuner/
|   |       |-- pitch.js
|   |       `-- tuner.js
|   `-- icons-LICENSE.txt
|-- database/
|   `-- catalog.json
|-- docs/
|   |-- architecture/
|   |   |-- after.json
|   |   |-- before.json
|   |   |-- migration.json
|   |   |-- removed-empty-folders.json
|   |   |-- routes-after.txt
|   |   |-- routes-before.txt
|   |   |-- tree-after.txt
|   |   |-- tree-before.txt
|   |   `-- updated-files.md
|   |-- archive/
|   |   `-- guitar-practice-source.md
|   `-- guitar-practice.md
|-- modules/
|   |-- admin/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- ai/
|   |   |-- __init__.py
|   |   |-- rag_sync.py
|   |   `-- services.py
|   |-- auth/
|   |   |-- __init__.py
|   |   |-- mail.py
|   |   `-- routes.py
|   |-- catalog/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- chatbot/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- database/
|   |   |-- __init__.py
|   |   |-- connection.py
|   |   `-- models.py
|   |-- lessons/
|   |   |-- __init__.py
|   |   |-- data.py
|   |   `-- routes.py
|   |-- orders/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- tuner/
|   |   |-- __init__.py
|   |   `-- routes.py
|   `-- __init__.py
|-- templates/
|   |-- account/
|   |   `-- account.html
|   |-- admin/
|   |   `-- admin.html
|   |-- auth/
|   |   `-- auth.html
|   |-- catalog/
|   |   `-- storefront.html
|   |-- chatbot/
|   |   `-- chatbot.html
|   |-- landing/
|   |   `-- landing.html
|   |-- lessons/
|   |   |-- _chord_diagram.html
|   |   |-- chord_detail.html
|   |   |-- chords.html
|   |   |-- getting_started.html
|   |   |-- index.html
|   |   `-- strumming.html
|   |-- shared/
|   |   |-- base.html
|   |   |-- components.html
|   |   |-- practice_base.html
|   |   `-- practice_links.html
|   `-- tuner/
|       `-- tuner.html
|-- tests/
|   |-- browser.cjs
|   |-- chatbot.cjs
|   |-- practice.cjs
|   |-- serve.py
|   |-- structure-browser.cjs
|   |-- support.py
|   |-- test_ai.py
|   |-- test_app.py
|   |-- test_practice.py
|   |-- test_structure.py
|   `-- tuner-pitch.cjs
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- debug.log
|-- PROJECT_STRUCTURE.md
|-- README.md
`-- requirements.txt
```

## Migration map: every moved file

| Original location | New location |
| --- | --- |
| `modules/auth.py` | `modules/auth/routes.py` |
| `modules/mail.py` | `modules/auth/mail.py` |
| `modules/catalog.py` | `modules/catalog/routes.py` |
| `modules/orders.py` | `modules/orders/routes.py` |
| `modules/admin.py` | `modules/admin/routes.py` |
| `modules/chatbot.py` | `modules/chatbot/routes.py` |
| `modules/ai.py` | `modules/ai/services.py` |
| `modules/rag_sync.py` | `modules/ai/rag_sync.py` |
| `modules/tuner.py` | `modules/tuner/routes.py` |
| `modules/lessons.py` | `modules/lessons/routes.py` |
| `modules/lessons_content.py` | `modules/lessons/data.py` |
| `modules/database.py` | `modules/database/connection.py` |
| `modules/models.py` | `modules/database/models.py` |
| `templates/base.html` | `templates/shared/base.html` |
| `templates/shared.html` | `templates/shared/components.html` |
| `templates/practice/base.html` | `templates/shared/practice_base.html` |
| `templates/practice/feature_links.html` | `templates/shared/practice_links.html` |
| `templates/auth.html` | `templates/auth/auth.html` |
| `templates/storefront.html` | `templates/catalog/storefront.html` |
| `templates/account.html` | `templates/account/account.html` |
| `templates/admin.html` | `templates/admin/admin.html` |
| `templates/chatbot.html` | `templates/chatbot/chatbot.html` |
| `templates/landing.html` | `templates/landing/landing.html` |
| `assets/css/auth.css` | `assets/css/auth/auth.css` |
| `assets/css/storefront.css` | `assets/css/catalog/storefront.css` |
| `assets/css/account.css` | `assets/css/account/account.css` |
| `assets/css/admin.css` | `assets/css/admin/admin.css` |
| `assets/css/landing.css` | `assets/css/landing/landing.css` |
| `assets/css/tuner.css` | `assets/css/tuner/tuner.css` |
| `assets/css/lessons.css` | `assets/css/lessons/lessons.css` |
| `assets/css/shared.css` | `assets/css/shared/shared.css` |
| `assets/css/practice.css` | `assets/css/shared/practice.css` |
| `assets/js/auth.js` | `assets/js/auth/auth.js` |
| `assets/js/storefront.js` | `assets/js/catalog/storefront.js` |
| `assets/js/account.js` | `assets/js/account/account.js` |
| `assets/js/admin.js` | `assets/js/admin/admin.js` |
| `assets/js/tuner.js` | `assets/js/tuner/tuner.js` |
| `assets/js/tuner-pitch.js` | `assets/js/tuner/pitch.js` |
| `assets/js/app.js` | `assets/js/shared/app.js` |
| `assets/js/shared.js` | `assets/js/shared/shared.js` |
| `assets/js/theme.js` | `assets/js/shared/theme.js` |
| `docs/guitar-practice-source.md` | `docs/archive/guitar-practice-source.md` |

Existing lessons HTML and chatbot JavaScript already had feature folders and
were retained there. No duplicate copies or compatibility stub files were
created at old locations. Package `__init__.py` files expose the existing
blueprints/services, so imports such as `from modules.auth import auth` still
work. Model imports now use `modules.database.models`; RAG sync uses
`modules.ai.rag_sync`.

## Where to work on each feature

| Area | Backend | Templates | CSS / JavaScript |
| --- | --- | --- | --- |
| Authentication, sessions, profile, passwords | `modules/auth/routes.py`; reset delivery in `modules/auth/mail.py` | `templates/auth/auth.html`; account forms in `templates/account/account.html` | `assets/css/auth/`, `assets/js/auth/`; account assets in `assets/css/account/`, `assets/js/account/` |
| Catalog, products, recommendations, saved instruments | `modules/catalog/routes.py` | `templates/catalog/storefront.html` | `assets/css/catalog/`, `assets/js/catalog/` |
| Orders and purchasing | `modules/orders/routes.py` | Existing checkout/cart markup in catalog; order cards in account; reusable order detail in shared components | Existing catalog/account controllers and shared `orderDetails()` helper |
| Administration | `modules/admin/routes.py` | `templates/admin/admin.html` | `assets/css/admin/`, `assets/js/admin/` |
| Chatbot HTTP/UI interface | `modules/chatbot/routes.py` | `templates/chatbot/chatbot.html` | `assets/js/chatbot/`; existing chat CSS stays in `assets/css/shared/shared.css` |
| Gemini, embeddings, filters, retrieval, enrichment, prompts | `modules/ai/services.py` | Uses chatbot UI | No browser credentials or AI implementation |
| Product RAG synchronization | `modules/ai/rag_sync.py`; unchanged `flask --app app sync-rag` command | — | — |
| Guitar Tuner | `modules/tuner/routes.py` | `templates/tuner/tuner.html` | `assets/css/tuner/tuner.css`, `assets/js/tuner/tuner.js`, `assets/js/tuner/pitch.js` |
| Guitar Lessons | `modules/lessons/routes.py`; chord/pattern data in `modules/lessons/data.py` | `templates/lessons/`; reusable `_chord_diagram.html` macro | `assets/css/lessons/lessons.css`; static pages need no separate JavaScript |
| Public landing | Existing page function in `app.py` | `templates/landing/landing.html` | `assets/css/landing/landing.css`; startup behavior in shared app controller |
| Shared HTML | — | `templates/shared/base.html`, `components.html`, `practice_base.html`, `practice_links.html` | — |
| Shared frontend helpers and theme | — | Shared base loads assets | `assets/js/shared/{app.js, shared.js, theme.js}`, `assets/css/shared/{shared.css, practice.css}` |
| Images | Catalog paths and seed data retain existing image URLs | Existing local image references | `assets/images/`; category folders and all product filenames stay unchanged |
| Database | `modules/database/connection.py`, `modules/database/models.py` | No database work in templates | Seed stays in `database/catalog.json`; configuration remains in `.env` and `app.py` |

There is one shared database, not one per feature. PostgreSQL configuration,
SQLAlchemy fields/relationships, queries, initialization, and catalog seeding
are unchanged. The models, connection implementation, lesson content, tuner
pitch algorithm, shared stylesheet, and images retain their original bytes.

`app.py` still loads configuration before importing AI, creates the app,
initializes the database, registers the seven existing blueprints once,
installs security, and keeps the existing entry-page/CLI/global-error-handler
functions. Moving those page functions into new blueprints would complicate
endpoint compatibility, so they remain where they were.

The request security hooks remain in `modules/auth/routes.py`. Their session
restoration, CSRF validation, authorization, cookie handling, and password
behavior are unchanged. The chatbot still calls AI/RAG; it does not own Gemini
configuration or embeddings. Browser tuner audio still stays local.

## Files created

The nine feature/shared-backend packages each have a small `__init__.py`:
`modules/auth/`, `catalog/`, `orders/`, `admin/`, `chatbot/`, `ai/`, `tuner/`,
`lessons/`, and `database/`. These import and expose existing objects; they
do not redefine blueprints or add business logic.

Architecture and verification support:

- `PROJECT_STRUCTURE.md`: this guide, trees, migration, and verification.
- `docs/architecture/before.json`: original fingerprints, blueprints, and
  complete route contracts, recorded before moves.
- `docs/architecture/after.json`: final route contract and file-change summary.
- `docs/architecture/migration.json`: machine-readable 42-file migration map.
- `docs/architecture/tree-before.txt` and `tree-after.txt`: actual source trees.
- `docs/architecture/routes-before.txt` and `routes-after.txt`: Flask CLI maps.
- `docs/architecture/removed-empty-folders.json`: confirmed-empty folder removed.
- `docs/architecture/updated-files.md`: complete versions of changed existing
  files and newly created source/support files, rather than snippets.
- `tests/test_structure.py`: exact route comparison, original Python-logic and
  frontend-content preservation, file completeness, and local import checks.
- `tests/test_ai.py`: actual chatbot/RAG/SQL/enrichment pipeline with only the
  Gemini provider mocked; no paid API call.
- `tests/structure-browser.cjs`: before/after desktop/mobile screenshot check.

## Files whose contents changed

| Current file | Reason |
| --- | --- |
| `modules/admin/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/ai/services.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/auth/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/catalog/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/lessons/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/orders/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/ai/rag_sync.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `modules/tuner/routes.py` | Update imports for the feature package and shared database; page modules also use moved stylesheet paths. |
| `templates/account/account.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/admin/admin.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/auth/auth.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/shared/base.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/landing/landing.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/lessons/chord_detail.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/lessons/chords.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/lessons/getting_started.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/lessons/index.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/lessons/strumming.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/shared/practice_base.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/catalog/storefront.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `templates/tuner/tuner.html` | Update shared extends/includes and moved static asset references; markup stays unchanged. |
| `assets/css/account/account.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/admin/admin.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/auth/auth.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/landing/landing.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/lessons/lessons.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/catalog/storefront.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/css/tuner/tuner.css` | Update file-location comments and, for practice pages, the shared stylesheet import; rules stay unchanged. |
| `assets/js/account/account.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/admin/admin.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/shared/app.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/auth/auth.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/chatbot/chatbot-ui.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/catalog/storefront.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `assets/js/tuner/tuner.js` | Update relative imports for moved controllers/helpers/pitch module; behavior stays unchanged. |
| `tests/practice.cjs` | Wait for SVG dimensions after viewport resize before retaining all original layout assertions (test only). |
| `tests/serve.py` | Update model imports or tested static asset paths for their new locations. |
| `tests/test_app.py` | Update model imports or tested static asset paths for their new locations. |
| `tests/test_practice.py` | Update model imports or tested static asset paths for their new locations. |
| `tests/tuner-pitch.cjs` | Update model imports or tested static asset paths for their new locations. |
| `docs/guitar-practice.md` | Document current feature folders and replace outdated live source paths; preserve the historical snapshot. |
| `app.py` | Update model/RAG imports and moved page template/stylesheet paths; registration stays identical. |
| `README.md` | Document current feature folders and replace outdated live source paths; preserve the historical snapshot. |

Other migrated files were moved without changing their bytes. Every one of
the 117 original inventoried files remains at its original or mapped location.
The complete updated source is available in
[updated-files.md](docs/architecture/updated-files.md).

## Route comparison

All **45 route entries**, including the static route, retain their endpoint
names, paths, and method sets. All seven blueprint names and registration
order are preserved: `auth`, `catalog`, `orders`, `admin`, `chatbot`, `tuner`,
and `lessons`. The structural test also compares HEAD and OPTIONS behavior.

Before (`python -m flask --app app routes`):

```text
Endpoint                 Methods   Rule                                
-----------------------  --------  ------------------------------------
account_page             GET       /account                            
admin.add_product        POST      /api/admin/products                 
admin.archive_product    DELETE    /api/admin/products/<int:product_id>
admin.customers          GET       /api/admin/customers                
admin.edit_product       PUT       /api/admin/products/<int:product_id>
admin.export_sales       GET       /api/admin/sales/export             
admin.products           GET       /api/admin/products                 
admin.sales              GET       /api/admin/sales                    
admin.settings           GET, PUT  /api/admin/settings                 
admin.summary            GET       /api/admin/summary                  
admin.update_order       PATCH     /api/admin/sales/<order_id>         
auth.change_password     POST      /api/auth/password                  
auth.current_session     GET       /api/auth/session                   
auth.forgot_password     POST      /api/auth/forgot-password           
auth.login               POST      /api/auth/login                     
auth.logout              POST      /api/auth/logout                    
auth.profile             PATCH     /api/auth/profile                   
auth.register            POST      /api/auth/register                  
auth.reset_password      POST      /api/auth/reset-password            
catalog.finder           POST      /api/finder                         
catalog.product          GET       /api/products/<int:product_id>      
catalog.products         GET       /api/products                       
catalog.save             PUT       /api/account/saved/<int:product_id> 
catalog.saved            GET       /api/account/saved                  
catalog.store_info       GET       /api/store                          
catalog.unsave           DELETE    /api/account/saved/<int:product_id> 
chatbot.chat             POST      /api/chat                           
chatbot.chat_status      GET       /api/chat                           
dashboard                GET       /admin                              
health                   GET       /api/health                         
index                    GET       /                                   
lessons.chord_detail     GET       /lessons/chords/<slug>              
lessons.chords           GET       /lessons/chords                     
lessons.getting_started  GET       /lessons/getting-started            
lessons.index            GET       /lessons                            
lessons.strumming        GET       /lessons/strumming                  
login_page               GET       /login                              
orders.checkout          POST      /api/orders                         
orders.detail            GET       /api/orders/<order_id>              
orders.history           GET       /api/orders                         
register_page            GET       /register                           
reset_password_page      GET       /reset-password                     
shop                     GET       /shop                               
static                   GET       /static/<path:filename>             
tuner.index              GET       /tuner
```

After (same command):

```text
Endpoint                 Methods   Rule                                
-----------------------  --------  ------------------------------------
account_page             GET       /account                            
admin.add_product        POST      /api/admin/products                 
admin.archive_product    DELETE    /api/admin/products/<int:product_id>
admin.customers          GET       /api/admin/customers                
admin.edit_product       PUT       /api/admin/products/<int:product_id>
admin.export_sales       GET       /api/admin/sales/export             
admin.products           GET       /api/admin/products                 
admin.sales              GET       /api/admin/sales                    
admin.settings           GET, PUT  /api/admin/settings                 
admin.summary            GET       /api/admin/summary                  
admin.update_order       PATCH     /api/admin/sales/<order_id>         
auth.change_password     POST      /api/auth/password                  
auth.current_session     GET       /api/auth/session                   
auth.forgot_password     POST      /api/auth/forgot-password           
auth.login               POST      /api/auth/login                     
auth.logout              POST      /api/auth/logout                    
auth.profile             PATCH     /api/auth/profile                   
auth.register            POST      /api/auth/register                  
auth.reset_password      POST      /api/auth/reset-password            
catalog.finder           POST      /api/finder                         
catalog.product          GET       /api/products/<int:product_id>      
catalog.products         GET       /api/products                       
catalog.save             PUT       /api/account/saved/<int:product_id> 
catalog.saved            GET       /api/account/saved                  
catalog.store_info       GET       /api/store                          
catalog.unsave           DELETE    /api/account/saved/<int:product_id> 
chatbot.chat             POST      /api/chat                           
chatbot.chat_status      GET       /api/chat                           
dashboard                GET       /admin                              
health                   GET       /api/health                         
index                    GET       /                                   
lessons.chord_detail     GET       /lessons/chords/<slug>              
lessons.chords           GET       /lessons/chords                     
lessons.getting_started  GET       /lessons/getting-started            
lessons.index            GET       /lessons                            
lessons.strumming        GET       /lessons/strumming                  
login_page               GET       /login                              
orders.checkout          POST      /api/orders                         
orders.detail            GET       /api/orders/<order_id>              
orders.history           GET       /api/orders                         
register_page            GET       /register                           
reset_password_page      GET       /reset-password                     
shop                     GET       /shop                               
static                   GET       /static/<path:filename>             
tuner.index              GET       /tuner
```

The two CLI outputs match. The generic `/static/<path:filename>` route remains
the same; CSS/JS filenames now follow their feature folders and all references
were updated. Product image filenames and `/static/images/...` URLs remain
unchanged, including paths stored in catalog/database records.

## Verification

- The original 24 server tests passed before changes, after backend moves,
  and after the full migration. The final suite has **29 passing tests**,
  including three structure checks and two offline AI pipeline checks.
- Original Python non-import logic is compared against the recorded AST
  fingerprint after canonicalizing only changed resource paths. Original
  frontend content is compared against byte fingerprints after undoing the
  explicit import/include/path substitutions. This includes all CSS rules,
  template markup, browser controllers, lesson content, and image files.
- The application imports and compiles without missing modules or circular
  imports. Each feature-stage route check matched the original map. The
  normal `flask --app app run --no-reload` entry point starts; `/login` returned
  HTTP 200. Fixture tests render actual application routes with disposable data.
- **56 before/after screenshot cases** cover guest/member landing, auth pages,
  store, account, admin, tuner, and lesson pages at 375 and 1440 pixels in both
  themes. Appearance is unchanged. Comparison allows only compositor rounding
  of at most 2/255 per channel in at most 0.1% of pixels. All assets load and
  there are no page errors.
- Existing storefront/account/admin browser tests pass: registration, login,
  logout, profile, password/recovery, session revocation, products/filtering,
  images, recommendations, saved instruments, checkout, orders, inventory,
  sales, customers, reports, settings, export, responsive layouts, and themes.
- Existing chatbot browser tests pass: guests/members, safe answers, Unicode,
  Send/Enter, duplicate prevention, typing, errors, and the single CSRF retry.
- Existing guitar-practice browser tests verify the microphone lifecycle,
  real Web Audio pitch readings, note/meter states, permissions/errors,
  silence recovery, lessons, eight diagrams, strumming counts, and 130 layout
  cases at 320, 375, 768, 1024, and 1440 pixels in both themes.
  A test-only readiness wait now allows Chromium to finish resizing SVGs
  before reading their dimensions. It fixes an observed intermittent stale
  measurement (166 px briefly, then 240 px). Every original assertion remains;
  no application style or behavior was changed to address this timing issue.
- All **90 synthetic harmonic pitch cases** pass across six strings, three
  sample rates, and flat/in-tune/sharp offsets, plus noise/stabilization cases.

No live Gemini call or production-database mutation was made. AI verification
uses real application retrieval/enrichment code with disposable SQL data and
mock provider responses. Physical microphone/guitar behavior and Safari/Firefox
remain the same manual-verification limits as before this refactor.

## Run and recheck

Normal development remains:

```powershell
.venv/Scripts/python.exe app.py
# Or:
.venv/Scripts/python.exe -m flask --app app run --no-reload
```

Use the existing `.env`, PostgreSQL, mail, and Gemini configuration. No runtime
dependency, environment setting, or schema migration was introduced.

```powershell
.venv/Scripts/python.exe -m flask --app app routes
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py'
node tests/tuner-pitch.cjs
```

Browser verification uses a disposable server, never the customer database:

```powershell
# Terminal 1
.venv/Scripts/python.exe tests/serve.py

# Terminal 2, with Playwright installed or PLAYWRIGHT_MODULE set
node tests/browser.cjs
node tests/chatbot.cjs
node tests/practice.cjs
```

The visual baseline is stored in ignored `test-results/architecture/screens/`.
To compare it again, start a fresh disposable fixture before running the
screenshot test, so the expected account/admin data is unchanged:

```powershell
$env:STRUCTURE_PHASE = 'after'
node tests/structure-browser.cjs
```

The historical `before` screenshots are retained for review. Running with
`STRUCTURE_PHASE=before` intentionally captures a new baseline. The snapshot
contract in `before.json` documents this migration; a future behavior change
should update that contract deliberately, rather than bypassing it.

````

## README.md

````markdown
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

```text
app.py                       Flask app, settings, @app.route pages, CLI, entry point
modules/
  auth/                      Authentication, request security, password reset mail
  catalog/                   Catalog, recommendations, saved instruments, support
  orders/                    Customer checkout and order access
  admin/                     Protected store operations and reporting
  chatbot/                   AUDIA Assistant HTTP interface
  ai/                        Gemini, embeddings, RAG, and knowledge synchronization
  tuner/                     Existing guitar tuner page
  lessons/                   Existing lesson routes and static chord/pattern data
  database/                  Shared connection lifecycle, initialization, and models
database/catalog.json        School-project catalog seed
templates/
  shared/                    Shared document, icons, dialogs, and practice layout
  landing/                   Public overview and account entry points
  auth/                      Login, registration and password recovery
  catalog/                   Shop, product cards, cart, checkout, and finder
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
docs/architecture/           Migration map, route snapshots, and updated source
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
| `/shop` | `catalog/storefront.html` | `catalog/storefront.css` | `catalog/storefront.js` |
| `/account` | `account/account.html` | `account/account.css` | `account/account.js` |
| `/admin` | `admin/admin.html` | `admin/admin.css` | `admin/admin.js` |
| `/tuner` | `tuner/tuner.html` | `tuner/tuner.css` | `tuner/tuner.js`, `tuner/pitch.js` |
| `/lessons` and lesson details | `lessons/` | `lessons/lessons.css` | Static Jinja pages; no separate controller |

For example, to change a product card, edit `templates/catalog/storefront.html` and `assets/css/catalog/storefront.css`. Cart, checkout, and finder markup and styles remain in those same files. The chatbot has its own included template. The administration page similarly keeps its related sections together. Comment headings mark the sections. Repeated cards and popups use HTML `<template>` blocks within their page file; JavaScript fills them with data from the API.

`templates/shared/components.html`, `assets/css/shared/shared.css`, and `assets/js/shared/shared.js` contain elements used by several pages. `assets/js/shared/app.js` starts the current page and handles navigation, sign-out, and theme controls. `assets/js/shared/theme.js` applies the saved theme before the page appears. Flask still serves assets at `/static/`. Templates do not contain inline CSS; shared animation helpers apply movement styles at runtime.

Each backend feature has a folder under `modules/`, with a small `__init__.py` exposing its existing blueprint or services. Forms and interactive controls call the unchanged `/api/...` endpoints. To change account creation, edit `modules/auth/routes.py`; to change an existing entry page's template, edit `app.py`. Database credentials stay in `.env`. Test-only app construction is in `tests/support.py`.

## Chatbot: where to edit

The existing chat design is available on the public landing page and in the signed-in shop. Its markup is in `templates/chatbot/chatbot.html`, included by both pages. Chat styling lives under the `Chat` comment in `assets/css/shared/shared.css`. The public chat does not unlock the catalog, cart or checkout.

All chatbot JavaScript is grouped under `assets/js/chatbot/` (Flask serves the `assets` folder as `/static`):

| File | Purpose and functions to look at |
| --- | --- |
| `chatbot-api.js` | Flask requests only. `getSession()` loads the session and CSRF token; `refreshCsrfToken()` reloads it; `sendChatMessage()` posts the message and retries a rejected CSRF request once. `requestJson()` handles JSON, timeouts and network failures. |
| `chatbot-ui.js` | DOM only. `addUserMessage()` and `addAssistantMessage()` display safe text; `showTypingIndicator()`, `hideTypingIndicator()` and `setChatLoading()` control the waiting state; `showError()` displays a friendly error. |
| `chatbot.js` | `initChatbot()` connects existing buttons and the form. Its `sendMessage()` validates input, prevents duplicate submissions, calls the API and restores the form in `finally`. |

`assets/js/shared/app.js` calls `initChatbot()` after the page starts. The controller obtains `/api/auth/session`, then sends `{ "message": "..." }` to the existing `/api/chat` route with same-origin cookies, a CSRF header and UTF-8 JSON. Flask's existing `modules/chatbot/routes.py` calls `modules/ai/services.py`; only the returned `answer` appears in the chat. Sources, SQL filters and internal errors are not rendered. Gemini credentials stay on the server. CSRF tokens stay in JavaScript memory.

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

````

## app.py

```python
import os
import secrets
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import URL, text
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------
# 1. Load environment variables FIRST
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")


# ---------------------------------------------------------
# 2. Import AUDIA modules AFTER .env has been loaded
# ---------------------------------------------------------

from modules.admin import admin
from modules.auth import (
    auth,
    install_security,
    validate_email,
    validate_password,
)
from modules.catalog import catalog
from modules.chatbot import chatbot
from modules.database import db, init_database, initialize
from modules.database.models import User
from modules.orders import orders
from modules.tuner import tuner
from modules.lessons import lessons


# ---------------------------------------------------------
# 3. Create Flask application
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="assets",
    static_url_path="/static",
    template_folder="templates",
    instance_path=str(ROOT / "instance"),
)


# ---------------------------------------------------------
# 4. Build PostgreSQL database URL
# ---------------------------------------------------------

def build_database_url():
    """
    Build the PostgreSQL URL from the separate
    credentials stored in .env.

    Falls back to DATABASE_URL if the separate
    credentials are not available.
    """

    required_variables = (
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    )

    if not all(
        os.getenv(name)
        for name in required_variables
    ):
        return os.getenv(
            "DATABASE_URL",
            "",
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "DB_PORT",
                "5432",
            )
        ),
        database=os.getenv("DB_NAME"),
    )


# ---------------------------------------------------------
# 5. Application configuration
# ---------------------------------------------------------

app.config.update(
    DATABASE_URL=build_database_url(),

    SECRET_KEY=os.getenv(
        "SECRET_KEY"
    ),

    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",

    SESSION_COOKIE_SECURE=(
        os.getenv(
            "COOKIE_SECURE",
            "false",
        ).lower()
        == "true"
    ),

    PERMANENT_SESSION_LIFETIME=timedelta(
        days=30
    ),

    MAX_CONTENT_LENGTH=64 * 1024,

    MAIL_BACKEND=os.getenv(
        "MAIL_BACKEND",
        "disabled",
    ),

    SMTP_HOST=os.getenv(
        "SMTP_HOST",
        "",
    ),

    SMTP_PORT=int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    ),

    SMTP_USER=os.getenv(
        "SMTP_USER",
        "",
    ),

    SMTP_PASSWORD=os.getenv(
        "SMTP_PASSWORD",
        "",
    ),

    SMTP_FROM=os.getenv(
        "SMTP_FROM",
        "noreply@audia.local",
    ),

    APP_URL=os.getenv(
        "APP_URL",
        "http://localhost:5000",
    ).rstrip("/"),
)


# ---------------------------------------------------------
# 6. Secret key fallback
# ---------------------------------------------------------

if not app.config["SECRET_KEY"]:

    Path(
        app.instance_path
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    key_file = (
        Path(app.instance_path)
        / ".secret-key"
    )

    try:
        with key_file.open(
            "x",
            encoding="utf-8",
        ) as file:

            file.write(
                secrets.token_hex(32)
            )

    except FileExistsError:
        pass

    app.config["SECRET_KEY"] = (
        key_file.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------
# 7. Initialize PostgreSQL
# ---------------------------------------------------------

init_database(app)


# ---------------------------------------------------------
# 8. Register blueprints
# ---------------------------------------------------------

app.register_blueprint(auth)
app.register_blueprint(catalog)
app.register_blueprint(orders)
app.register_blueprint(admin)

# Gemini chatbot
app.register_blueprint(chatbot)
app.register_blueprint(tuner)
app.register_blueprint(lessons)


# Install authentication/security hooks
install_security(app)


# ---------------------------------------------------------
# 9. Pages
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "landing/landing.html",
        title="Find your sound",
        page_name="landing",
        stylesheet="landing/landing",
    )


@app.route("/login")
def login_page():

    if g.user:
        return redirect(
            url_for(
                "dashboard"
                if g.user.role == "admin"
                else "shop"
            )
        )

    mode = (
        "admin"
        if request.args.get("role") == "admin"
        else "login"
    )

    return render_template(
        "auth/auth.html",
        title="Sign in",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode=mode,
    )


@app.route("/register")
def register_page():

    if g.user:
        return redirect(
            url_for("shop")
        )

    return render_template(
        "auth/auth.html",
        title="Create an account",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode="register",
    )


@app.route("/reset-password")
def reset_password_page():

    return render_template(
        "auth/auth.html",
        title="Reset your password",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode="reset",
        reset_token=request.args.get(
            "token",
            "",
        ),
    )


@app.route("/shop")
def shop():

    if not g.user:
        return redirect(
            url_for("login_page")
        )

    return render_template(
        "catalog/storefront.html",
        title="Guitar shop",
        page_name="storefront",
        stylesheet="catalog/storefront",
    )


@app.route("/account")
def account_page():

    if not g.user:
        return redirect(
            url_for("login_page")
        )

    return render_template(
        "account/account.html",
        title="My account",
        page_name="account",
        stylesheet="account/account",
    )


@app.route("/admin")
def dashboard():

    if not g.user:
        return redirect(
            url_for(
                "login_page",
                role="admin",
            )
        )

    if g.user.role != "admin":
        return redirect(
            url_for("shop")
        )

    return render_template(
        "admin/admin.html",
        title="Administration",
        page_name="dashboard",
        stylesheet="admin/admin",
    )


# ---------------------------------------------------------
# 10. Health endpoint
# ---------------------------------------------------------

@app.route("/api/health")
def health():

    if "engine" not in current_app.extensions:

        return jsonify(
            status="setup_required",
            database="not_configured",
        ), 503

    db().execute(
        text("SELECT 1")
    )

    return jsonify(
        status="ok",
        service="AUDIA",
        database="connected",
    )

# ---------------------------------------------------------
# 11. Error handlers
# ---------------------------------------------------------

@app.errorhandler(
    OperationalError
)
def database_unavailable(error):

    if g.get("db"):
        g.db.rollback()

    return jsonify(
        error=(
            "The database is unavailable. "
            "Please try again shortly."
        )
    ), 503


@app.errorhandler(503)
def service_unavailable(error):

    return jsonify(
        error=(
            "Account and order services "
            "are not available yet. "
            "Please try again later."
        )
    ), 503


@app.errorhandler(413)
def request_too_large(error):

    return jsonify(
        error="This request is too large."
    ), 413


# ---------------------------------------------------------
# 12. CLI: initialize database
# ---------------------------------------------------------

@app.cli.command(
    "init-db"
)
def init_db():
    """
    Create missing tables and seed an empty
    catalog without deleting existing data.
    """

    initialize(
        current_app
    )

    click.echo(
        "Database ready. "
        "Catalog seed applied where needed."
    )


# ---------------------------------------------------------
# 13. CLI: create administrator
# ---------------------------------------------------------

@app.cli.command(
    "create-admin"
)
@click.option(
    "--email",
    prompt=True,
)
@click.option(
    "--name",
    default="AUDIA Admin",
    prompt=True,
)
@click.password_option()
def create_admin(
    email,
    name,
    password,
):

    try:

        email = validate_email(
            email
        )

        validate_password(
            password
        )

    except ValueError as error:

        raise click.ClickException(
            str(error)
        ) from error

    existing_user = (
        db()
        .query(User)
        .filter_by(
            email=email
        )
        .first()
    )

    if existing_user:

        raise click.ClickException(
            "That email already exists; "
            "no account was changed."
        )

    admin_user = User(
        name=name.strip(),
        email=email,
        password_hash=generate_password_hash(
            password
        ),
        role="admin",
    )

    db().add(
        admin_user
    )

    db().commit()

    click.echo(
        "Administrator created."
    )

@app.cli.command("sync-rag")
def sync_rag():
    """
    Synchronize AUDIA product knowledge
    with the RAG database.
    """

    from modules.ai.rag_sync import (
        sync_products_to_rag,
    )

    try:

        result = sync_products_to_rag()

        click.echo(
            f"RAG synchronization complete. "
            f"{result['indexed']} products indexed, "
            f"{result['removed']} stale documents removed."
        )

    except Exception:

        db().rollback()

        current_app.logger.exception(
            "RAG synchronization failed."
        )

        raise click.ClickException(
            "RAG synchronization failed. "
            "Check the error above."
        )
# ---------------------------------------------------------
# 14. Run development server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",

        port=int(
            os.getenv(
                "PORT",
                "5000",
            )
        ),

        debug=(
            os.getenv(
                "FLASK_DEBUG",
                "0",
            )
            == "1"
        ),
    )

```

## assets/css/account/account.css

```css
/* Styles for templates/account/account.html. */

/* Account */
.account-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding-block: 24px;
  border-bottom: 1px solid var(--line);
}
.account-main {
  padding-block: 48px 80px;
}
.account-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
  margin-top: 32px;
}
.account-section {
  padding: 28px;
  min-width: 0;
}
.account-orders {
  margin-top: 20px;
}
.account-order {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 22px 0;
  border-bottom: 1px solid var(--line);
}
.account-order:last-child {
  border: 0;
}
.account-order-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
}
.saved-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
  margin-top: 24px;
}
.saved-item {
  display: flex;
  gap: 16px;
  align-items: center;
  min-width: 0;
}
.saved-item img {
  width: 80px;
  height: 110px;
  object-fit: cover;
  border-radius: 9px;
}
.saved-item > div {
  min-width: 0;
}
.saved-item .form-actions {
  justify-content: flex-start;
}
.finder-profile-summary {
  margin-top: 28px;
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--line);
  padding-top: 24px;
}
@media (max-width: 639px) {
  .account-header {
    align-items: start;
    flex-direction: column;
  }
  .account-header .secondary-btn {
    font-size: 11px;
    padding: 10px;
  }
  .account-grid,
  .saved-grid {
    grid-template-columns: 1fr;
  }
  .account-section {
    padding: 20px;
  }
  .account-order,
  .finder-profile-summary {
    align-items: start;
    flex-direction: column;
  }
}

```

## assets/css/admin/admin.css

```css
/* Styles for templates/admin/admin.html. */

/* Dashboard */
.admin-page {
  background-image: radial-gradient(
    ellipse at 95% 0%,
    #a77ce310,
    transparent 50%
  );
}

.admin-page aside {
  border-color: var(--line);
  background: var(--surface);
}

.admin-page aside nav button {
  border-radius: 7px;
}

.admin-page aside nav button.bg-zinc-950 {
  color: var(--accent);
  background: var(--soft);
  box-shadow: inset 3px 0 var(--accent);
}

.admin-page main {
  max-width: 1760px;
  margin-inline: auto;
}

.admin-page main > div,
.admin-page .grid > *,
.admin-page .surface-card {
  min-width: 0;
}

.admin-page thead {
  background: var(--soft);
}

.admin-page th {
  color: var(--muted);
}

.admin-page td {
  font-variant-numeric: tabular-nums;
}

/* Overview */
.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: "";
  position: absolute;
  width: 90px;
  height: 90px;
  right: -25px;
  bottom: -40px;
  border: 1px solid var(--line);
  border-radius: 50%;
  box-shadow:
    0 0 0 15px color-mix(in srgb, var(--line) 25%, transparent),
    0 0 0 30px color-mix(in srgb, var(--line) 12%, transparent);
  pointer-events: none;
}

.stat-card > p:last-child {
  font-size: clamp(1.5rem, 2.3vw, 2rem);
  letter-spacing: -0.055em;
  font-variant-numeric: tabular-nums;
}

.revenue-chart > div:nth-child(2) {
  background: repeating-linear-gradient(
    to top,
    var(--line) 0 1px,
    transparent 1px 25%
  );
  padding-top: 12px;
}

.revenue-chart > div:nth-child(2) .bg-zinc-200 {
  background: color-mix(in srgb, var(--accent) 22%, var(--surface));
}

.revenue-chart > div:nth-child(2) .bg-violet-500 {
  background: linear-gradient(to top, #7143d6, #bb9bff);
}

.dark .revenue-chart > div:nth-child(2) .bg-violet-500 {
  background: linear-gradient(to top, #80b89a, #c9ffdf);
}

.report-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
.stat-glyph {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  font-size: 22px;
  color: var(--accent);
  background: var(--soft);
}
.revenue-plot {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 24px;
}
.revenue-plot svg {
  width: 100%;
  overflow: visible;
}
.revenue-plot rect {
  fill: var(--accent);
  opacity: 0.8;
}
.revenue-chart select {
  min-width: 100px;
  padding-block: 8px;
  font-size: 12px;
  background: var(--surface);
  color: var(--text);
}
.category-report {
  display: grid;
  gap: 25px;
  margin-top: 30px;
  font-size: 12px;
}
.category-report meter {
  width: 100%;
  height: 12px;
  margin-top: 8px;
}
.category-report meter::-webkit-meter-bar {
  border: 0;
  background: var(--soft);
}
.category-report meter::-webkit-meter-optimum-value {
  background: var(--accent);
}
.category-report meter::-moz-meter-bar {
  background: var(--accent);
}
@media (max-width: 1023px) {
  .report-grid {
    grid-template-columns: 1fr;
  }
}

/* Admin Products */
.admin-section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
[data-field="admin-products"] .secondary-btn {
  padding: 9px 12px;
  font-size: 11px;
}
[data-field="admin-products"] h3 {
  overflow-wrap: anywhere;
}
@media (max-width: 639px) {
  .admin-section-heading {
    align-items: start;
    flex-wrap: wrap;
  }
}

/* Settings */
.settings-panel {
  max-width: 660px;
  padding: 30px;
}
.settings-security {
  margin-top: 30px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}

/* Notifications */
.notification-list {
  margin-top: 20px;
  display: grid;
  gap: 14px;
  font-size: 13px;
}
.notification-list li {
  padding: 14px;
  border-radius: 9px;
  background: var(--soft);
}

/* Order Status */
.status-delivered {
  color: var(--mint);
}
.status-cancelled,
.status-refunded {
  color: #be123c;
  background: #fb71851a;
}
.dark .status-cancelled,
.dark .status-refunded {
  color: #fda4af;
}
.status-pending {
  color: #a16207;
  background: #fbbf241a;
}
.dark .status-pending {
  color: #fde68a;
}

/* Responsive layout */
@media (max-width: 639px) {
  .admin-page main {
    padding: 20px 16px;
  }
  .admin-page header {
    padding-inline: 12px;
  }
  .admin-page main > div > .flex {
    flex-wrap: wrap;
    gap: 16px;
  }
  .admin-page .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .stat-card {
    padding: 16px;
  }
  .stat-card > div {
    gap: 8px;
    flex-wrap: wrap;
  }
  .stat-card > p:last-child {
    font-size: 23px;
  }
  .revenue-chart > div:first-child {
    flex-wrap: wrap;
    gap: 16px;
  }
}
@media (max-width: 359px) {
  .stat-card {
    padding: 12px;
  }
  .stat-card > p:last-child {
    font-size: 20px;
  }
}

```

## assets/css/auth/auth.css

```css
/* Styles for templates/auth/auth.html. */

/* Auth */
/* Sign-in and administration use quieter versions of the storefront accents. */

.auth-art {
  margin: 18px;
  border-radius: 12px;
  border: 1px solid #b99ddd33;
}

.auth-art > img {
  filter: saturate(0.6);
}

.auth-art::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(135deg, #7136af33, transparent 60%);
}

.auth-art .mark-a {
  color: #b8f5d0;
}

.auth-panel {
  background-image: radial-gradient(
    ellipse at 80% 20%,
    #a77ce312,
    transparent 60%
  );
}

.auth-panel > div {
  max-width: 470px;
}

.auth-panel h1 {
  letter-spacing: -0.05em;
}

.auth-panel form + div {
  background: var(--soft);
  border-color: var(--line);
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.auth-page > div > img {
  object-position: 68% center;
}

/* Responsive layout */
@media (max-width: 1023px) {
  .auth-panel {
    min-height: 100dvh;
  }
}
@media (max-width: 639px) {
  .auth-panel h1 {
    font-size: 34px;
  }
}

```

## assets/css/catalog/storefront.css

```css
/* Styles for templates/catalog/storefront.html. */

/* Storefront */
/* Editorial hero: a fine grid, spectral color, and an instrument-inspired signal. */

.hero-section {
  border-color: var(--line);
  background: var(--page);
}

.hero-mesh {
  pointer-events: none;
  background-image:
    radial-gradient(ellipse at 78% 35%, #a77ce32b, transparent 50%),
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size:
    auto,
    76px 76px,
    76px 76px;
  -webkit-mask-image: linear-gradient(to bottom, black 55%, transparent);
  mask-image: linear-gradient(to bottom, black 55%, transparent);
}

.hero-layout {
  min-height: 710px;
}

.hero-eyebrow {
  display: inline-flex;
  border: 1px solid var(--line);
  padding: 8px 12px;
  border-radius: 5px;
  background: var(--surface);
  font-size: 9px;
}

.hero-eyebrow::before {
  display: none;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--mint);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--mint) 12%, transparent);
  flex-shrink: 0;
}

.hero-copy h1 {
  font-size: clamp(4.4rem, 7.9vw, 7.4rem);
  line-height: 0.98;
  letter-spacing: -0.075em;
}

.hero-copy > p:not(.section-label) {
  max-width: 430px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--muted);
}

.hero-gradient {
  color: #8453d6;
  background: linear-gradient(110deg, #6940bb 5%, #a668d5 45%, #477d86 90%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .hero-gradient {
  background-image: linear-gradient(
    110deg,
    #c1a0ff 5%,
    #d3b5fb 45%,
    #a7edcb 95%
  );
}

.hero-stats {
  max-width: 440px;
  border-color: var(--line);
  gap: 16px;
}

.hero-stats > div + div {
  border-left: 1px solid var(--line);
  padding-left: 22px;
}

.hero-stats .font-display {
  font-size: 25px;
  letter-spacing: -0.05em;
}

.hero-visual {
  min-height: 565px;
  isolation: isolate;
}

.hero-photo {
  inset: 32px 24px 38px 24px;
  border-radius: 10px;
  transform: rotate(-3deg);
  border: 6px solid var(--surface);
  outline: 1px solid var(--line);
  box-shadow: 0 28px 75px -30px #35204f66;
}

.hero-photo img {
  filter: saturate(0.7);
}

.hero-photo-caption {
  flex-wrap: wrap;
  bottom: 68px;
}

.hero-photo-caption > div {
  min-width: 0;
}

.hero-photo-caption h2 {
  font-size: 23px;
}

.hero-photo-caption button {
  flex-shrink: 0;
  border-radius: 6px;
  height: 38px;
}

.hero-photo-caption button span {
  font-size: 10px;
}

.setup-note {
  z-index: 2;
  border-radius: 9px;
  background: var(--surface);
  border-color: var(--line);
  box-shadow: var(--shadow);
  animation: note-float 7s ease-in-out infinite;
}

.setup-note svg {
  color: var(--accent);
}

.sound-orbit {
  position: absolute;
  border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
}

.orbit-one {
  inset: -5% -11%;
  transform: rotate(-27deg) scaleY(0.72);
}

.orbit-two {
  inset: -11% -5%;
  transform: rotate(35deg) scaleY(0.86);
  border-style: dashed;
  opacity: 0.55;
}

.orbit-one::after {
  content: "";
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  top: 20%;
  right: 10%;
  background: var(--accent);
  box-shadow: 0 0 22px var(--accent);
}

.sound-signature {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 16px;
  bottom: 10px;
  left: -8px;
  z-index: 2;
  padding: 17px 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 9px;
  box-shadow: var(--shadow);
}

.sound-signature-icon {
  display: grid;
  place-items: center;
  height: 38px;
  width: 38px;
  border-radius: 7px;
  background: var(--soft);
  color: var(--accent);
}

.sound-signature-label {
  font-size: 10px;
  font-weight: 600;
}

.sound-signature-type {
  font:
    8px ui-monospace,
    monospace;
  letter-spacing: 0.08em;
  color: var(--muted);
  border-left: 1px solid var(--line);
  padding-left: 16px;
}

.sound-wave {
  display: flex;
  align-items: center;
  height: 23px;
  gap: 4px;
  margin-top: 3px;
}

.sound-wave i {
  display: block;
  width: 3px;
  height: 45%;
  border-radius: 2px;
  background: var(--accent);
  animation: signal 1.8s ease-in-out infinite alternate;
}

.sound-wave i:nth-child(3n) {
  height: 90%;
  animation-delay: -0.5s;
  background: var(--mint);
}

.sound-wave i:nth-child(3n + 1) {
  height: 60%;
  animation-delay: -1.2s;
}

.sound-wave i:nth-child(4n) {
  height: 30%;
  animation-delay: -0.8s;
}

.hero-bottom {
  padding: 18px 0;
  border-top: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface) 55%, transparent);
}

.hero-bottom .shell {
  color: var(--muted);
  font:
    9px ui-monospace,
    monospace;
  letter-spacing: 0.13em;
}

/* Collections and commerce surfaces. */

#categories {
  position: relative;
}

.category-card {
  height: 320px;
  border: 1px solid var(--line);
  border-radius: 10px;
}

.category-card img {
  object-fit: cover;
  background: #cac7c3;
  filter: none;
  transition:
    filter 0.6s,
    transform 0.7s;
}

.category-card:hover img {
  filter: saturate(1);
}

.category-card[data-category="Electric"] img {
  object-position: 66% center;
}
.category-card[data-category="Classical"] img {
  object-position: 35% center;
}
.category-card[data-category="Bass"] img {
  object-position: left center;
}

.category-card::after {
  content: "";
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 0 0 1px #ffffff0f;
}

.category-card h3 {
  letter-spacing: -0.04em;
}

.category-card .rounded-full {
  border-radius: 7px;
}

#shop {
  background: var(--soft);
  border-color: var(--line);
}

.finder-banner {
  border: 1px solid #56416e;
  border-radius: 12px;
  background:
    radial-gradient(ellipse at 95% 0%, #7444a640, transparent 65%), #18121f;
}

.dark .finder-banner {
  background:
    radial-gradient(ellipse at 95% 0%, #7444a640, transparent 65%), #18121f;
}

.finder-banner::before {
  content: "";
  pointer-events: none;
  position: absolute;
  inset: 0;
  opacity: 0.5;
  background-image:
    linear-gradient(#d5b5ff0c 1px, transparent 1px),
    linear-gradient(90deg, #d5b5ff0c 1px, transparent 1px);
  background-size: 48px 48px;
}

.finder-banner h2 {
  font-size: clamp(2.1rem, 4.2vw, 3.6rem);
  letter-spacing: -0.055em;
}

.finder-banner .text-zinc-500,
.finder-banner .text-zinc-400 {
  color: #b9aec5;
}

.finder-banner .primary-btn {
  background: #b8f5d0;
  color: #132b20;
}

.finder-banner .primary-btn:hover {
  background: #d5ffe5;
}

.finder-profile {
  position: relative;
  border-radius: 10px;
  border-color: #b696de33;
  box-shadow: 0 24px 45px #00000030;
  transform: rotate(2deg);
}

.finder-profile::before {
  content: "";
  position: absolute;
  width: 7px;
  height: 7px;
  top: 26px;
  right: 26px;
  border-radius: 50%;
  background: #b8f5d0;
  box-shadow:
    -13px 0 #b696de77,
    -26px 0 #b696de33;
}

#bundles > div {
  border-radius: 12px;
  border-color: var(--line);
  background: var(--surface);
}

#bundles h2 {
  letter-spacing: -0.05em;
  line-height: 1.12;
}

#track {
  border-color: var(--line);
  background: linear-gradient(120deg, var(--soft), var(--page));
}

.storefront main > .shell:last-child > div {
  border-radius: 9px;
  background: var(--surface);
  border-color: var(--line);
}

.storefront main > .shell:last-child > div > svg {
  flex-shrink: 0;
  color: var(--accent);
}

.storefront footer {
  border-color: var(--line);
  background: var(--surface);
}

.storefront footer .audia-mark {
  font-size: 27px;
}

.storefront footer h3 {
  color: var(--accent);
  font-size: 10px;
}

/* Product Card */
#shop .product-card {
  height: 100%;
  overflow: hidden;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  box-shadow: var(--shadow);
  transition:
    border-color 0.25s,
    box-shadow 0.25s;
}

#shop .product-card:hover {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
  box-shadow: 0 12px 32px -16px #7143d64d;
}

.product-image {
  aspect-ratio: 4 / 5;
  border-radius: 7px;
}

.product-image img {
  object-fit: contain;
  filter: none;
}

.product-details [data-field="description"] {
  min-height: 8.75rem;
}

.product-image > span {
  border-radius: 4px;
  font-size: 8px;
}

.product-details {
  padding: 20px 14px 14px;
}

.product-details > div:first-child {
  flex-wrap: wrap;
  gap: 6px;
  font-size: 9px;
}

.product-details > div:last-child {
  border-top: 1px solid var(--line);
  padding-top: 16px;
}

.product-details > div:last-child > button {
  border-radius: 7px;
  width: 39px;
  height: 39px;
}

.product-details h3 {
  font-size: 20px;
  letter-spacing: -0.035em;
}

/* Finder */
.finder-modal {
  max-height: calc(100dvh - 32px);
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 14px;
}

/* Cart */
.cart-panel {
  border-left: 1px solid var(--line);
}

/* Checkout */
[data-form="checkout"] .order-total {
  margin-top: 4px;
  padding-bottom: 0;
}

/* Bundle Detail */
.bundle-image {
  width: 100%;
  height: 230px;
  object-fit: cover;
  border-radius: 12px;
}

/* Responsive layout */
@media (min-width: 1600px) {
  .hero-layout {
    min-height: 770px;
  }
}
@media (max-width: 1023px) {
  .hero-layout {
    gap: 40px;
    padding-top: 56px;
    padding-bottom: 46px;
  }
  .hero-copy {
    max-width: 650px;
  }
  .hero-copy h1 {
    font-size: clamp(4.8rem, 10vw, 6.8rem);
  }
  .hero-visual {
    min-height: 510px;
    width: 100%;
    max-width: 650px;
    margin-inline: auto;
  }
  .hero-photo {
    inset: 15px 24px 32px;
  }
  .hero-photo img {
    -o-object-position: center 45%;
    object-position: center 45%;
  }
  .sound-orbit {
    max-width: 100%;
  }
  .category-card {
    height: 310px;
  }
}
@media (max-width: 639px) {
  .announcement {
    padding-inline: 16px;
    font-size: 8px;
    letter-spacing: 0.09em;
  }
  .store-header .shell {
    height: 68px;
    gap: 8px;
  }
  .store-header .audia-mark {
    font-size: 16px;
    letter-spacing: 0.22em;
  }
  .store-header .icon-btn,
  .store-header .theme-toggle {
    width: 36px;
    height: 38px;
  }
  .hero-layout {
    padding-top: 38px;
    gap: 30px;
  }
  .hero-copy h1 {
    font-size: clamp(3.6rem, 14vw, 5.5rem);
  }
  .hero-copy > p:not(.section-label) {
    font-size: 14px;
  }
  .hero-copy > .mt-9 {
    flex-direction: row;
    gap: 10px;
  }
  .hero-copy .primary-btn,
  .hero-copy .secondary-btn {
    padding: 13px 14px;
    font-size: 11px;
    gap: 7px;
  }
  .hero-stats {
    margin-top: 30px;
    gap: 10px;
  }
  .hero-stats > div + div {
    padding-left: 15px;
  }
  .hero-stats .font-display {
    font-size: 22px;
  }
  .hero-visual {
    min-height: 410px;
  }
  .hero-photo {
    inset: 22px 9px 38px;
    border-width: 4px;
    transform: rotate(-2deg);
  }
  .hero-photo-caption {
    left: 17px;
    right: 17px;
    bottom: 58px;
  }
  .hero-photo-caption h2 {
    font-size: 20px;
  }
  .hero-photo-caption p:last-child {
    font-size: 10px;
  }
  .hero-photo-caption button {
    padding-inline: 10px;
  }
  .setup-note {
    padding: 12px;
    top: 0;
  }
  .sound-signature {
    left: 0;
    bottom: 5px;
    padding: 12px;
    gap: 12px;
  }
  .hero-bottom .shell {
    font-size: 8px;
    gap: 13px;
  }
  #categories,
  #shop,
  #track {
    padding-block: 64px;
  }
  #categories > .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }
  .category-card {
    height: 245px;
  }
  .category-card .p-6 {
    padding: 14px;
  }
  .category-card h3 {
    font-size: 20px;
  }
  .category-card .p-6 > span {
    height: 27px;
    width: 27px;
    flex-shrink: 0;
  }
  .category-card .p-6 p {
    font-size: 8px;
    letter-spacing: 0.04em;
  }
  #shop .input-shell {
    min-width: 0;
  }
  #shop .mt-9.grid {
    gap: 20px;
  }
  .product-image {
    aspect-ratio: 1.2;
  }
  .finder-banner {
    padding: 36px 24px;
  }
  .finder-banner > .relative {
    gap: 32px;
  }
  .finder-profile {
    transform: none;
  }
  #bundles {
    padding-bottom: 64px;
  }
  #bundles > div > div:first-child {
    min-height: 290px;
  }
  #bundles h2 {
    font-size: 32px;
  }
  .storefront main > section:has(.finder-banner) {
    padding-block: 64px;
  }
}
@media (max-width: 359px) {
  .hero-copy .primary-btn,
  .hero-copy .secondary-btn {
    padding-inline: 10px;
    font-size: 10px;
  }
  .category-card .p-6 {
    padding: 10px;
  }
  .category-card h3 {
    font-size: 18px;
  }
  .category-card .p-6 > span {
    width: 23px;
    height: 23px;
  }
}

```

## assets/css/landing/landing.css

```css
/* Styles for templates/landing/landing.html. */

/* Landing */
.landing-page {
  overflow-x: clip;
}
.landing-page [hidden] {
  display: none;
}
.landing-page section {
  scroll-margin-top: 100px;
}
.landing-header {
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid var(--line);
  background: var(--page);
}
.landing-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 84px;
}
.landing-nav > .audia-mark {
  font-size: 22px;
  letter-spacing: 0.22em;
}
.landing-nav nav,
.landing-nav-actions {
  display: flex;
  align-items: center;
  gap: 28px;
}
.landing-nav nav {
  font-size: 13px;
  color: var(--muted);
}
.landing-nav a:hover,
.landing-text-link:hover {
  color: var(--accent);
}
.landing-nav-actions {
  gap: 12px;
}
.landing-theme {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 9px;
}
.landing-hero {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  align-items: center;
  gap: 68px;
  padding-top: 80px;
  padding-bottom: 80px;
}
.landing-hero h1 {
  margin-top: 24px;
  font-size: clamp(3.25rem, 5.6vw, 5.6rem);
  font-weight: 600;
  letter-spacing: -0.065em;
  line-height: 1.04;
}
.landing-hero-copy > p:not(.section-label) {
  max-width: 480px;
  margin-top: 28px;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.9;
}
.landing-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 32px;
}
.landing-text-link {
  font-size: 13px;
  font-weight: 600;
}
.landing-text-link span {
  margin-left: 8px;
}
.landing-hero-copy > .landing-access-note {
  margin-top: 18px;
  font-size: 12px;
}
.landing-hero-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 44px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.landing-hero-photo {
  position: relative;
  height: 560px;
  overflow: hidden;
  border-radius: 16px;
  background: #1e1711;
}
.landing-hero-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 30% center;
}
.landing-hero-photo::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 50%, #000b);
  pointer-events: none;
}
.landing-hero-photo figcaption {
  position: absolute;
  z-index: 1;
  left: 28px;
  right: 28px;
  bottom: 30px;
  color: #fff;
}
.landing-hero-photo figcaption span {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.17em;
  color: #ffffffb8;
}
.landing-hero-photo figcaption strong {
  display: block;
  margin-top: 10px;
  font-size: 23px;
  letter-spacing: -0.025em;
}
.landing-about {
  border-block: 1px solid var(--line);
  padding-block: 80px;
  background: var(--surface);
}
.landing-section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 40px;
  margin-bottom: 36px;
}
.landing-section-heading .section-title,
.landing-how .section-title,
.landing-join .section-title {
  margin-top: 18px;
  font-weight: 600;
}
.landing-section-heading > p {
  max-width: 390px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.9;
}
.landing-features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 30px;
}
.landing-features article {
  border-top: 1px solid var(--line);
  padding-top: 26px;
}
.landing-step {
  color: var(--accent);
  font-size: 10px;
  letter-spacing: 0.14em;
}
.landing-features h3 {
  margin-top: 20px;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.landing-features p,
.landing-steps p {
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.85;
}
.landing-collections {
  padding-block: 90px;
}
.landing-collection-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}
.landing-collection {
  display: block;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 12px;
  text-align: left;
  background: var(--surface);
  transition: border-color 0.2s;
}
.landing-collection:hover {
  border-color: var(--accent);
}
.landing-collection-photo {
  position: relative;
  display: block;
  height: 280px;
  overflow: hidden;
  background: #17141b;
}
.landing-collection-photo::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 45%, #000d);
  pointer-events: none;
}
.landing-collection-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.landing-collection[data-category="Electric"] img {
  object-position: 66% center;
}
.landing-collection[data-category="Classical"] img {
  object-position: 35% center;
}
.landing-collection[data-category="Bass"] img {
  object-position: left center;
}
.landing-collection-label {
  position: absolute;
  z-index: 1;
  bottom: 22px;
  left: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}
.landing-collection-label strong {
  font-size: 23px;
  letter-spacing: -0.035em;
}
.landing-collection-label > span {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 1px solid #ffffff60;
  border-radius: 7px;
}
.landing-collection-copy {
  display: block;
  padding: 22px 20px;
}
.landing-collection-copy strong {
  display: block;
  font-size: 13px;
  font-weight: 600;
}
.landing-collection-copy > span {
  display: block;
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.8;
  color: var(--muted);
}
.landing-how {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  padding-top: 25px;
  padding-bottom: 90px;
}
.landing-how-intro {
  margin-top: 22px;
  color: var(--muted);
  font-size: 14px;
}
.landing-steps {
  display: grid;
  gap: 24px;
}
.landing-steps li {
  display: flex;
  gap: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--line);
}
.landing-steps li > span {
  color: var(--accent);
  font-size: 13px;
}
.landing-steps h3 {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.landing-steps p {
  margin-top: 8px;
}
.landing-join {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  padding-top: 40px;
  padding-bottom: 50px;
  border-top: 1px solid var(--line);
}
.landing-join h2 {
  font-size: clamp(1.8rem, 3vw, 2.8rem);
}
.landing-join p:last-child {
  margin-top: 14px;
  color: var(--muted);
  font-size: 14px;
}
.landing-join > button {
  flex-shrink: 0;
}
.landing-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
  padding-block: 28px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 11px;
}
.landing-footer .audia-mark {
  color: var(--text);
  letter-spacing: 0.2em;
}
.landing-page :is(a, button):focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 5px;
}
@media (max-width: 1023px) {
  .landing-nav nav {
    gap: 18px;
  }
  .landing-hero {
    gap: 36px;
    padding-block: 55px;
  }
  .landing-hero-photo {
    height: 480px;
  }
  .landing-collection-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .landing-collection-photo {
    height: 290px;
  }
  .landing-how {
    gap: 40px;
  }
}
@media (max-width: 767px) {
  .landing-nav {
    min-height: 72px;
    gap: 14px;
  }
  .landing-nav nav {
    display: none;
  }
  .landing-nav .secondary-btn {
    padding: 10px 14px;
    font-size: 12px;
  }
  .landing-hero {
    grid-template-columns: 1fr;
    padding-top: 42px;
  }
  .landing-hero h1 {
    max-width: 500px;
    font-size: clamp(3rem, 11vw, 4.6rem);
  }
  .landing-hero-details {
    margin-top: 28px;
  }
  .landing-hero-photo {
    height: 350px;
  }
  .landing-section-heading {
    display: block;
  }
  .landing-section-heading > p {
    margin-top: 24px;
  }
  .landing-about,
  .landing-collections {
    padding-block: 54px;
  }
  .landing-features {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  .landing-how {
    grid-template-columns: 1fr;
    gap: 32px;
    padding-bottom: 50px;
  }
  .landing-join {
    align-items: start;
    flex-direction: column;
  }
}
@media (max-width: 479px) {
  .landing-collection-grid {
    grid-template-columns: 1fr;
  }
  .landing-collection-photo {
    height: 270px;
  }
  .landing-hero-photo {
    height: 310px;
  }
  .landing-hero-photo figcaption {
    left: 20px;
    right: 20px;
  }
  .landing-hero-photo figcaption strong {
    font-size: 20px;
  }
  .landing-nav > .audia-mark {
    font-size: 18px;
  }
}

```

## assets/css/lessons/lessons.css

```css
@import url("../shared/practice.css");

.lesson-hero { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); overflow: hidden; margin-bottom: 24px; }
.lesson-hero .practice-card { align-self: center; padding: 36px; }
.lesson-hero h2 { margin-top: 16px; font-size: clamp(26px, 4vw, 40px); letter-spacing: -0.04em; }
.lesson-hero img { height: 100%; min-height: 320px; max-height: 430px; width: 100%; object-fit: cover; }
.lesson-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; }
.lesson-card { display: flex; flex-direction: column; gap: 12px; }
.lesson-card p { margin-top: 0; }
.lesson-card .practice-link { margin-top: auto; padding-top: 12px; }
.lesson-card:hover, .chord-card:hover { border-color: var(--accent); }
.lesson-topics { display: flex; flex-wrap: wrap; gap: 12px 20px; margin-bottom: 24px; color: var(--accent); font-size: 13px; }
.lesson-basics-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }
.lesson-wide { grid-column: 1 / -1; }
.lesson-steps { margin-block: 16px; padding-left: 22px; font-size: 14px; line-height: 1.8; color: var(--muted); }
ol.lesson-steps { list-style: decimal; }
ul.lesson-steps { list-style: disc; }
.lesson-steps li + li { margin-top: 8px; }
.lesson-definitions dt { font-size: 14px; font-weight: 600; margin-top: 16px; }
.lesson-definitions dd { color: var(--muted); font-size: 14px; line-height: 1.8; margin-top: 4px; }
.lesson-string-list { margin-top: 16px; font-size: 14px; line-height: 2; }
.chord-legend { color: var(--muted); font-size: 12px; line-height: 1.8; margin-bottom: 24px; }
.chord-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }
.chord-card h2 { font-size: 17px; display: flex; justify-content: space-between; gap: 8px; }
.chord-card h2 span { color: var(--accent); }
.chord-diagram { display: block; width: 100%; max-width: 240px; height: auto; margin: 20px auto; }
.chord-fret, .chord-string { stroke: var(--muted); stroke-width: 1.5; }
.chord-nut { stroke: var(--text); stroke-width: 5; }
.chord-string-label, .chord-open-muted { fill: var(--text); font-size: 14px; }
.chord-fret-label { fill: var(--muted); font-size: 12px; }
.chord-finger { fill: var(--text); }
.chord-finger-number { fill: var(--surface); font-size: 12px; font-weight: 700; }
.chord-detail-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 24px; }
.chord-detail-diagram { text-align: center; align-self: start; }
.chord-detail-diagram h2 { font-size: 36px; color: var(--accent); }
.chord-detail-diagram .chord-legend { margin-bottom: 0; }
.strumming-lessons { display: grid; gap: 24px; margin-top: 24px; }
.strumming-pattern { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 8px; margin-block: 24px; max-width: 640px; }
.strumming-beat { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.strumming-stroke { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 64px; width: 100%; border-radius: 8px; background: var(--soft); color: var(--accent); font-size: 20px; font-weight: 600; }
.strumming-rest { color: var(--muted); }
.strumming-stroke > span { font-size: 15px; }
.strumming-count { color: var(--muted); font-size: 13px; }
@media (max-width: 1100px) { .chord-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 900px) { .chord-detail-layout { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 767px) {
  .lesson-hero, .lesson-grid, .lesson-basics-grid { grid-template-columns: minmax(0, 1fr); }
  .lesson-hero .practice-card { padding: 24px; }
  .lesson-hero img { min-height: 0; max-height: 260px; }
  .chord-grid { gap: 12px; }
  .chord-card { padding: 16px 12px; }
  .chord-card h2 { font-size: 15px; flex-wrap: wrap; }
  .strumming-pattern { gap: 4px; }
  .strumming-stroke { font-size: 17px; }
}
@media (max-width: 479px) {
  .chord-grid { grid-template-columns: minmax(0, 1fr); }
  .chord-card { padding: 20px; }
  .chord-card h2 { font-size: 17px; }
}

```

## assets/css/shared/practice.css

```css
/* Shared only by the new tuner and lessons pages. Reuses AUDIA's theme. */
.practice-page {
  min-height: 100vh;
  background: var(--page);
  color: var(--text);
}
.practice-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding-block: 20px;
  border-bottom: 1px solid var(--line);
}
.practice-header .audia-mark { font-size: 22px; }
.practice-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  margin-left: auto;
  font-size: 13px;
  color: var(--muted);
}
.practice-nav a { padding-block: 6px; }
.practice-nav a:hover, .practice-nav a[aria-current] { color: var(--accent); }
.practice-main { max-width: 1200px; padding-block: 40px 80px; }
.practice-heading { margin-bottom: 32px; }
.practice-heading > p:last-child {
  max-width: 660px;
  margin-top: 16px;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.8;
}
.practice-card { padding: 28px; min-width: 0; }
.practice-card h2 {
  font-family: "Space Grotesk", Inter, ui-sans-serif, system-ui;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.4;
}
.practice-card h3 { font-size: 15px; font-weight: 600; margin-top: 24px; }
.practice-card p:not(.section-label) { margin-top: 12px; color: var(--muted); font-size: 14px; line-height: 1.8; }
.practice-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 24px; }
.practice-link { color: var(--accent); font-size: 14px; font-weight: 600; }
.practice-link:hover { text-decoration: underline; }
@media (max-width: 767px) {
  .practice-header { gap: 12px; }
  .practice-header > .icon-btn { margin-left: auto; }
  .practice-nav { order: 3; width: 100%; margin-left: 0; gap: 8px 20px; }
  .practice-main { padding-block: 28px 64px; }
  .practice-card { padding: 20px; }
}

```

## assets/css/shared/shared.css

```css
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");

*,
::before,
::after {
  --tw-border-spacing-x: 0;
  --tw-border-spacing-y: 0;
  --tw-translate-x: 0;
  --tw-translate-y: 0;
  --tw-rotate: 0;
  --tw-skew-x: 0;
  --tw-skew-y: 0;
  --tw-scale-x: 1;
  --tw-scale-y: 1;
  --tw-pan-x:  ;
  --tw-pan-y:  ;
  --tw-pinch-zoom:  ;
  --tw-scroll-snap-strictness: proximity;
  --tw-gradient-from-position:  ;
  --tw-gradient-via-position:  ;
  --tw-gradient-to-position:  ;
  --tw-ordinal:  ;
  --tw-slashed-zero:  ;
  --tw-numeric-figure:  ;
  --tw-numeric-spacing:  ;
  --tw-numeric-fraction:  ;
  --tw-ring-inset:  ;
  --tw-ring-offset-width: 0px;
  --tw-ring-offset-color: #fff;
  --tw-ring-color: rgb(59 130 246 / 0.5);
  --tw-ring-offset-shadow: 0 0 #0000;
  --tw-ring-shadow: 0 0 #0000;
  --tw-shadow: 0 0 #0000;
  --tw-shadow-colored: 0 0 #0000;
  --tw-blur:  ;
  --tw-brightness:  ;
  --tw-contrast:  ;
  --tw-grayscale:  ;
  --tw-hue-rotate:  ;
  --tw-invert:  ;
  --tw-saturate:  ;
  --tw-sepia:  ;
  --tw-drop-shadow:  ;
  --tw-backdrop-blur:  ;
  --tw-backdrop-brightness:  ;
  --tw-backdrop-contrast:  ;
  --tw-backdrop-grayscale:  ;
  --tw-backdrop-hue-rotate:  ;
  --tw-backdrop-invert:  ;
  --tw-backdrop-opacity:  ;
  --tw-backdrop-saturate:  ;
  --tw-backdrop-sepia:  ;
  --tw-contain-size:  ;
  --tw-contain-layout:  ;
  --tw-contain-paint:  ;
  --tw-contain-style:  ;
}

::backdrop {
  --tw-border-spacing-x: 0;
  --tw-border-spacing-y: 0;
  --tw-translate-x: 0;
  --tw-translate-y: 0;
  --tw-rotate: 0;
  --tw-skew-x: 0;
  --tw-skew-y: 0;
  --tw-scale-x: 1;
  --tw-scale-y: 1;
  --tw-pan-x:  ;
  --tw-pan-y:  ;
  --tw-pinch-zoom:  ;
  --tw-scroll-snap-strictness: proximity;
  --tw-gradient-from-position:  ;
  --tw-gradient-via-position:  ;
  --tw-gradient-to-position:  ;
  --tw-ordinal:  ;
  --tw-slashed-zero:  ;
  --tw-numeric-figure:  ;
  --tw-numeric-spacing:  ;
  --tw-numeric-fraction:  ;
  --tw-ring-inset:  ;
  --tw-ring-offset-width: 0px;
  --tw-ring-offset-color: #fff;
  --tw-ring-color: rgb(59 130 246 / 0.5);
  --tw-ring-offset-shadow: 0 0 #0000;
  --tw-ring-shadow: 0 0 #0000;
  --tw-shadow: 0 0 #0000;
  --tw-shadow-colored: 0 0 #0000;
  --tw-blur:  ;
  --tw-brightness:  ;
  --tw-contrast:  ;
  --tw-grayscale:  ;
  --tw-hue-rotate:  ;
  --tw-invert:  ;
  --tw-saturate:  ;
  --tw-sepia:  ;
  --tw-drop-shadow:  ;
  --tw-backdrop-blur:  ;
  --tw-backdrop-brightness:  ;
  --tw-backdrop-contrast:  ;
  --tw-backdrop-grayscale:  ;
  --tw-backdrop-hue-rotate:  ;
  --tw-backdrop-invert:  ;
  --tw-backdrop-opacity:  ;
  --tw-backdrop-saturate:  ;
  --tw-backdrop-sepia:  ;
  --tw-contain-size:  ;
  --tw-contain-layout:  ;
  --tw-contain-paint:  ;
  --tw-contain-style:  ;
}

/*
! tailwindcss v3.4.19 | MIT License | https://tailwindcss.com
*/

/*
1. Prevent padding and border from affecting element width. (https://github.com/mozdevs/cssremedy/issues/4)
2. Allow adding a border to an element by just adding a border-width. (https://github.com/tailwindcss/tailwindcss/pull/116)
*/

*,
::before,
::after {
  box-sizing: border-box;
  /* 1 */
  border-width: 0;
  /* 2 */
  border-style: solid;
  /* 2 */
  border-color: #e5e7eb;
  /* 2 */
}

::before,
::after {
  --tw-content: "";
}

/*
1. Use a consistent sensible line-height in all browsers.
2. Prevent adjustments of font size after orientation changes in iOS.
3. Use a more readable tab size.
4. Use the user's configured `sans` font-family by default.
5. Use the user's configured `sans` font-feature-settings by default.
6. Use the user's configured `sans` font-variation-settings by default.
7. Disable tap highlights on iOS
*/

html,
:host {
  line-height: 1.5;
  /* 1 */
  -webkit-text-size-adjust: 100%;
  /* 2 */
  -moz-tab-size: 4;
  /* 3 */
  -o-tab-size: 4;
  tab-size: 4;
  /* 3 */
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  /* 4 */
  font-feature-settings: normal;
  /* 5 */
  font-variation-settings: normal;
  /* 6 */
  -webkit-tap-highlight-color: transparent;
  /* 7 */
}

/*
1. Remove the margin in all browsers.
2. Inherit line-height from `html` so users can set them as a class directly on the `html` element.
*/

body {
  margin: 0;
  /* 1 */
  line-height: inherit;
  /* 2 */
}

/*
1. Add the correct height in Firefox.
2. Correct the inheritance of border color in Firefox. (https://bugzilla.mozilla.org/show_bug.cgi?id=190655)
3. Ensure horizontal rules are visible by default.
*/

hr {
  height: 0;
  /* 1 */
  color: inherit;
  /* 2 */
  border-top-width: 1px;
  /* 3 */
}

/*
Add the correct text decoration in Chrome, Edge, and Safari.
*/

abbr:where([title]) {
  -webkit-text-decoration: underline dotted;
  text-decoration: underline dotted;
}

/*
Remove the default font size and weight for headings.
*/

h1,
h2,
h3,
h4,
h5,
h6 {
  font-size: inherit;
  font-weight: inherit;
}

/*
Reset links to optimize for opt-in styling instead of opt-out.
*/

a {
  color: inherit;
  text-decoration: inherit;
}

/*
Add the correct font weight in Edge and Safari.
*/

b,
strong {
  font-weight: bolder;
}

/*
1. Use the user's configured `mono` font-family by default.
2. Use the user's configured `mono` font-feature-settings by default.
3. Use the user's configured `mono` font-variation-settings by default.
4. Correct the odd `em` font sizing in all browsers.
*/

code,
kbd,
samp,
pre {
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
    "Courier New", monospace;
  /* 1 */
  font-feature-settings: normal;
  /* 2 */
  font-variation-settings: normal;
  /* 3 */
  font-size: 1em;
  /* 4 */
}

/*
Add the correct font size in all browsers.
*/

small {
  font-size: 80%;
}

/*
Prevent `sub` and `sup` elements from affecting the line height in all browsers.
*/

sub,
sup {
  font-size: 75%;
  line-height: 0;
  position: relative;
  vertical-align: baseline;
}

sub {
  bottom: -0.25em;
}

sup {
  top: -0.5em;
}

/*
1. Remove text indentation from table contents in Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=999088, https://bugs.webkit.org/show_bug.cgi?id=201297)
2. Correct table border color inheritance in all Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=935729, https://bugs.webkit.org/show_bug.cgi?id=195016)
3. Remove gaps between table borders by default.
*/

table {
  text-indent: 0;
  /* 1 */
  border-color: inherit;
  /* 2 */
  border-collapse: collapse;
  /* 3 */
}

/*
1. Change the font styles in all browsers.
2. Remove the margin in Firefox and Safari.
3. Remove default padding in all browsers.
*/

button,
input,
optgroup,
select,
textarea {
  font-family: inherit;
  /* 1 */
  font-feature-settings: inherit;
  /* 1 */
  font-variation-settings: inherit;
  /* 1 */
  font-size: 100%;
  /* 1 */
  font-weight: inherit;
  /* 1 */
  line-height: inherit;
  /* 1 */
  letter-spacing: inherit;
  /* 1 */
  color: inherit;
  /* 1 */
  margin: 0;
  /* 2 */
  padding: 0;
  /* 3 */
}

/*
Remove the inheritance of text transform in Edge and Firefox.
*/

button,
select {
  text-transform: none;
}

/*
1. Correct the inability to style clickable types in iOS and Safari.
2. Remove default button styles.
*/

button,
input:where([type="button"]),
input:where([type="reset"]),
input:where([type="submit"]) {
  -webkit-appearance: button;
  /* 1 */
  background-color: transparent;
  /* 2 */
  background-image: none;
  /* 2 */
}

/*
Use the modern Firefox focus style for all focusable elements.
*/

:-moz-focusring {
  outline: auto;
}

/*
Remove the additional `:invalid` styles in Firefox. (https://github.com/mozilla/gecko-dev/blob/2f9eacd9d3d995c937b4251a5557d95d494c9be1/layout/style/res/forms.css#L728-L737)
*/

:-moz-ui-invalid {
  box-shadow: none;
}

/*
Add the correct vertical alignment in Chrome and Firefox.
*/

progress {
  vertical-align: baseline;
}

/*
Correct the cursor style of increment and decrement buttons in Safari.
*/

::-webkit-inner-spin-button,
::-webkit-outer-spin-button {
  height: auto;
}

/*
1. Correct the odd appearance in Chrome and Safari.
2. Correct the outline style in Safari.
*/

[type="search"] {
  -webkit-appearance: textfield;
  /* 1 */
  outline-offset: -2px;
  /* 2 */
}

/*
Remove the inner padding in Chrome and Safari on macOS.
*/

::-webkit-search-decoration {
  -webkit-appearance: none;
}

/*
1. Correct the inability to style clickable types in iOS and Safari.
2. Change font properties to `inherit` in Safari.
*/

::-webkit-file-upload-button {
  -webkit-appearance: button;
  /* 1 */
  font: inherit;
  /* 2 */
}

/*
Add the correct display in Chrome and Safari.
*/

summary {
  display: list-item;
}

/*
Removes the default spacing and border for appropriate elements.
*/

blockquote,
dl,
dd,
h1,
h2,
h3,
h4,
h5,
h6,
hr,
figure,
p,
pre {
  margin: 0;
}

fieldset {
  margin: 0;
  padding: 0;
}

legend {
  padding: 0;
}

ol,
ul,
menu {
  list-style: none;
  margin: 0;
  padding: 0;
}

/*
Reset default styling for dialogs.
*/

dialog {
  padding: 0;
}

/*
Prevent resizing textareas horizontally by default.
*/

textarea {
  resize: vertical;
}

/*
1. Reset the default placeholder opacity in Firefox. (https://github.com/tailwindlabs/tailwindcss/issues/3300)
2. Set the default placeholder color to the user's configured gray 400 color.
*/

input::-moz-placeholder,
textarea::-moz-placeholder {
  opacity: 1;
  /* 1 */
  color: #9ca3af;
  /* 2 */
}

input::placeholder,
textarea::placeholder {
  opacity: 1;
  /* 1 */
  color: #9ca3af;
  /* 2 */
}

/*
Set the default cursor for buttons.
*/

button,
[role="button"] {
  cursor: pointer;
}

/*
Make sure disabled buttons don't get the pointer cursor.
*/

:disabled {
  cursor: default;
}

/*
1. Make replaced elements `display: block` by default. (https://github.com/mozdevs/cssremedy/issues/14)
2. Add `vertical-align: middle` to align replaced elements more sensibly by default. (https://github.com/jensimmons/cssremedy/issues/14#issuecomment-634934210)
   This can trigger a poorly considered lint error in some tools but is included by design.
*/

img,
svg,
video,
canvas,
audio,
iframe,
embed,
object {
  display: block;
  /* 1 */
  vertical-align: middle;
  /* 2 */
}

/*
Constrain images and videos to the parent width and preserve their intrinsic aspect ratio. (https://github.com/mozdevs/cssremedy/issues/14)
*/

img,
video {
  max-width: 100%;
  height: auto;
}

/* Make elements with the HTML hidden attribute stay hidden by default */

[hidden]:where(:not([hidden="until-found"])) {
  display: none;
}

.shell {
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  max-width: 1440px;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}

@media (min-width: 640px) {
  .shell {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

@media (min-width: 1024px) {
  .shell {
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

.section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  --tw-text-opacity: 1;
  color: rgb(124 58 237 / var(--tw-text-opacity, 1));
}

.section-label:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(184 245 208 / var(--tw-text-opacity, 1));
}

.section-title {
  margin-top: 0.75rem;
  font-family:
    Space Grotesk,
    Inter,
    ui-sans-serif,
    system-ui;
  font-size: 2.25rem;
  line-height: 2.5rem;
  font-weight: 600;
  letter-spacing: -0.035em;
}

.hero-stats .section-title {
  font-size: 25px;
  letter-spacing: -0.05em;
}

@media (max-width: 639px) {
  .hero-stats .section-title {
    font-size: 22px;
  }
}

@media (min-width: 640px) {
  .section-title {
    font-size: 3rem;
    line-height: 1;
  }
}

.surface-card {
  border-radius: 1rem;
  border-width: 1px;
  --tw-border-opacity: 1;
  border-color: rgb(228 228 231 / var(--tw-border-opacity, 1));
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
  --tw-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --tw-shadow-colored: 0 1px 2px 0 var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.surface-card:is(.dark *) {
  border-color: rgb(255 255 255 / 0.1);
  --tw-bg-opacity: 1;
  background-color: rgb(23 21 30 / var(--tw-bg-opacity, 1));
}

.product-card {
  border-radius: 1rem;
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.product-card:is(.dark *) {
  background-color: transparent;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 9999px;
  --tw-bg-opacity: 1;
  background-color: rgb(9 9 11 / var(--tw-bg-opacity, 1));
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  padding-top: 0.875rem;
  padding-bottom: 0.875rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 700;
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.category-card .primary-btn {
  border-radius: 7px;
}

.admin-page aside nav button.primary-btn {
  color: var(--accent);
  background: var(--soft);
  box-shadow: inset 3px 0 var(--accent);
}

.primary-btn:hover {
  --tw-translate-y: -0.125rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  --tw-bg-opacity: 1;
  background-color: rgb(109 40 217 / var(--tw-bg-opacity, 1));
}

.primary-btn:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(184 245 208 / var(--tw-bg-opacity, 1));
  --tw-text-opacity: 1;
  color: rgb(13 12 18 / var(--tw-text-opacity, 1));
}

.primary-btn:hover:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 9999px;
  border-width: 1px;
  --tw-border-opacity: 1;
  border-color: rgb(228 228 231 / var(--tw-border-opacity, 1));
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  padding-top: 0.875rem;
  padding-bottom: 0.875rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 600;
  --tw-text-opacity: 1;
  color: rgb(24 24 27 / var(--tw-text-opacity, 1));
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.category-card .secondary-btn {
  border-radius: 7px;
}

.secondary-btn:hover {
  --tw-translate-y: -0.125rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  --tw-border-opacity: 1;
  border-color: rgb(161 161 170 / var(--tw-border-opacity, 1));
}

.secondary-btn:is(.dark *) {
  border-color: rgb(255 255 255 / 0.15);
  background-color: rgb(255 255 255 / 0.04);
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.secondary-btn:hover:is(.dark *) {
  border-color: rgb(255 255 255 / 0.3);
  background-color: rgb(255 255 255 / 0.08);
}

.icon-btn {
  display: grid;
  height: 2.5rem;
  width: 2.5rem;
  flex-shrink: 0;
  place-items: center;
  border-radius: 9999px;
  --tw-text-opacity: 1;
  color: rgb(82 82 91 / var(--tw-text-opacity, 1));
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.category-card .icon-btn {
  border-radius: 7px;
}

.admin-page .icon-btn > * {
  min-width: 0;
}

@media (max-width: 639px) {
  #categories > .icon-btn {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  #shop .mt-9.icon-btn {
    gap: 20px;
  }
}

.icon-btn:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(244 244 245 / var(--tw-bg-opacity, 1));
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.icon-btn:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(212 212 216 / var(--tw-text-opacity, 1));
}

.icon-btn:hover:is(.dark *) {
  background-color: rgb(255 255 255 / 0.1);
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.nav-link {
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.nav-link:hover {
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.nav-link:hover:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.input-shell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 9999px;
  border-width: 1px;
  --tw-border-opacity: 1;
  border-color: rgb(228 228 231 / var(--tw-border-opacity, 1));
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
  padding-left: 1rem;
  padding-right: 1rem;
  --tw-text-opacity: 1;
  color: rgb(113 113 122 / var(--tw-text-opacity, 1));
  --tw-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --tw-shadow-colored: 0 1px 2px 0 var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

:is(.storefront, .auth-page, .admin-page) .input-shell {
  color: var(--muted);
}

.category-card .input-shell {
  border-radius: 7px;
}

.finder-banner .input-shell {
  color: #b9aec5;
}

@media (max-width: 639px) {
  .admin-page main > div > .input-shell {
    flex-wrap: wrap;
    gap: 16px;
  }
}

.input-shell:focus-within {
  --tw-border-opacity: 1;
  border-color: rgb(161 161 170 / var(--tw-border-opacity, 1));
}

.input-shell:is(.dark *) {
  border-color: rgb(255 255 255 / 0.1);
  background-color: rgb(255 255 255 / 0.04);
}

.input-shell:focus-within:is(.dark *) {
  border-color: rgb(255 255 255 / 0.25);
}

.filter-chip {
  flex-shrink: 0;
  border-radius: 9999px;
  border-width: 1px;
  --tw-border-opacity: 1;
  border-color: rgb(228 228 231 / var(--tw-border-opacity, 1));
  padding-left: 1.25rem;
  padding-right: 1.25rem;
  padding-top: 0.625rem;
  padding-bottom: 0.625rem;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 600;
  --tw-text-opacity: 1;
  color: rgb(113 113 122 / var(--tw-text-opacity, 1));
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

:is(.storefront, .auth-page, .admin-page) .filter-chip {
  color: var(--muted);
}

.category-card .filter-chip {
  border-radius: 7px;
}

.finder-banner .filter-chip {
  color: #b9aec5;
}

.filter-chip:hover {
  --tw-border-opacity: 1;
  border-color: rgb(161 161 170 / var(--tw-border-opacity, 1));
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.filter-chip:is(.dark *) {
  border-color: rgb(255 255 255 / 0.1);
}

.filter-chip:hover:is(.dark *) {
  border-color: rgb(255 255 255 / 0.25);
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.filter-chip-active {
  --tw-border-opacity: 1;
  border-color: rgb(9 9 11 / var(--tw-border-opacity, 1));
  --tw-bg-opacity: 1;
  background-color: rgb(9 9 11 / var(--tw-bg-opacity, 1));
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.admin-page aside nav button.filter-chip-active {
  color: var(--accent);
  background: var(--soft);
  box-shadow: inset 3px 0 var(--accent);
}

.filter-chip-active:hover {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.filter-chip-active:is(.dark *) {
  --tw-border-opacity: 1;
  border-color: rgb(255 255 255 / var(--tw-border-opacity, 1));
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
  --tw-text-opacity: 1;
  color: rgb(13 12 18 / var(--tw-text-opacity, 1));
}

.fixed {
  position: fixed;
}

.absolute {
  position: absolute;
}

.relative {
  position: relative;
}

.sticky {
  position: sticky;
}

.inset-0 {
  inset: 0px;
}

.inset-x-0 {
  left: 0px;
  right: 0px;
}

.inset-y-0 {
  top: 0px;
  bottom: 0px;
}

.-left-2 {
  left: -0.5rem;
}

.-right-0\.5 {
  right: -0.125rem;
}

.-right-28 {
  right: -7rem;
}

.-top-0\.5 {
  top: -0.125rem;
}

.-top-2 {
  top: -0.5rem;
}

.-top-28 {
  top: -7rem;
}

.-top-7 {
  top: -1.75rem;
}

.bottom-0 {
  bottom: 0px;
}

.bottom-24 {
  bottom: 6rem;
}

.bottom-3 {
  bottom: 0.75rem;
}

.bottom-5 {
  bottom: 1.25rem;
}

.bottom-6 {
  bottom: 1.5rem;
}

.left-0 {
  left: 0px;
}

.left-1\/2 {
  left: 50%;
}

.left-3 {
  left: 0.75rem;
}

.left-6 {
  left: 1.5rem;
}

.right-0 {
  right: 0px;
}

.right-2 {
  right: 0.5rem;
}

.right-3 {
  right: 0.75rem;
}

.right-4 {
  right: 1rem;
}

.right-5 {
  right: 1.25rem;
}

.right-6 {
  right: 1.5rem;
}

.top-0 {
  top: 0px;
}

.top-2 {
  top: 0.5rem;
}

.top-3 {
  top: 0.75rem;
}

.top-5 {
  top: 1.25rem;
}

.top-6 {
  top: 1.5rem;
}

.z-10 {
  z-index: 10;
}

.z-30 {
  z-index: 30;
}

.z-40 {
  z-index: 40;
}

.z-50 {
  z-index: 50;
}

.z-\[60\] {
  z-index: 60;
}

.float-right {
  float: right;
}

.mx-2 {
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

.mb-10 {
  margin-bottom: 2.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-7 {
  margin-bottom: 1.75rem;
}

.mb-8 {
  margin-bottom: 2rem;
}

.mb-9 {
  margin-bottom: 2.25rem;
}

.ml-1 {
  margin-left: 0.25rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.ml-auto {
  margin-left: auto;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mt-0\.5 {
  margin-top: 0.125rem;
}

.mt-1 {
  margin-top: 0.25rem;
}

.mt-10 {
  margin-top: 2.5rem;
}

.mt-12 {
  margin-top: 3rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-3 {
  margin-top: 0.75rem;
}

.mt-4 {
  margin-top: 1rem;
}

.mt-5 {
  margin-top: 1.25rem;
}

.mt-6 {
  margin-top: 1.5rem;
}

.mt-7 {
  margin-top: 1.75rem;
}

.mt-8 {
  margin-top: 2rem;
}

.mt-9 {
  margin-top: 2.25rem;
}

.mt-auto {
  margin-top: auto;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.block {
  display: block;
}

.flex {
  display: flex;
}

.inline-flex {
  display: inline-flex;
}

.table {
  display: table;
}

.grid {
  display: grid;
}

.hidden {
  display: none;
}

.aspect-\[4\/4\.5\] {
  aspect-ratio: 4/4.5;
}

.h-1 {
  height: 0.25rem;
}

.h-1\.5 {
  height: 0.375rem;
}

.h-10 {
  height: 2.5rem;
}

.h-11 {
  height: 2.75rem;
}

.h-12 {
  height: 3rem;
}

.h-14 {
  height: 3.5rem;
}

.h-2 {
  height: 0.5rem;
}

.h-20 {
  height: 5rem;
}

.h-24 {
  height: 6rem;
}

.h-5 {
  height: 1.25rem;
}

.h-6 {
  height: 1.5rem;
}

.h-64 {
  height: 16rem;
}

.h-8 {
  height: 2rem;
}

.h-80 {
  height: 20rem;
}

.h-9 {
  height: 2.25rem;
}

.h-\[390px\] {
  height: 390px;
}

.h-\[510px\] {
  height: 510px;
}

.h-\[76px\] {
  height: 76px;
}

.h-\[78px\] {
  height: 78px;
}

.h-full {
  height: 100%;
}

.h-px {
  height: 1px;
}

.min-h-\[40px\] {
  min-height: 40px;
}

.min-h-\[430px\] {
  min-height: 430px;
}

.min-h-screen {
  min-height: 100vh;
}

.w-1\.5 {
  width: 0.375rem;
}

.w-10 {
  width: 2.5rem;
}

.w-11 {
  width: 2.75rem;
}

.w-12 {
  width: 3rem;
}

.w-14 {
  width: 3.5rem;
}

.w-16 {
  width: 4rem;
}

.w-20 {
  width: 5rem;
}

.w-5 {
  width: 1.25rem;
}

.w-6 {
  width: 1.5rem;
}

.w-8 {
  width: 2rem;
}

.w-80 {
  width: 20rem;
}

.w-9 {
  width: 2.25rem;
}

.w-\[270px\] {
  width: 270px;
}

.w-\[74px\] {
  width: 74px;
}

.w-\[calc\(100\%-2rem\)\] {
  width: calc(100% - 2rem);
}

.w-full {
  width: 100%;
}

.min-w-0 {
  min-width: 0px;
}

.min-w-\[270px\] {
  min-width: 270px;
}

.min-w-\[680px\] {
  min-width: 680px;
}

.min-w-\[900px\] {
  min-width: 900px;
}

.max-w-2xl {
  max-width: 42rem;
}

.max-w-\[180px\] {
  max-width: 180px;
}

.max-w-\[210px\] {
  max-width: 210px;
}

.max-w-\[86\%\] {
  max-width: 86%;
}

.max-w-lg {
  max-width: 32rem;
}

.max-w-md {
  max-width: 28rem;
}

.max-w-sm {
  max-width: 24rem;
}

.max-w-xl {
  max-width: 36rem;
}

.max-w-xs {
  max-width: 20rem;
}

.flex-1 {
  flex: 1 1 0%;
}

.-translate-x-1\/2 {
  --tw-translate-x: -50%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.-translate-x-full {
  --tw-translate-x: -100%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.translate-x-0 {
  --tw-translate-x: 0px;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.appearance-none {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.flex-col {
  flex-direction: column;
}

.flex-wrap {
  flex-wrap: wrap;
}

.place-items-center {
  place-items: center;
}

.items-start {
  align-items: flex-start;
}

.items-end {
  align-items: flex-end;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-1 {
  gap: 0.25rem;
}

.gap-1\.5 {
  gap: 0.375rem;
}

.gap-12 {
  gap: 3rem;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 0.75rem;
}

.gap-4 {
  gap: 1rem;
}

.gap-6 {
  gap: 1.5rem;
}

.gap-7 {
  gap: 1.75rem;
}

.gap-8 {
  gap: 2rem;
}

.gap-px {
  gap: 1px;
}

.gap-x-5 {
  -moz-column-gap: 1.25rem;
  column-gap: 1.25rem;
}

.gap-y-12 {
  row-gap: 3rem;
}

.space-y-1 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.25rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.25rem * var(--tw-space-y-reverse));
}

.space-y-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.75rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.75rem * var(--tw-space-y-reverse));
}

.space-y-5 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(1.25rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(1.25rem * var(--tw-space-y-reverse));
}

.space-y-6 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(1.5rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(1.5rem * var(--tw-space-y-reverse));
}

.divide-y > :not([hidden]) ~ :not([hidden]) {
  --tw-divide-y-reverse: 0;
  border-top-width: calc(1px * calc(1 - var(--tw-divide-y-reverse)));
  border-bottom-width: calc(1px * var(--tw-divide-y-reverse));
}

.divide-white\/10 > :not([hidden]) ~ :not([hidden]) {
  border-color: rgb(255 255 255 / 0.1);
}

.divide-zinc-100 > :not([hidden]) ~ :not([hidden]) {
  --tw-divide-opacity: 1;
  border-color: rgb(244 244 245 / var(--tw-divide-opacity, 1));
}

.self-start {
  align-self: flex-start;
}

.overflow-hidden {
  overflow: hidden;
}

.overflow-x-auto {
  overflow-x: auto;
}

.overflow-y-auto {
  overflow-y: auto;
}

.overflow-x-clip {
  overflow-x: clip;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rounded {
  border-radius: 0.25rem;
}

.rounded-2xl {
  border-radius: 1rem;
}

.rounded-3xl {
  border-radius: 1.5rem;
}

.rounded-\[1\.15rem\] {
  border-radius: 1.15rem;
}

.rounded-\[2rem\] {
  border-radius: 2rem;
}

.rounded-full {
  border-radius: 9999px;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.rounded-xl {
  border-radius: 0.75rem;
}

.rounded-t-md {
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
}

.border {
  border-width: 1px;
}

.border-y {
  border-top-width: 1px;
  border-bottom-width: 1px;
}

.border-b {
  border-bottom-width: 1px;
}

.border-l {
  border-left-width: 1px;
}

.border-r {
  border-right-width: 1px;
}

.border-t {
  border-top-width: 1px;
}

.border-dashed {
  border-style: dashed;
}

.border-white\/10 {
  border-color: rgb(255 255 255 / 0.1);
}

.border-white\/30 {
  border-color: rgb(255 255 255 / 0.3);
}

.border-zinc-100 {
  --tw-border-opacity: 1;
  border-color: rgb(244 244 245 / var(--tw-border-opacity, 1));
}

.border-zinc-200 {
  --tw-border-opacity: 1;
  border-color: rgb(228 228 231 / var(--tw-border-opacity, 1));
}

.border-zinc-200\/80 {
  border-color: rgb(228 228 231 / 0.8);
}

.border-zinc-300 {
  --tw-border-opacity: 1;
  border-color: rgb(212 212 216 / var(--tw-border-opacity, 1));
}

.border-zinc-950 {
  --tw-border-opacity: 1;
  border-color: rgb(9 9 11 / var(--tw-border-opacity, 1));
}

.bg-amber-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(254 243 199 / var(--tw-bg-opacity, 1));
}

.bg-amber-400 {
  --tw-bg-opacity: 1;
  background-color: rgb(251 191 36 / var(--tw-bg-opacity, 1));
}

.bg-black\/40 {
  background-color: rgb(0 0 0 / 0.4);
}

.bg-black\/55 {
  background-color: rgb(0 0 0 / 0.55);
}

.bg-black\/65 {
  background-color: rgb(0 0 0 / 0.65);
}

.bg-blue-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(219 234 254 / var(--tw-bg-opacity, 1));
}

.bg-cyan-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(6 182 212 / var(--tw-bg-opacity, 1));
}

.bg-emerald-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(209 250 229 / var(--tw-bg-opacity, 1));
}

.bg-rose-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(255 228 230 / var(--tw-bg-opacity, 1));
}

.bg-rose-400 {
  --tw-bg-opacity: 1;
  background-color: rgb(251 113 133 / var(--tw-bg-opacity, 1));
}

.bg-rose-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(255 241 242 / var(--tw-bg-opacity, 1));
}

.bg-rose-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(244 63 94 / var(--tw-bg-opacity, 1));
}

.bg-stone-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(250 250 249 / var(--tw-bg-opacity, 1));
}

.bg-stone-50\/90 {
  background-color: rgb(250 250 249 / 0.9);
}

.bg-transparent {
  background-color: transparent;
}

.bg-violet-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(237 233 254 / var(--tw-bg-opacity, 1));
}

.bg-violet-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(139 92 246 / var(--tw-bg-opacity, 1));
}

.bg-violet-500\/25 {
  background-color: rgb(139 92 246 / 0.25);
}

.bg-white {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.bg-white\/10 {
  background-color: rgb(255 255 255 / 0.1);
}

.bg-white\/15 {
  background-color: rgb(255 255 255 / 0.15);
}

.bg-white\/90 {
  background-color: rgb(255 255 255 / 0.9);
}

.bg-white\/\[\.055\] {
  background-color: rgb(255 255 255 / 0.055);
}

.bg-zinc-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(244 244 245 / var(--tw-bg-opacity, 1));
}

.bg-zinc-200 {
  --tw-bg-opacity: 1;
  background-color: rgb(228 228 231 / var(--tw-bg-opacity, 1));
}

.bg-zinc-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(250 250 250 / var(--tw-bg-opacity, 1));
}

.bg-zinc-900 {
  --tw-bg-opacity: 1;
  background-color: rgb(24 24 27 / var(--tw-bg-opacity, 1));
}

.bg-zinc-950 {
  --tw-bg-opacity: 1;
  background-color: rgb(9 9 11 / var(--tw-bg-opacity, 1));
}

.bg-gradient-to-t {
  background-image: linear-gradient(to top, var(--tw-gradient-stops));
}

.from-amber-500\/30 {
  --tw-gradient-from: rgb(245 158 11 / 0.3) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(245 158 11 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-black {
  --tw-gradient-from: #000 var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(0 0 0 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-black\/75 {
  --tw-gradient-from: rgb(0 0 0 / 0.75) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(0 0 0 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-black\/90 {
  --tw-gradient-from: rgb(0 0 0 / 0.9) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(0 0 0 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-cyan-500\/30 {
  --tw-gradient-from: rgb(6 182 212 / 0.3) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(6 182 212 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-rose-500\/30 {
  --tw-gradient-from: rgb(244 63 94 / 0.3) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(244 63 94 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.from-violet-500\/30 {
  --tw-gradient-from: rgb(139 92 246 / 0.3) var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(139 92 246 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.via-black\/15 {
  --tw-gradient-to: rgb(0 0 0 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops:
    var(--tw-gradient-from), rgb(0 0 0 / 0.15) var(--tw-gradient-via-position),
    var(--tw-gradient-to);
}

.via-transparent {
  --tw-gradient-to: rgb(0 0 0 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops:
    var(--tw-gradient-from), transparent var(--tw-gradient-via-position),
    var(--tw-gradient-to);
}

.to-black\/30 {
  --tw-gradient-to: rgb(0 0 0 / 0.3) var(--tw-gradient-to-position);
}

.to-black\/5 {
  --tw-gradient-to: rgb(0 0 0 / 0.05) var(--tw-gradient-to-position);
}

.to-transparent {
  --tw-gradient-to: transparent var(--tw-gradient-to-position);
}

.fill-amber-400 {
  fill: #fbbf24;
}

.object-cover {
  -o-object-fit: cover;
  object-fit: cover;
}

.object-center {
  -o-object-position: center;
  object-position: center;
}

.p-1\.5 {
  padding: 0.375rem;
}

.p-12 {
  padding: 3rem;
}

.p-3 {
  padding: 0.75rem;
}

.p-4 {
  padding: 1rem;
}

.p-5 {
  padding: 1.25rem;
}

.p-6 {
  padding: 1.5rem;
}

.p-7 {
  padding: 1.75rem;
}

.p-8 {
  padding: 2rem;
}

.px-1 {
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}

.px-2 {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.px-2\.5 {
  padding-left: 0.625rem;
  padding-right: 0.625rem;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.px-5 {
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}

.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.px-7 {
  padding-left: 1.75rem;
  padding-right: 1.75rem;
}

.py-0\.5 {
  padding-top: 0.125rem;
  padding-bottom: 0.125rem;
}

.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.py-1\.5 {
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
}

.py-14 {
  padding-top: 3.5rem;
  padding-bottom: 3.5rem;
}

.py-16 {
  padding-top: 4rem;
  padding-bottom: 4rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.py-2\.5 {
  padding-top: 0.625rem;
  padding-bottom: 0.625rem;
}

.py-20 {
  padding-top: 5rem;
  padding-bottom: 5rem;
}

.py-24 {
  padding-top: 6rem;
  padding-bottom: 6rem;
}

.py-3 {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

.py-3\.5 {
  padding-top: 0.875rem;
  padding-bottom: 0.875rem;
}

.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.py-5 {
  padding-top: 1.25rem;
  padding-bottom: 1.25rem;
}

.py-6 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.pb-1 {
  padding-bottom: 0.25rem;
}

.pb-14 {
  padding-bottom: 3.5rem;
}

.pb-2 {
  padding-bottom: 0.5rem;
}

.pb-24 {
  padding-bottom: 6rem;
}

.pl-4 {
  padding-left: 1rem;
}

.pl-5 {
  padding-left: 1.25rem;
}

.pr-4 {
  padding-right: 1rem;
}

.pr-6 {
  padding-right: 1.5rem;
}

.pt-16 {
  padding-top: 4rem;
}

.pt-3 {
  padding-top: 0.75rem;
}

.pt-4 {
  padding-top: 1rem;
}

.pt-5 {
  padding-top: 1.25rem;
}

.pt-6 {
  padding-top: 1.5rem;
}

.text-left {
  text-align: left;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.font-display {
  font-family:
    Space Grotesk,
    Inter,
    ui-sans-serif,
    system-ui;
}

.text-2xl {
  font-size: 1.5rem;
  line-height: 2rem;
}

.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-4xl {
  font-size: 2.25rem;
  line-height: 2.5rem;
}

.text-5xl {
  font-size: 3rem;
  line-height: 1;
}

.text-\[10px\] {
  font-size: 10px;
}

.text-\[11px\] {
  font-size: 11px;
}

.text-\[9px\] {
  font-size: 9px;
}

.text-\[clamp\(3\.4rem\2c 7\.5vw\2c 7rem\)\] {
  font-size: clamp(3.4rem, 7.5vw, 7rem);
}

.text-base {
  font-size: 1rem;
  line-height: 1.5rem;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.text-xl {
  font-size: 1.25rem;
  line-height: 1.75rem;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.font-bold {
  font-weight: 700;
}

.font-medium {
  font-weight: 500;
}

.font-semibold {
  font-weight: 600;
}

.uppercase {
  text-transform: uppercase;
}

.normal-case {
  text-transform: none;
}

.leading-5 {
  line-height: 1.25rem;
}

.leading-6 {
  line-height: 1.5rem;
}

.leading-7 {
  line-height: 1.75rem;
}

.leading-\[\.88\] {
  line-height: 0.88;
}

.leading-\[1\.03\] {
  line-height: 1.03;
}

.leading-tight {
  line-height: 1.25;
}

.tracking-\[-\.04em\] {
  letter-spacing: -0.04em;
}

.tracking-\[-\.065em\] {
  letter-spacing: -0.065em;
}

.tracking-\[\.12em\] {
  letter-spacing: 0.12em;
}

.tracking-\[\.14em\] {
  letter-spacing: 0.14em;
}

.tracking-\[\.15em\] {
  letter-spacing: 0.15em;
}

.tracking-\[\.16em\] {
  letter-spacing: 0.16em;
}

.tracking-\[\.18em\] {
  letter-spacing: 0.18em;
}

.tracking-\[\.2em\] {
  letter-spacing: 0.2em;
}

.tracking-normal {
  letter-spacing: 0em;
}

.tracking-tight {
  letter-spacing: -0.025em;
}

.tracking-widest {
  letter-spacing: 0.1em;
}

.text-acid {
  --tw-text-opacity: 1;
  color: rgb(184 245 208 / var(--tw-text-opacity, 1));
}

.text-amber-400 {
  --tw-text-opacity: 1;
  color: rgb(251 191 36 / var(--tw-text-opacity, 1));
}

.text-amber-500 {
  --tw-text-opacity: 1;
  color: rgb(245 158 11 / var(--tw-text-opacity, 1));
}

.text-amber-700 {
  --tw-text-opacity: 1;
  color: rgb(180 83 9 / var(--tw-text-opacity, 1));
}

.text-blue-700 {
  --tw-text-opacity: 1;
  color: rgb(29 78 216 / var(--tw-text-opacity, 1));
}

.text-emerald-500 {
  --tw-text-opacity: 1;
  color: rgb(16 185 129 / var(--tw-text-opacity, 1));
}

.text-emerald-700 {
  --tw-text-opacity: 1;
  color: rgb(4 120 87 / var(--tw-text-opacity, 1));
}

.text-rose-500 {
  --tw-text-opacity: 1;
  color: rgb(244 63 94 / var(--tw-text-opacity, 1));
}

.text-rose-600 {
  --tw-text-opacity: 1;
  color: rgb(225 29 72 / var(--tw-text-opacity, 1));
}

.text-rose-700 {
  --tw-text-opacity: 1;
  color: rgb(190 18 60 / var(--tw-text-opacity, 1));
}

.text-violet-700 {
  --tw-text-opacity: 1;
  color: rgb(109 40 217 / var(--tw-text-opacity, 1));
}

.text-white {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.text-white\/40 {
  color: rgb(255 255 255 / 0.4);
}

.text-white\/55 {
  color: rgb(255 255 255 / 0.55);
}

.text-white\/60 {
  color: rgb(255 255 255 / 0.6);
}

.text-white\/65 {
  color: rgb(255 255 255 / 0.65);
}

.text-zinc-300 {
  --tw-text-opacity: 1;
  color: rgb(212 212 216 / var(--tw-text-opacity, 1));
}

.text-zinc-400 {
  --tw-text-opacity: 1;
  color: rgb(161 161 170 / var(--tw-text-opacity, 1));
}

.text-zinc-500 {
  --tw-text-opacity: 1;
  color: rgb(113 113 122 / var(--tw-text-opacity, 1));
}

.text-zinc-600 {
  --tw-text-opacity: 1;
  color: rgb(82 82 91 / var(--tw-text-opacity, 1));
}

.text-zinc-700 {
  --tw-text-opacity: 1;
  color: rgb(63 63 70 / var(--tw-text-opacity, 1));
}

.text-zinc-950 {
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.line-through {
  text-decoration-line: line-through;
}

.opacity-40 {
  opacity: 0.4;
}

.opacity-70 {
  opacity: 0.7;
}

.shadow-2xl {
  --tw-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.shadow-lg {
  --tw-shadow:
    0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --tw-shadow-colored:
    0 10px 15px -3px var(--tw-shadow-color),
    0 4px 6px -4px var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.shadow-md {
  --tw-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --tw-shadow-colored:
    0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.shadow-sm {
  --tw-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --tw-shadow-colored: 0 1px 2px 0 var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.shadow-xl {
  --tw-shadow:
    0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --tw-shadow-colored:
    0 20px 25px -5px var(--tw-shadow-color),
    0 8px 10px -6px var(--tw-shadow-color);
  box-shadow:
    var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000),
    var(--tw-shadow);
}

.outline-none {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.blur-\[100px\] {
  --tw-blur: blur(100px);
  filter: var(--tw-blur) var(--tw-brightness) var(--tw-contrast)
    var(--tw-grayscale) var(--tw-hue-rotate) var(--tw-invert) var(--tw-saturate)
    var(--tw-sepia) var(--tw-drop-shadow);
}

.filter {
  filter: var(--tw-blur) var(--tw-brightness) var(--tw-contrast)
    var(--tw-grayscale) var(--tw-hue-rotate) var(--tw-invert) var(--tw-saturate)
    var(--tw-sepia) var(--tw-drop-shadow);
}

.backdrop-blur {
  --tw-backdrop-blur: blur(8px);
  backdrop-filter: var(--tw-backdrop-blur) var(--tw-backdrop-brightness)
    var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale)
    var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert)
    var(--tw-backdrop-opacity) var(--tw-backdrop-saturate)
    var(--tw-backdrop-sepia);
}

.backdrop-blur-md {
  --tw-backdrop-blur: blur(12px);
  backdrop-filter: var(--tw-backdrop-blur) var(--tw-backdrop-brightness)
    var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale)
    var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert)
    var(--tw-backdrop-opacity) var(--tw-backdrop-saturate)
    var(--tw-backdrop-sepia);
}

.backdrop-blur-sm {
  --tw-backdrop-blur: blur(4px);
  backdrop-filter: var(--tw-backdrop-blur) var(--tw-backdrop-brightness)
    var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale)
    var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert)
    var(--tw-backdrop-opacity) var(--tw-backdrop-saturate)
    var(--tw-backdrop-sepia);
}

.backdrop-blur-xl {
  --tw-backdrop-blur: blur(24px);
  backdrop-filter: var(--tw-backdrop-blur) var(--tw-backdrop-brightness)
    var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale)
    var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert)
    var(--tw-backdrop-opacity) var(--tw-backdrop-saturate)
    var(--tw-backdrop-sepia);
}

.transition {
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke,
    opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-colors {
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.duration-1000 {
  transition-duration: 1000ms;
}

.duration-300 {
  transition-duration: 300ms;
}

.duration-700 {
  transition-duration: 700ms;
}

:root {
  --page: #f8f7fb;
  --surface: #ffffff;
  --soft: #f0edf6;
  --line: #e3deec;
  --text: #211b2e;
  --muted: #70687c;
  --accent: #7143d6;
  --mint: #22734d;
  --grid: rgba(112, 85, 155, 0.07);
  --shadow: 0 12px 40px -24px rgba(57, 33, 96, 0.3);
  color: #18181b;
  background: #fafaf9;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  font-synthesis: none;
}

html {
  scroll-behavior: smooth;
  scroll-padding-top: 100px;
  color-scheme: light;
}

html.dark {
  color-scheme: dark;
  --page: #0d0c12;
  --surface: #17151e;
  --soft: #211d2b;
  --line: #302939;
  --text: #f5f1fb;
  --muted: #aaa1b7;
  --accent: #bb9bff;
  --mint: #b8f5d0;
  --grid: rgba(197, 173, 235, 0.065);
  --shadow: 0 12px 40px -24px rgba(0, 0, 0, 0.65);
}

body {
  margin: 0;
  min-width: 320px;
  background: #fafaf9;
  transition: background-color 0.3s ease;
}

.dark body {
  background: #09090b;
}

button,
a,
input,
select {
  -webkit-tap-highlight-color: transparent;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

::-moz-selection {
  background: #d5c0ff;
  color: #211b2e;
}

::selection {
  background: #d5c0ff;
  color: #211b2e;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #e7e5e4;
}

.dark ::-webkit-scrollbar-track {
  background: #09090b;
}

::-webkit-scrollbar-thumb {
  background: #34343d;
  border-radius: 99px;
}

.audia-mark {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  letter-spacing: 0.36em;
  line-height: 1;
}

.audia-mark .mark-a {
  color: var(--accent);
  display: inline-block;
  transform: scaleX(0.86);
}

.dark .audia-mark .mark-a {
  color: var(--mint);
}

.hero-mesh {
  background:
    radial-gradient(
      circle at 82% 22%,
      rgba(124, 58, 237, 0.16),
      transparent 28%
    ),
    radial-gradient(
      circle at 35% 78%,
      rgba(200, 255, 61, 0.13),
      transparent 25%
    );
}

.text-outline {
  color: transparent;
  -webkit-text-stroke: 1.5px #18181b;
}

.dark .text-outline {
  -webkit-text-stroke-color: rgba(255, 255, 255, 0.9);
}

.noise::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E");
}

.range-acid {
  accent-color: var(--accent);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Shared presentation tokens keep every workspace in the same visual family. */

body,
.dark body,
#root > div,
.auth-page,
.admin-page {
  background: var(--page);
  color: var(--text);
}

body {
  -webkit-font-smoothing: antialiased;
}

button,
a,
input,
select {
  touch-action: manipulation;
}

button:disabled {
  cursor: wait;
  opacity: 0.6;
}

input,
select {
  min-width: 0;
}

select option {
  background: var(--surface);
  color: var(--text);
}

.shell {
  max-width: 1360px;
}

:is(.storefront, .auth-page, .admin-page) .text-zinc-500 {
  color: var(--muted);
}

.section-label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--accent);
  font-size: 10px;
  letter-spacing: 0.18em;
}

.section-label::before {
  content: "";
  width: 18px;
  height: 1px;
  flex-shrink: 0;
  background: currentColor;
}

.section-title {
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.1;
  letter-spacing: -0.055em;
}

.surface-card {
  background: var(--surface);
  border-color: var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.primary-btn,
.secondary-btn {
  min-height: 46px;
  border-radius: 8px;
  transition:
    background 0.2s,
    border-color 0.2s,
    box-shadow 0.2s,
    transform 0.2s;
}

.primary-btn {
  background: #7346d6;
  color: #fff;
  box-shadow:
    inset 0 1px 0 #ffffff24,
    0 4px 14px #7143d61a;
}

.primary-btn:hover {
  background: #6333c5;
  box-shadow: 0 6px 22px #7143d63d;
}

.dark .primary-btn {
  background: #b8f5d0;
  color: #132b20;
  box-shadow:
    inset 0 1px 0 #ffffff66,
    0 4px 20px #b8f5d012;
}

.dark .primary-btn:hover {
  background: #d5ffe5;
  box-shadow: 0 6px 24px #b8f5d026;
}

.secondary-btn {
  border-color: var(--line);
  background: var(--surface);
  color: var(--text);
}

.secondary-btn:hover {
  border-color: var(--accent);
  background: var(--soft);
}

.primary-btn svg,
.secondary-btn svg {
  flex-shrink: 0;
  transition: transform 0.2s;
}

.primary-btn:hover svg:last-child {
  transform: translateX(3px);
}

.icon-btn,
.theme-toggle {
  border-radius: 9px;
}

.theme-toggle {
  border-color: var(--line);
  box-shadow: none;
}

.input-shell {
  border-radius: 8px;
  border-color: var(--line);
  background: var(--surface);
  box-shadow: none;
  color: var(--muted);
}

.input-shell:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 12%, transparent);
}

.input-shell input,
.input-shell select {
  color: var(--text);
}

.input-shell input::-moz-placeholder {
  color: var(--muted);
}

.input-shell input::placeholder {
  color: var(--muted);
}

.input-shell input:focus-visible,
.input-shell select:focus-visible {
  outline: none;
}

.filter-chip {
  border-radius: 6px;
  border-color: var(--line);
  color: var(--muted);
  background: var(--surface);
}

.filter-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.filter-chip-active,
.dark .filter-chip-active {
  background: var(--soft);
  color: var(--accent);
  border-color: var(--accent);
}

.announcement,
.dark .announcement {
  background: #dfd0fa;
  color: #35204f;
  border-bottom: 1px solid #b9a0e63d;
  font-size: 9px;
  line-height: 1.6;
}

.dark .announcement {
  background: #262031;
  color: #d5c0f2;
}

.storefront .store-header,
.admin-page header {
  background: color-mix(in srgb, var(--page) 92%, transparent);
  border-color: var(--line);
}

.dark .storefront .store-header,
.dark .admin-page header {
  background: color-mix(in srgb, var(--page) 92%, transparent);
  border-color: var(--line);
}

.dark .section-label {
  color: var(--accent);
}

.dark .surface-card,
.dark .setup-note,
.dark .cart-panel,
.dark .chat-panel,
.dark .finder-modal {
  background: var(--surface);
  border-color: var(--line);
}

.dark .secondary-btn,
.dark .input-shell {
  background: var(--surface);
  border-color: var(--line);
  color: var(--text);
}

.nav-link {
  position: relative;
}

.nav-link::after {
  content: "";
  position: absolute;
  height: 1px;
  inset: auto 0 -7px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.2s;
}

.nav-link:hover::after {
  transform: scaleX(1);
}

/* shared/variants.css */
.hover\:scale-105:hover {
  --tw-scale-x: 1.05;
  --tw-scale-y: 1.05;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.hover\:scale-\[1\.025\]:hover {
  --tw-scale-x: 1.025;
  --tw-scale-y: 1.025;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.hover\:border-zinc-300:hover {
  --tw-border-opacity: 1;
  border-color: rgb(212 212 216 / var(--tw-border-opacity, 1));
}

.hover\:border-zinc-400:hover {
  --tw-border-opacity: 1;
  border-color: rgb(161 161 170 / var(--tw-border-opacity, 1));
}

.hover\:border-zinc-500:hover {
  --tw-border-opacity: 1;
  border-color: rgb(113 113 122 / var(--tw-border-opacity, 1));
}

.hover\:bg-violet-300:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(196 181 253 / var(--tw-bg-opacity, 1));
}

.hover\:bg-zinc-100:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(244 244 245 / var(--tw-bg-opacity, 1));
}

.hover\:bg-zinc-50:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(250 250 250 / var(--tw-bg-opacity, 1));
}

.hover\:text-rose-500:hover {
  --tw-text-opacity: 1;
  color: rgb(244 63 94 / var(--tw-text-opacity, 1));
}

.hover\:text-zinc-950:hover {
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.hover\:underline:hover {
  text-decoration-line: underline;
}

.group:hover .group-hover\:block {
  display: block;
}

.group:hover .group-hover\:scale-105 {
  --tw-scale-x: 1.05;
  --tw-scale-y: 1.05;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.group:hover .group-hover\:scale-\[1\.04\] {
  --tw-scale-x: 1.04;
  --tw-scale-y: 1.04;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y))
    rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
    scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.group:hover .group-hover\:bg-white {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.group:hover .group-hover\:text-zinc-950 {
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.dark\:divide-white\/5:is(.dark *) > :not([hidden]) ~ :not([hidden]) {
  border-color: rgb(255 255 255 / 0.05);
}

.dark\:border-acid:is(.dark *) {
  --tw-border-opacity: 1;
  border-color: rgb(184 245 208 / var(--tw-border-opacity, 1));
}

.dark\:border-white\/10:is(.dark *) {
  border-color: rgb(255 255 255 / 0.1);
}

.dark\:border-white\/15:is(.dark *) {
  border-color: rgb(255 255 255 / 0.15);
}

.dark\:border-white\/5:is(.dark *) {
  border-color: rgb(255 255 255 / 0.05);
}

.dark\:bg-\[\#0c0c0f\]:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(12 12 15 / var(--tw-bg-opacity, 1));
}

.dark\:bg-\[\#0d0d10\]:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(13 13 16 / var(--tw-bg-opacity, 1));
}

.dark\:bg-\[\#101014\]:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(16 16 20 / var(--tw-bg-opacity, 1));
}

.dark\:bg-acid:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(184 245 208 / var(--tw-bg-opacity, 1));
}

.dark\:bg-acid\/10:is(.dark *) {
  background-color: rgb(184 245 208 / 0.1);
}

.dark\:bg-amber-400\/10:is(.dark *) {
  background-color: rgb(251 191 36 / 0.1);
}

.dark\:bg-amber-400\/15:is(.dark *) {
  background-color: rgb(251 191 36 / 0.15);
}

.dark\:bg-black\/10:is(.dark *) {
  background-color: rgb(0 0 0 / 0.1);
}

.dark\:bg-blue-400\/10:is(.dark *) {
  background-color: rgb(96 165 250 / 0.1);
}

.dark\:bg-blue-400\/15:is(.dark *) {
  background-color: rgb(96 165 250 / 0.15);
}

.dark\:bg-emerald-400\/10:is(.dark *) {
  background-color: rgb(52 211 153 / 0.1);
}

.dark\:bg-emerald-400\/15:is(.dark *) {
  background-color: rgb(52 211 153 / 0.15);
}

.dark\:bg-ink:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(13 12 18 / var(--tw-bg-opacity, 1));
}

.dark\:bg-ink\/90:is(.dark *) {
  background-color: rgb(13 12 18 / 0.9);
}

.dark\:bg-panel:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(23 21 30 / var(--tw-bg-opacity, 1));
}

.dark\:bg-rose-400\/10:is(.dark *) {
  background-color: rgb(251 113 133 / 0.1);
}

.dark\:bg-rose-500\/10:is(.dark *) {
  background-color: rgb(244 63 94 / 0.1);
}

.dark\:bg-violet-400\/15:is(.dark *) {
  background-color: rgb(167 139 250 / 0.15);
}

.dark\:bg-white:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.dark\:bg-white\/10:is(.dark *) {
  background-color: rgb(255 255 255 / 0.1);
}

.dark\:bg-white\/5:is(.dark *) {
  background-color: rgb(255 255 255 / 0.05);
}

.dark\:bg-white\/\[\.025\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.025);
}

.dark\:bg-white\/\[\.02\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.02);
}

.dark\:bg-white\/\[\.055\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.055);
}

.dark\:bg-white\/\[\.05\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.05);
}

.dark\:bg-white\/\[\.06\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.06);
}

.dark\:bg-white\/\[\.07\]:is(.dark *) {
  background-color: rgb(255 255 255 / 0.07);
}

.dark\:bg-zinc-800:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(39 39 42 / var(--tw-bg-opacity, 1));
}

.dark\:bg-zinc-900:is(.dark *) {
  --tw-bg-opacity: 1;
  background-color: rgb(24 24 27 / var(--tw-bg-opacity, 1));
}

.dark\:bg-gradient-to-br:is(.dark *) {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

.dark\:from-\[\#1c1330\]:is(.dark *) {
  --tw-gradient-from: #1c1330 var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(28 19 48 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}

.dark\:via-zinc-950:is(.dark *) {
  --tw-gradient-to: rgb(9 9 11 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops:
    var(--tw-gradient-from), #09090b var(--tw-gradient-via-position),
    var(--tw-gradient-to);
}

.dark\:to-zinc-950:is(.dark *) {
  --tw-gradient-to: #09090b var(--tw-gradient-to-position);
}

.dark\:text-acid:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(184 245 208 / var(--tw-text-opacity, 1));
}

.dark\:text-amber-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(252 211 77 / var(--tw-text-opacity, 1));
}

.dark\:text-blue-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(147 197 253 / var(--tw-text-opacity, 1));
}

.dark\:text-emerald-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(110 231 183 / var(--tw-text-opacity, 1));
}

.dark\:text-ink:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(13 12 18 / var(--tw-text-opacity, 1));
}

.dark\:text-rose-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(253 164 175 / var(--tw-text-opacity, 1));
}

.dark\:text-violet-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(196 181 253 / var(--tw-text-opacity, 1));
}

.dark\:text-white:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.dark\:text-zinc-200:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(228 228 231 / var(--tw-text-opacity, 1));
}

.dark\:text-zinc-300:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(212 212 216 / var(--tw-text-opacity, 1));
}

.dark\:text-zinc-400:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(161 161 170 / var(--tw-text-opacity, 1));
}

.dark\:text-zinc-700:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(63 63 70 / var(--tw-text-opacity, 1));
}

.dark\:text-zinc-950:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(9 9 11 / var(--tw-text-opacity, 1));
}

.dark\:hover\:bg-white\/20:hover:is(.dark *) {
  background-color: rgb(255 255 255 / 0.2);
}

.dark\:hover\:bg-white\/5:hover:is(.dark *) {
  background-color: rgb(255 255 255 / 0.05);
}

.dark\:hover\:bg-white\/\[\.025\]:hover:is(.dark *) {
  background-color: rgb(255 255 255 / 0.025);
}

.dark\:hover\:text-white:hover:is(.dark *) {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

@media (min-width: 640px) {
  .sm\:left-8 {
    left: 2rem;
  }

  .sm\:right-1 {
    right: 0.25rem;
  }

  .sm\:right-8 {
    right: 2rem;
  }

  .sm\:top-12 {
    top: 3rem;
  }

  .sm\:flex {
    display: flex;
  }

  .sm\:grid {
    display: grid;
  }

  .sm\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .sm\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .sm\:flex-row {
    flex-direction: row;
  }

  .sm\:items-end {
    align-items: flex-end;
  }

  .sm\:gap-3 {
    gap: 0.75rem;
  }

  .sm\:p-10 {
    padding: 2.5rem;
  }

  .sm\:p-12 {
    padding: 3rem;
  }

  .sm\:p-6 {
    padding: 1.5rem;
  }

  .sm\:p-8 {
    padding: 2rem;
  }

  .sm\:px-12 {
    padding-left: 3rem;
    padding-right: 3rem;
  }

  .sm\:px-8 {
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .sm\:py-28 {
    padding-top: 7rem;
    padding-bottom: 7rem;
  }

  .sm\:pb-28 {
    padding-bottom: 7rem;
  }

  .sm\:text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }

  .sm\:text-6xl {
    font-size: 3.75rem;
    line-height: 1;
  }

  .sm\:text-\[10px\] {
    font-size: 10px;
  }

  .sm\:text-\[11px\] {
    font-size: 11px;
  }

  .sm\:text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
}

@media (min-width: 1024px) {
  .lg\:block {
    display: block;
  }

  .lg\:flex {
    display: flex;
  }

  .lg\:hidden {
    display: none;
  }

  .lg\:translate-x-0 {
    --tw-translate-x: 0px;
    transform: translate(var(--tw-translate-x), var(--tw-translate-y))
      rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
      scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  }

  .lg\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .lg\:grid-cols-\[\.72fr_1\.28fr\] {
    grid-template-columns: 0.72fr 1.28fr;
  }

  .lg\:grid-cols-\[1\.03fr_\.97fr\] {
    grid-template-columns: 1.03fr 0.97fr;
  }

  .lg\:grid-cols-\[1\.05fr_1fr\] {
    grid-template-columns: 1.05fr 1fr;
  }

  .lg\:grid-cols-\[1\.4fr_repeat\(3\2c 1fr\)\] {
    grid-template-columns: 1.4fr repeat(3, 1fr);
  }

  .lg\:grid-cols-\[1fr_\.72fr\] {
    grid-template-columns: 1fr 0.72fr;
  }

  .lg\:flex-row {
    flex-direction: row;
  }

  .lg\:items-end {
    align-items: flex-end;
  }

  .lg\:items-center {
    align-items: center;
  }

  .lg\:p-16 {
    padding: 4rem;
  }

  .lg\:px-20 {
    padding-left: 5rem;
    padding-right: 5rem;
  }

  .lg\:py-10 {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
  }

  .lg\:py-20 {
    padding-top: 5rem;
    padding-bottom: 5rem;
  }

  .lg\:pl-\[270px\] {
    padding-left: 270px;
  }
}

@media (min-width: 1280px) {
  .xl\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .xl\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .xl\:grid-cols-\[1\.55fr_\.75fr\] {
    grid-template-columns: 1.55fr 0.75fr;
  }

  .xl\:p-10 {
    padding: 2.5rem;
  }

  .xl\:p-16 {
    padding: 4rem;
  }

  .xl\:text-6xl {
    font-size: 3.75rem;
    line-height: 1;
  }
}

/* shared/dialogs.css */
.cart-panel,
.chat-panel,
.finder-modal {
  background: var(--surface);
  color: var(--text);
}

/* motion.css */
/* Shared native animation and visibility support, loaded by index.css. */
[hidden] {
  display: none !important;
}
[data-hover] {
  transition: transform 0.25s ease;
}
@media (prefers-reduced-motion: no-preference) {
  .category-card:hover {
    transform: translateY(-7px);
  }
  .stat-card:hover {
    transform: translateY(-4px);
  }
}

/* dialog.css */
.app-dialog {
  width: min(640px, calc(100% - 32px));
  max-height: calc(100dvh - 40px);
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 28px;
  background: var(--surface);
  color: var(--text);
  box-shadow: 0 30px 100px #0005;
  margin: auto;
}
.app-dialog::backdrop {
  background: #100c1bb3;
  backdrop-filter: blur(6px);
}
.dialog-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.dialog-heading h2 {
  margin-top: 12px;
  overflow-wrap: anywhere;
}
.dialog-heading .icon-btn {
  flex-shrink: 0;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
.form-grid label,
.stack-form label {
  display: grid;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
}
.form-grid input,
.form-grid select,
.form-grid textarea,
.stack-form input,
.stack-form textarea,
.stack-form select {
  width: 100%;
  min-width: 0;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 9px;
  color: var(--text);
  background: var(--surface);
  font-weight: 400;
}
.form-grid textarea,
.stack-form textarea {
  min-height: 96px;
  resize: vertical;
}
.form-wide {
  grid-column: 1 / -1;
}
.form-grid .checkbox-label,
.stack-form .checkbox-label {
  display: flex;
  align-items: center;
}
.checkbox-label input {
  width: auto;
}
.stack-form {
  display: grid;
  gap: 18px;
}
.form-hint {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.8;
}
.form-error {
  border: 1px solid #fb718555;
  color: #be123c;
  background: #fb718515;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
}
.dark .form-error {
  color: #fda4af;
}
.form-success {
  padding: 14px;
  border: 1px solid var(--line);
  background: var(--soft);
  border-radius: 10px;
  font-size: 13px;
  color: var(--mint);
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}
.danger-btn {
  color: #be123c;
  border: 1px solid #fb718560;
  border-radius: 9px;
  padding: 10px 14px;
  font-size: 12px;
}
.dark .danger-btn {
  color: #fda4af;
}
.notice {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: max-content;
  max-width: calc(100% - 40px);
  padding: 15px 20px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--text);
  box-shadow: var(--shadow);
  font-size: 13px;
}
.empty-state {
  padding: 36px 20px;
  color: var(--muted);
  font-size: 14px;
  text-align: center;
  grid-column: 1 / -1;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.detail-list {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr);
  gap: 12px 20px;
  margin: 24px 0;
  font-size: 13px;
}
.detail-list dt {
  color: var(--muted);
}
.detail-list dd {
  overflow-wrap: anywhere;
}
.order-status {
  display: inline-block;
  padding: 7px 12px;
  border-radius: 20px;
  color: var(--accent);
  background: var(--soft);
  font-size: 12px;
  font-weight: 600;
}
.order-items {
  display: grid;
  gap: 10px;
  margin: 16px 0;
  font-size: 13px;
}
.order-total {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 0;
  border-top: 1px solid var(--line);
}
@media (max-width: 639px) {
  .app-dialog {
    padding: 20px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .detail-list {
    grid-template-columns: 100px minmax(0, 1fr);
  }
}

/* Shared responsive rules */
@keyframes note-float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-8px);
  }
}
@keyframes signal {
  from {
    transform: scaleY(0.5);
  }

  to {
    transform: scaleY(1);
  }
}
@media (max-width: 639px) {
  .shell {
    padding-inline: 20px;
  }
}
@media (max-width: 359px) {
  .shell {
    padding-inline: 16px;
  }
}
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    animation: none !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Retain content without movement when browser animation is reduced. */

  .storefront main [style],
  .auth-page [style]:not(img),
  .admin-page main [style],
  .finder-modal[style],
  .chat-panel[style],
  .cart-panel[style],
  #root > div > div[style] {
    transform: none !important;
    opacity: 1 !important;
  }

  .auth-art img {
    transform: none !important;
  }
}

/* Chat */
.chat-panel {
  max-height: calc(100dvh - 120px);
  border-radius: 14px;
  border-color: var(--line);
}

/* Keep long replies readable and controls visibly busy without changing the layout. */
.chat-panel [data-field="messages"] {
  min-height: 0;
}
.chat-panel [data-field="message"] {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.chat-panel :disabled {
  cursor: wait;
  opacity: 0.6;
}

```

## assets/css/tuner/tuner.css

```css
@import url("../shared/practice.css");

.tuner-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  gap: 24px;
}
.tuner-container {
  padding: 32px;
  text-align: center;
  min-width: 0;
  align-self: start;
}
.tuner-microphone {
  color: var(--muted);
  font-size: 13px;
  min-height: 24px;
}
.tuner-note {
  font-family: "Space Grotesk", Inter, system-ui;
  font-size: clamp(72px, 12vw, 116px);
  font-weight: 600;
  line-height: 1.2;
  margin-top: 24px;
}
.tuner-octave {
  font-size: 0.45em;
  color: var(--muted);
  margin-left: 4px;
}
.tuner-frequency {
  color: var(--muted);
  font-size: 18px;
  font-variant-numeric: tabular-nums;
}
.tuner-cents {
  margin-top: 8px;
  color: var(--accent);
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}
.tuner-status {
  font-weight: 600;
  margin-top: 24px;
  color: var(--muted);
}
.tuner-container[data-tuning="in-tune"] .tuner-status {
  color: var(--mint);
}
.tuner-container[data-tuning="flat"] .tuner-status,
.tuner-container[data-tuning="sharp"] .tuner-status {
  color: var(--accent);
}
.tuner-meter {
  margin-top: 24px;
}
.tuner-meter-track {
  position: relative;
  height: 36px;
  margin-inline: 8px;
  border-bottom: 2px solid var(--line);
  background: repeating-linear-gradient(
    90deg,
    var(--line) 0 1px,
    transparent 1px 10%
  );
}
.tuner-meter-center {
  position: absolute;
  left: 45%;
  width: 10%;
  height: 100%;
  background: var(--mint);
  opacity: 0.18;
  border-radius: 4px;
}
.tuner-meter-center::after {
  content: "";
  position: absolute;
  left: 50%;
  height: 100%;
  width: 2px;
  background: var(--text);
}
.tuner-indicator {
  position: absolute;
  left: 50%;
  top: -5px;
  width: 4px;
  height: 45px;
  background: var(--accent);
  border-radius: 4px;
  transform: translateX(-50%);
  transition: left 100ms linear;
}
.tuner-container[data-tuning="in-tune"] .tuner-indicator {
  background: var(--mint);
}
.tuner-meter-labels {
  display: flex;
  justify-content: space-between;
  gap: 4px;
  margin-top: 12px;
  color: var(--muted);
  font-size: 11px;
}
.tuner-controls {
  justify-content: center;
  margin-top: 32px;
}
.tuner-privacy {
  margin-top: 24px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.7;
}
.tuner-container .form-error {
  margin-top: 20px;
}
.tuner-strings {
  list-style: none;
  margin-top: 24px;
}
.tuner-strings li {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--line);
  padding: 12px 8px;
  font-size: 12px;
  color: var(--muted);
}
.tuner-strings li > :last-child {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.tuner-strings strong {
  color: var(--text);
  font-size: 20px;
}
.tuner-strings li[data-active] {
  background: var(--soft);
  border-radius: 8px;
}
.tuner-strings li[data-active] strong {
  color: var(--accent);
}
.tuner-tips .practice-link {
  display: inline-block;
  margin-top: 16px;
}
@media (max-width: 767px) {
  .tuner-layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .tuner-container {
    padding: 24px 20px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .tuner-indicator {
    transition: none;
  }
}

```

## assets/js/account/account.js

```javascript
import {
  imageSource,
  field,
  clone,
  peso,
  api,
  busy,
  empty,
  formError,
  notice,
  orderDetails,
} from "../shared/shared.js";

export function mountAccount(page, app) {
  let alive = true,
    orders = [],
    saved = [];
  field(page, "greeting").textContent =
    `Welcome back, ${app.user.name.split(" ")[0]}.`;
  const profile = page.querySelector('[data-form="profile"]');
  for (const name of ["name", "email", "phone", "address"])
    profile.elements[name].value = app.user[name] || "";
  async function loadOrders() {
    try {
      const data = await api("/orders");
      if (!alive) return;
      orders = data.orders;
      if (!orders.length)
        return empty(
          field(page, "orders"),
          "Your first order starts with your next favorite instrument.",
        );
      field(page, "orders").replaceChildren(
        ...orders.map((order) => {
          const card = clone("order-card");
          card.dataset.orderId = order.id;
          for (const key of ["id", "date", "product", "status"])
            field(card, key).textContent = order[key];
          field(card, "amount").textContent = peso(order.amount);
          return card;
        }),
      );
    } catch (error) {
      if (alive) empty(field(page, "orders"), error.message);
    }
  }
  async function loadSaved() {
    try {
      const data = await api("/account/saved");
      if (!alive) return;
      saved = data.products;
      field(page, "finder-profile").textContent = data.profile
        ? `Last Guitar Finder: ${data.profile.level} · ${data.profile.category} · ${peso(data.profile.budget)}`
        : "Find instruments suited to your experience and budget.";
      if (!saved.length)
        return empty(
          field(page, "saved"),
          "Tap the heart on an instrument to save it here.",
        );
      field(page, "saved").replaceChildren(
        ...saved.map((product) => {
          const item = clone("saved-item");
          item.dataset.productId = product.id;
          field(item, "image").src = imageSource(product.image);
          field(item, "image").alt = product.name;
          field(item, "name").textContent = product.name;
          field(item, "price").textContent = peso(product.price);
          return item;
        }),
      );
    } catch (error) {
      if (alive) empty(field(page, "saved"), error.message);
    }
  }
  page.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    if (form.querySelector("[type=submit]").disabled) return;
    const values = Object.fromEntries(new FormData(form)),
      password = form.dataset.form === "password";
    if (password && values.password !== values.confirm)
      return formError(form, "The new passwords do not match.");
    busy(form, true);
    formError(form, "");
    try {
      const data = await api(password ? "/auth/password" : "/auth/profile", {
        method: password ? "POST" : "PATCH",
        body: values,
      });
      if (!alive) return;
      app.user = data.user;
      if (password) form.reset();
      notice(password ? "Password updated." : "Profile saved.");
    } catch (error) {
      if (alive) formError(form, error.message);
    } finally {
      if (alive)
        busy(form, false, password ? "Update password" : "Save profile");
    }
  });
  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (action === "store") app.navigate("storefront");
    if (action === "logout") app.logout();
    if (action === "refresh-orders") loadOrders();
    if (action === "view-order")
      orderDetails(
        orders.find(
          (order) =>
            order.id === button.closest("[data-order-id]").dataset.orderId,
        ),
      );
    if (action === "saved-shop") {
      app.searchProduct = saved.find(
        (p) =>
          p.id ===
          Number(button.closest("[data-product-id]").dataset.productId),
      ).name;
      app.navigate("storefront");
    }
    if (action === "find-guitar") {
      app.openFinder = true;
      app.navigate("storefront");
    }
    if (action === "unsave") {
      button.disabled = true;
      try {
        await api(
          `/account/saved/${button.closest("[data-product-id]").dataset.productId}`,
          { method: "DELETE" },
        );
        if (alive) loadSaved();
      } catch (error) {
        notice(error.message);
        button.disabled = false;
      }
    }
  });
  loadOrders();
  loadSaved();
  return {
    destroy() {
      alive = false;
    },
  };
}

```

## assets/js/admin/admin.js

```javascript
import {
  imageSource,
  $,
  $$,
  field,
  text,
  clone,
  peso,
  animate,
  dismiss,
  api,
  dialog,
  notice,
  empty,
  busy,
  formError,
  orderDetails,
} from "../shared/shared.js";

const labels = {
  overview: "Overview",
  sales: "Sales directory",
  products: "Products",
  customers: "Customers",
  settings: "Settings",
};
const transitions = {
  Pending: ["Processing", "Cancelled"],
  Processing: ["Shipped", "Cancelled"],
  Shipped: ["Delivered"],
  Delivered: ["Refunded"],
  Cancelled: [],
  Refunded: [],
};

export function mountAdmin(page, app) {
  let active = "",
    sales = [],
    products = [],
    customers = [],
    query = "",
    status = "All",
    pageNumber = 0,
    period = "week";
  let alive = true,
    generation = 0,
    backdrop,
    summary;
  const main = field(page, "admin-view");
  text(page, "admin-name", app.user.name);
  function saleRow(sale, recent = false) {
    const row = clone(recent ? "recent-sale" : "sale-row");
    row.dataset.orderId = sale.id;
    for (const key of [
      "id",
      "customer",
      "email",
      "product",
      ...(recent ? [] : ["date", "payment"]),
    ])
      text(row, key, sale[key]);
    text(row, "amount", peso(sale.amount));
    text(row, "status", sale.status);
    field(row, "status").className =
      `order-status status-${sale.status.toLowerCase()}`;
    return row;
  }
  function renderSales() {
    const filtered = sales.filter(
      (sale) =>
        (status === "All" || sale.status === status) &&
        `${sale.id} ${sale.customer} ${sale.email} ${sale.product}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    );
    const recent = active === "overview";
    pageNumber = Math.max(
      0,
      Math.min(pageNumber, Math.ceil(filtered.length / 10) - 1),
    );
    const shown = recent
      ? filtered.slice(0, 5)
      : filtered.slice(pageNumber * 10, pageNumber * 10 + 10);
    field(main, "sales-rows").replaceChildren(
      ...shown.map((sale) => saleRow(sale, recent)),
    );
    field(main, "sales-empty").hidden = shown.length > 0;
    if (!recent) {
      text(
        main,
        "sales-count",
        filtered.length
          ? `Showing ${pageNumber * 10 + 1}–${pageNumber * 10 + shown.length} of ${filtered.length} orders`
          : "No matching orders",
      );
      $(main, '[data-action="sales-previous"]').disabled = pageNumber === 0;
      $(main, '[data-action="sales-next"]').disabled =
        (pageNumber + 1) * 10 >= filtered.length;
    }
  }
  function renderProducts() {
    const filtered = products.filter((product) =>
      `${product.name} ${product.brand}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    );
    if (!filtered.length)
      return empty(
        field(main, "admin-products"),
        "No products match your search.",
      );
    field(main, "admin-products").replaceChildren(
      ...filtered.map((product) => {
        const card = clone("admin-product");
        card.dataset.productId = product.id;
        field(card, "image").src = imageSource(product.image);
        field(card, "image").alt = product.name;
        text(card, "name", product.name);
        text(card, "category", `${product.brand} · ${product.category}`);
        text(card, "price", peso(product.price));
        text(
          card,
          "stock",
          product.active ? `${product.stock} in stock` : "Archived",
        );
        $(card, '[data-action="edit-product"]').setAttribute(
          "aria-label",
          `Edit ${product.name}`,
        );
        return card;
      }),
    );
  }
  function renderCustomers() {
    const filtered = customers.filter((customer) =>
      `${customer.name} ${customer.email}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    );
    if (!filtered.length)
      return empty(field(main, "customers"), "No customers match your search.");
    field(main, "customers").replaceChildren(
      ...filtered.map((customer) => {
        const card = clone("customer");
        text(
          card,
          "initials",
          customer.name
            .split(" ")
            .map((part) => part[0])
            .slice(0, 2)
            .join(""),
        );
        text(card, "customer", customer.name);
        text(card, "email", customer.email);
        text(card, "order", `${customer.orders} orders`);
        text(card, "amount", peso(customer.amount));
        return card;
      }),
    );
  }
  function renderSummary() {
    for (const key of [
      "gross_revenue",
      "total_orders",
      "new_customers",
      "low_stock_items",
    ])
      text(
        main,
        key,
        key === "gross_revenue" ? peso(summary[key]) : summary[key],
      );
    text(
      main,
      "today",
      new Date().toLocaleDateString("en-PH", {
        weekday: "long",
        month: "long",
        day: "numeric",
      }),
    );
    text(
      main,
      "admin-greeting",
      `Welcome back, ${app.user.name.split(" ")[0]}.`,
    );
    field(main, "report-period").value = period;
    const chart = field(main, "revenue-chart"),
      max = Math.max(...summary.chart.map((day) => day.amount), 0);
    if (!max) empty(chart, "No delivered revenue in this period.");
    else {
      const ns = "http://www.w3.org/2000/svg",
        svg = document.createElementNS(ns, "svg");
      svg.setAttribute("viewBox", "0 0 700 230");
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Delivered revenue by day");
      const title = document.createElementNS(ns, "title");
      title.textContent = "Daily delivered revenue";
      svg.append(title);
      const width = 700 / summary.chart.length;
      summary.chart.forEach((day, index) => {
        const rect = document.createElementNS(ns, "rect"),
          height = (day.amount / max) * 185;
        for (const [name, value] of Object.entries({
          x: index * width + 3,
          y: 200 - height,
          width: Math.max(width - 6, 1),
          height,
          rx: 4,
        }))
          rect.setAttribute(name, String(value));
        const title = document.createElementNS(ns, "title");
        title.textContent = `${day.date}: ${peso(day.amount)}`;
        rect.append(title);
        svg.append(rect);
      });
      const caption = document.createElement("p");
      caption.className = "form-hint";
      caption.textContent = `${summary.chart[0].date} — ${summary.chart.at(-1).date} · Peak ${peso(max)}`;
      chart.replaceChildren(svg, caption);
    }
    const categories = field(main, "category-report"),
      total = Object.values(summary.categories).reduce(
        (sum, value) => sum + value,
        0,
      );
    if (!total) empty(categories, "Category totals appear after delivery.");
    else
      categories.replaceChildren(
        ...Object.entries(summary.categories).map(([category, value]) => {
          const row = document.createElement("div"),
            label = document.createElement("p"),
            meter = document.createElement("meter");
          label.textContent = `${category} · ${Math.round((value / total) * 100)}%`;
          meter.min = 0;
          meter.max = total;
          meter.value = value;
          meter.setAttribute("aria-label", `${category} revenue`);
          row.append(label, meter);
          return row;
        }),
      );
  }
  function closeSidebar() {
    const sidebar = $(page, "aside");
    sidebar.classList.add("-translate-x-full");
    sidebar.classList.remove("translate-x-0");
    if (backdrop) {
      dismiss(backdrop);
      backdrop = null;
    }
  }
  async function navigate(next) {
    if (!alive) return;
    active = next;
    query = "";
    status = "All";
    pageNumber = 0;
    const request = ++generation;
    main.replaceChildren(clone(next === "products" ? "admin-products" : next));
    text(page, "admin-title", labels[next]);
    $$(page, "aside nav button").forEach((button) => {
      const selected = button.dataset.action === next;
      button.setAttribute("aria-current", selected ? "page" : "false");
      button.className = `flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${selected ? "bg-zinc-950 text-white dark:bg-acid dark:text-ink" : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-white/5"}`;
    });
    closeSidebar();
    animate(main.firstElementChild);
    try {
      if (next === "overview") {
        const [report, orders] = await Promise.all([
          api(`/admin/summary?period=${period}`),
          api("/admin/sales"),
        ]);
        if (!alive || request !== generation) return;
        summary = report;
        sales = orders.sales;
        renderSummary();
        renderSales();
        text(page, "order-count", sales.length);
      } else if (next === "sales") {
        const data = await api("/admin/sales");
        if (!alive || request !== generation) return;
        sales = data.sales;
        renderSales();
      } else if (next === "products") {
        const data = await api("/admin/products");
        if (!alive || request !== generation) return;
        products = data.products;
        renderProducts();
      } else if (next === "customers") {
        const data = await api("/admin/customers");
        if (!alive || request !== generation) return;
        customers = data.customers;
        renderCustomers();
      } else if (next === "settings") {
        const data = await api("/admin/settings");
        if (!alive || request !== generation) return;
        const form = main.querySelector("form");
        for (const [key, value] of Object.entries(data.settings))
          if (form.elements[key]) form.elements[key].value = value;
      }
    } catch (error) {
      if (!alive || request !== generation) return;
      if (error.status === 401) {
        app.user = null;
        app.navigate("auth", "admin");
        notice("Your session expired. Please sign in again.");
        return;
      }
      const message = document.createElement("p");
      message.className = "form-error";
      message.textContent = error.message;
      message.setAttribute("role", "alert");
      main.prepend(message);
    }
  }
  function productEditor(product) {
    const panel = dialog(
        product ? "Edit instrument" : "Add an instrument",
        "product-form",
      ),
      form = panel.querySelector("form");
    if (product)
      for (const [key, value] of Object.entries(product)) {
        if (!form.elements[key]) continue;
        if (key === "active") form.elements[key].checked = value;
        else
          form.elements[key].value = key === "specs" ? value.join("\n") : value;
      }
    const archive = $(form, '[data-action="archive-product"]');
    archive.hidden = !product?.active;
    archive.addEventListener("click", async () => {
      archive.disabled = true;
      try {
        await api(`/admin/products/${product.id}`, { method: "DELETE" });
        panel.close();
        notice("Product archived.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
        archive.disabled = false;
      }
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      busy(form, true);
      formError(form, "");
      const values = Object.fromEntries(new FormData(form));
      values.price = Number(values.price);
      values.stock = Number(values.stock);
      values.active = form.elements.active.checked;
      values.specs = values.specs
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean);
      try {
        await api(
          product ? `/admin/products/${product.id}` : "/admin/products",
          { method: product ? "PUT" : "POST", body: values },
        );
        panel.close();
        notice("Product saved.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
      } finally {
        busy(form, false, "Save product");
      }
    });
  }
  function editOrder(order) {
    const panel = orderDetails(order),
      choices = transitions[order.status] || [];
    if (!choices.length) return;
    const form = clone("order-status");
    field(panel, "dialog-body").append(form);
    form.elements.status.replaceChildren(
      ...choices.map((status) => new Option(status, status)),
    );
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      busy(form, true);
      formError(form, "");
      try {
        await api(`/admin/sales/${order.id}`, {
          method: "PATCH",
          body: { status: form.elements.status.value },
        });
        panel.close();
        notice("Order updated.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
      } finally {
        busy(form, false, "Update order");
      }
    });
  }
  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (labels[action]) navigate(action);
    if (action === "store") app.navigate("storefront");
    if (action === "admin-account") app.navigate("account");
    if (action === "logout") app.logout();
    if (action === "close-sidebar") closeSidebar();
    if (action === "sidebar") {
      const sidebar = $(page, "aside");
      sidebar.classList.remove("-translate-x-full");
      sidebar.classList.add("translate-x-0");
      if (!backdrop) {
        backdrop = clone("sidebar-backdrop");
        page.prepend(backdrop);
        animate(backdrop);
      }
    }
    if (action === "add-product") productEditor();
    if (action === "edit-product")
      productEditor(
        products.find(
          (product) =>
            product.id ===
            Number(button.closest("[data-product-id]").dataset.productId),
        ),
      );
    if (action === "edit-order")
      editOrder(
        sales.find(
          (order) =>
            order.id === button.closest("[data-order-id]").dataset.orderId,
        ),
      );
    if (action === "sales-previous") {
      pageNumber--;
      renderSales();
    }
    if (action === "sales-next") {
      pageNumber++;
      renderSales();
    }
    if (action === "export-sales") {
      try {
        const response = await fetch(
          `/api/admin/sales/export?${new URLSearchParams({ q: query, status })}`,
        );
        if (!response.ok)
          throw new Error(
            "Unable to export sales. Please sign in and try again.",
          );
        const url = URL.createObjectURL(await response.blob()),
          link = document.createElement("a");
        link.href = url;
        link.download = "audia-sales.csv";
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      } catch (error) {
        notice(error.message);
      }
    }
    if (action === "notifications") {
      const panel = dialog("Store notifications", "notifications");
      try {
        const data = await api("/admin/summary");
        if (!panel.isConnected) return;
        const alerts = [
          `${data.pending_orders} orders awaiting processing.`,
          ...data.low_stock.map(
            (product) => `${product.name}: ${product.stock} left in stock.`,
          ),
        ];
        field(panel, "alerts").replaceChildren(
          ...alerts.map((message) => {
            const item = document.createElement("li");
            item.textContent = message;
            return item;
          }),
        );
      } catch (error) {
        empty(field(panel, "alerts"), error.message);
      }
    }
  });
  page.addEventListener("input", (event) => {
    const name = event.target.dataset.field;
    if (name === "sales-query") {
      query = event.target.value;
      pageNumber = 0;
      renderSales();
    }
    if (name === "product-query") {
      query = event.target.value;
      renderProducts();
    }
    if (name === "customer-query") {
      query = event.target.value;
      renderCustomers();
    }
  });
  page.addEventListener("change", (event) => {
    if (event.target.dataset.field === "sales-status") {
      status = event.target.value;
      pageNumber = 0;
      renderSales();
    }
    if (event.target.dataset.field === "report-period") {
      period = event.target.value;
      navigate("overview");
    }
  });
  page.addEventListener("submit", async (event) => {
    if (event.target.dataset.form !== "settings") return;
    event.preventDefault();
    const form = event.target;
    if (form.querySelector("[type=submit]").disabled) return;
    busy(form, true);
    formError(form, "");
    try {
      const data = await api("/admin/settings", {
        method: "PUT",
        body: Object.fromEntries(new FormData(form)),
      });
      if (alive) text(page, "store-name", data.settings.store_name);
      notice("Store settings saved.");
    } catch (error) {
      formError(form, error.message);
    } finally {
      busy(form, false, "Save settings");
    }
  });
  api("/admin/settings")
    .then((data) => {
      if (alive) text(page, "store-name", data.settings.store_name);
    })
    .catch(() => {});
  navigate("overview");
  return {
    destroy() {
      alive = false;
      generation++;
    },
  };
}

```

## assets/js/auth/auth.js

```javascript
import { $, field, icon, api } from "../shared/shared.js";

const selectedRole =
  "flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white";
const plainRole =
  "flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition text-zinc-500";

export function mountAuth(page, app, initialRole) {
  let role = initialRole === "admin" ? "admin" : "customer";
  let mode =
    initialRole === "reset"
      ? "reset"
      : initialRole === "register"
        ? "register"
        : "login";
  let loading = false,
    alive = true;
  const titles = {
    login: "Welcome to AUDIA.",
    register: "Find your people. Find your sound.",
    forgot: "Let’s get you back in.",
    reset: "A fresh start.",
  };
  const subtitles = {
    login:
      "Sign in to your account or open the store administration workspace.",
    register:
      "Create your account to save instruments, place orders, and keep track of your gear.",
    forgot:
      "Enter your account email and we’ll send you a password reset link.",
    reset: "Choose a new password for your AUDIA account.",
  };
  const labels = {
    login: role === "admin" ? "Open dashboard" : "Sign in",
    register: "Create account",
    forgot: "Send reset link",
    reset: "Reset password",
  };
  function error(message) {
    field(page, "login-error").textContent = message;
    field(page, "login-error").hidden = !message;
  }
  function success(message) {
    field(page, "auth-success").textContent = message;
    field(page, "auth-success").hidden = !message;
  }
  function render() {
    field(page, "auth-title").textContent = titles[mode];
    field(page, "auth-subtitle").textContent = subtitles[mode];
    field(page, "roles").hidden = mode !== "login";
    field(page, "signup").hidden = mode !== "login" || role === "admin";
    field(page, "back-login").hidden = mode === "login";
    field(page, "login-options").hidden = mode !== "login";
    for (const [name, visible] of [
      ["name", mode === "register"],
      ["email", mode !== "reset"],
      ["password", mode !== "forgot"],
      ["confirm", ["register", "reset"].includes(mode)],
    ]) {
      field(page, `${name}-wrap`).hidden = !visible;
      field(page, name).required = visible;
      field(page, name).disabled = !visible;
    }
    field(page, "password").minLength = mode === "login" ? 1 : 10;
    field(page, "password").autocomplete =
      mode === "login" ? "current-password" : "new-password";
    field(page, "password-hint").hidden = !["register", "reset"].includes(mode);
    for (const option of ["customer", "admin"]) {
      const button = $(page, `[data-action="role-${option}"]`);
      button.className = role === option ? selectedRole : plainRole;
      button.setAttribute("aria-pressed", String(role === option));
    }
    labels.login = role === "admin" ? "Open dashboard" : "Sign in";
    const submit = field(page, "login-submit");
    submit.disabled = loading;
    submit.replaceChildren(
      loading ? "Please wait… " : labels[mode] + " ",
      icon("arrow-right", 16),
    );
  }
  function change(next) {
    mode = next;
    error("");
    success("");
    render();
  }
  page.addEventListener("click", (event) => {
    const action = event.target.closest("[data-action]")?.dataset.action;
    if (action === "home" || action === "store") {
      app.catalogCategory = "";
      app.navigate(app.user ? "storefront" : "landing");
    }
    if (loading) return;
    if (action === "role-customer" || action === "role-admin") {
      role = action.slice(5);
      error("");
      render();
    }
    if (action === "register") {
      role = "customer";
      app.navigate("auth", "register");
    }
    if (action === "forgot") change("forgot");
    if (action === "back-login") {
      if (mode === "register") app.navigate("auth");
      else change("login");
    }
    if (action === "password") {
      const input = field(page, "password"),
        showing = input.type === "password";
      input.type = showing ? "text" : "password";
      const button = $(page, '[data-action="password"]');
      button.setAttribute(
        "aria-label",
        showing ? "Hide password" : "Show password",
      );
      button.replaceChildren(icon(showing ? "eye-off" : "eye", 16));
    }
  });
  page.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (loading) return;
    const password = field(page, "password").value;
    if (
      ["register", "reset"].includes(mode) &&
      password !== field(page, "confirm").value
    )
      return error("The passwords do not match.");
    loading = true;
    error("");
    success("");
    render();
    const submitted = mode;
    try {
      const paths = {
        login: "login",
        register: "register",
        forgot: "forgot-password",
        reset: "reset-password",
      };
      const data = await api(`/auth/${paths[submitted]}`, {
        method: "POST",
        body: {
          email: field(page, "email").value,
          password,
          name: field(page, "name").value,
          role,
          remember: field(page, "remember").checked,
          token: app.resetToken || "",
        },
      });
      if (!alive) return;
      if (submitted === "register") {
        sessionStorage.setItem(
          "audia-signup-email",
          field(page, "email").value,
        );
        sessionStorage.setItem("audia-auth-message", data.message);
        field(page, "password").value = "";
        field(page, "confirm").value = "";
        app.navigate("auth");
      } else if (data.user) app.login(data.user);
      else {
        if (submitted === "reset") {
          app.resetToken = "";
          change("login");
        }
        success(data.message);
      }
    } catch (failure) {
      if (alive) error(failure.message);
    } finally {
      loading = false;
      if (alive) render();
    }
  });
  render();
  if (mode === "login" && sessionStorage.getItem("audia-auth-message")) {
    field(page, "email").value =
      sessionStorage.getItem("audia-signup-email") || "";
    success(sessionStorage.getItem("audia-auth-message"));
    sessionStorage.removeItem("audia-auth-message");
    sessionStorage.removeItem("audia-signup-email");
  }
  return {
    destroy() {
      alive = false;
    },
  };
}

```

## assets/js/catalog/storefront.js

```javascript
import {
  imageSource,
  api,
  dialog,
  notice,
  formError,
  busy,
  orderDetails,
  readCart,
  writeCart,
  $,
  $$,
  field,
  text,
  clone,
  icon,
  peso,
  animate,
  dismiss,
} from "../shared/shared.js";

const questions = [
  { key: "budget", title: "What is your budget?" },
  {
    key: "level",
    title: "What is your experience level?",
    options: ["Beginner", "Intermediate", "Advanced"],
  },
  {
    key: "genre",
    title: "What do you want to play?",
    options: ["Rock", "Pop", "Blues", "Jazz", "Classical"],
  },
  {
    key: "category",
    title: "Which guitar type do you prefer?",
    options: ["Electric", "Acoustic", "Classical", "Bass"],
  },
];
const selectedOption =
  "rounded-2xl border p-5 text-left text-sm transition border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid";
const plainOption =
  "rounded-2xl border p-5 text-left text-sm transition border-zinc-200 hover:border-zinc-400 dark:border-white/10";

export function mountStore(page, app) {
  // State is scoped to this visit, matching the original screen's lifetime.
  let products = [];
  let saved = new Set();
  const storedCart = readCart();
  let cart = [];
  let filter = app.catalogCategory || "All";
  app.catalogCategory = "";
  let search = app.searchProduct || "";
  app.searchProduct = "";
  field(page, "search").value = search;
  let sort = "Featured";
  let cartPanel;
  let finder;
  let finderStep = 0;
  let results = [];
  let answers = {
    budget: 20000,
    level: "Beginner",
    genre: "Rock",
    category: "Electric",
  };
  let mobile;
  const cards = new Map();
  const timers = new Set();
  const soundTimers = new Map();
  let alive = true;

  const account = $(page, '[data-action="account"]');
  account.setAttribute("aria-label", app.user ? "Open account" : "Sign in");

  function renderProducts() {
    let list = products.filter(
      (p) =>
        (filter === "All" || p.category === filter) &&
        `${p.name} ${p.brand}`.toLowerCase().includes(search.toLowerCase()),
    );
    if (sort === "Price: low")
      list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "Price: high")
      list = [...list].sort((a, b) => b.price - a.price);
    if (sort === "Rating") list = [...list].sort((a, b) => b.rating - a.rating);
    const grid = field(page, "products");
    const activeIds = new Set(list.map((p) => p.id));
    for (const [id, card] of cards)
      if (!activeIds.has(id)) {
        card.remove();
        cards.delete(id);
      }
    const nextCards = list.map((product, index) => {
      let card = cards.get(product.id);
      const fresh = !card;
      if (fresh) {
        card = clone("product-card");
        cards.set(product.id, card);
        const motion = JSON.parse(card.dataset.motion);
        motion.transition.delay = index * 0.05;
        card.dataset.motion = JSON.stringify(motion);
      }
      card.dataset.productId = product.id;
      const image = field(card, "image");
      image.src = imageSource(product.image);
      image.alt = product.name;
      text(card, "badge", product.badge);
      text(card, "category", `${product.brand} · ${product.category}`);
      text(card, "rating", `${product.rating} (${product.reviews})`);
      text(card, "name", product.name);
      text(card, "description", product.description);
      text(card, "price", peso(product.price));
      text(
        card,
        "stock",
        product.stock ? `${product.stock} available` : "Out of stock",
      );
      const add = $(card, '[data-action="add"]');
      add.disabled = product.stock < 1;
      const heart = $(card, '[data-action="like"] svg');
      heart.setAttribute(
        "fill",
        saved.has(product.id) ? "currentColor" : "none",
      );
      heart.classList.toggle("text-rose-500", saved.has(product.id));
      $(card, '[data-action="add"]').setAttribute(
        "aria-label",
        `Add ${product.name} to cart`,
      );
      return { card, fresh };
    });
    grid.replaceChildren(...nextCards.map((item) => item.card));
    nextCards
      .filter((item) => item.fresh)
      .forEach((item) => animate(item.card));
    field(page, "no-products").hidden = list.length > 0;
    $$(page, ".filter-chip").forEach((button) =>
      button.classList.toggle(
        "filter-chip-active",
        button.dataset.category === filter,
      ),
    );
  }

  function renderCart() {
    writeCart(cart);
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const button = $(page, '[data-action="cart"]');
    let badge = $(button, "span");
    if (count && !badge) {
      badge = clone("cart-badge");
      button.append(badge);
    }
    if (badge) {
      badge.textContent = count;
      badge.hidden = count === 0;
    }
    if (!cartPanel) return;
    text(cartPanel, "cart-count", `${count} items`);
    const body = field(cartPanel, "cart-body");
    if (!cart.length) body.replaceChildren(clone("cart-empty"));
    else {
      const rows = clone("cart-items");
      rows.replaceChildren(
        ...cart.map((item) => {
          const row = clone("cart-item");
          row.dataset.productId = item.id;
          field(row, "image").src = imageSource(item.image);
          text(row, "brand", item.brand);
          text(row, "name", item.name);
          text(row, "price", peso(item.price));
          text(row, "quantity", item.qty);
          return row;
        }),
      );
      body.replaceChildren(rows);
    }
    field(cartPanel, "cart-footer").hidden = cart.length === 0;
    text(
      cartPanel,
      "subtotal",
      peso(cart.reduce((sum, item) => sum + item.price * item.qty, 0)),
    );
  }
  function openCart() {
    if (!cartPanel) {
      cartPanel = clone("cart");
      page.append(cartPanel);
      animate(cartPanel);
    }
    renderCart();
  }
  function addToCart(product) {
    if (!product || product.stock < 1)
      return notice("This item is currently out of stock.");
    if (
      (cart.find((item) => item.id === product.id)?.qty || 0) >= product.stock
    )
      return notice("You have reached the available stock for this item.");
    cart = cart.some((item) => item.id === product.id)
      ? cart.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + 1 } : item,
        )
      : [...cart, { ...product, qty: 1 }];
    openCart();
  }
  function changeQuantity(id, delta) {
    const item = cart.find((item) => item.id === id);
    if (delta > 0 && item && item.qty >= item.stock)
      return notice("You have reached the available stock for this item.");
    cart = cart
      .map((item) =>
        item.id === id ? { ...item, qty: Math.max(0, item.qty + delta) } : item,
      )
      .filter((item) => item.qty > 0);
    renderCart();
  }
  function closeCart() {
    const closing = cartPanel;
    cartPanel = null;
    dismiss(closing, "cart");
  }

  function renderFinder() {
    if (!finder) return;
    const modal = $(finder, ".finder-modal");
    modal.children[1]?.remove();
    if (finderStep === 4) {
      const body = clone("finder-results");
      field(body, "matches").replaceChildren(
        ...results.map((product, index) => {
          const row = clone("finder-match");
          row.dataset.productId = product.id;
          field(row, "image").src = imageSource(product.image);
          text(row, "rank", index + 1);
          text(row, "name", product.name);
          text(row, "category", `${product.category} · ${product.level}`);
          text(row, "price", peso(product.price));
          return row;
        }),
      );
      modal.append(body);
    } else {
      const body = field(clone("finder"), "finder-body");
      const question = questions[finderStep];
      text(body, "question-number", `Question ${finderStep + 1} of 4`);
      text(body, "question-title", question.title);
      [...field(body, "progress").children].forEach((bar, i) => {
        bar.className = `h-1 flex-1 rounded-full ${i <= finderStep ? "bg-zinc-950 dark:bg-acid" : "bg-zinc-200 dark:bg-white/10"}`;
      });
      field(body, "budget").hidden = finderStep !== 0;
      text(body, "budget-value", peso(answers.budget));
      field(body, "budget-input").value = answers.budget;
      const options = field(body, "options");
      options.hidden = finderStep === 0;
      options.replaceChildren(
        ...(question.options || []).map((option) => {
          const button = clone("finder-option");
          button.dataset.option = option;
          button.textContent = option;
          const selected = answers[question.key] === option;
          button.className = selected ? selectedOption : plainOption;
          if (selected) button.append(clone("check"));
          return button;
        }),
      );
      $(body, '[data-action="finder-next"]').replaceChildren(
        finderStep === 3 ? "Show my matches " : "Continue ",
        icon("arrow-right", 16),
      );
      modal.append(body);
    }
  }
  function openFinder() {
    closeMobile();
    if (finder) return;
    finder = clone("finder");
    page.append(finder);
    renderFinder();
    animate(finder);
  }
  function closeFinder() {
    const closing = finder;
    finder = null;
    finderStep = 0;
    results = [];
    dismiss(closing);
  }
  async function finishFinder() {
    const button = $(finder, '[data-action="finder-next"]');
    if (button.disabled) return;
    button.disabled = true;
    try {
      const data = await api("/finder", { method: "POST", body: answers });
      results = data.recommendations;
      finderStep = 4;
      if (alive) renderFinder();
    } catch (error) {
      notice(error.message);
      button.disabled = false;
    }
  }

  function openCheckout() {
    if (!app.user) {
      notice("Sign in to place your order. Your cart is saved.");
      app.navigate("auth");
      return;
    }
    if (!cart.length) return;
    const panel = dialog("Your next chapter starts here.", "checkout");
    const form = panel.querySelector("form");
    form.elements.address.value = app.user.address || "";
    form.elements.phone.value = app.user.phone || "";
    field(form, "checkout-total").textContent = peso(
      cart.reduce((sum, item) => sum + item.price * item.qty, 0),
    );
    const requestKey = crypto.randomUUID();
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      busy(form, true);
      formError(form, "");
      try {
        const data = await api("/orders", {
          method: "POST",
          body: {
            request_key: requestKey,
            address: form.elements.address.value,
            phone: form.elements.phone.value,
            items: cart.map((item) => ({
              product_id: item.id,
              quantity: item.qty,
            })),
          },
        });
        for (const item of cart) {
          const product = products.find((p) => p.id === item.id);
          if (product) product.stock -= item.qty;
        }
        cart = [];
        renderCart();
        renderProducts();
        panel.close();
        closeCart();
        orderDetails(data.order);
        notice("Your order has been placed.");
      } catch (error) {
        formError(form, error.message);
      } finally {
        busy(form, false, "Place order");
      }
    });
  }

  async function trackOrder() {
    if (!app.user) {
      notice("Sign in to track orders securely.");
      app.navigate("auth");
      return;
    }
    const id = field(page, "order").value.trim();
    if (!id) return notice("Enter your order number.");
    try {
      const data = await api(`/orders/${encodeURIComponent(id)}`);
      if (alive) orderDetails(data.order);
    } catch (error) {
      notice(error.message);
    }
  }

  function closeMobile() {
    if (mobile) {
      mobile.remove();
      mobile = null;
    }
    $(page, '[data-action="menu"]').replaceChildren(icon("menu", 19));
  }
  function toggleMobile() {
    if (mobile) return closeMobile();
    mobile = clone("mobile-nav");
    $(page, "header").append(mobile);
    animate(mobile);
    $(page, '[data-action="menu"]').replaceChildren(icon("x", 19));
  }
  function playSound(button) {
    function display(playing) {
      const label = $(button, "span");
      const glyph = icon(playing ? "pause" : "play", 15);
      glyph.setAttribute("fill", "currentColor");
      button.replaceChildren(glyph);
      if (label) {
        label.textContent = playing ? "Playing" : "Hear the tone";
        button.append(label);
      }
    }
    if (soundTimers.has(button)) {
      clearTimeout(soundTimers.get(button));
      soundTimers.delete(button);
      display(false);
      return;
    }
    display(true);
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      [164.81, 196, 246.94, 329.63].forEach((frequency, index) => {
        const oscillator = ctx.createOscillator();
        const gain = ctx.createGain();
        oscillator.type = "triangle";
        oscillator.frequency.value = frequency;
        gain.gain.setValueAtTime(0, ctx.currentTime + index * 0.18);
        gain.gain.linearRampToValueAtTime(
          0.055,
          ctx.currentTime + index * 0.18 + 0.03,
        );
        gain.gain.exponentialRampToValueAtTime(
          0.001,
          ctx.currentTime + index * 0.18 + 0.72,
        );
        oscillator.connect(gain).connect(ctx.destination);
        oscillator.start(ctx.currentTime + index * 0.18);
        oscillator.stop(ctx.currentTime + index * 0.18 + 0.75);
      });
      soundTimers.set(
        button,
        setTimeout(() => {
          soundTimers.delete(button);
          display(false);
          ctx.close();
        }, 1450),
      );
    } catch {
      display(false);
    }
  }

  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    if (!app.user) {
      app.navigate("auth");
      return;
    }
    if (button.tagName === "A") event.preventDefault();
    const id = Number(button.closest("[data-product-id]")?.dataset.productId);
    switch (button.dataset.action) {
      case "home":
        window.scrollTo({ top: 0, behavior: "smooth" });
        break;
      case "account": {
        const fromMobile = mobile?.contains(button);
        closeMobile();
        app.navigate(
          app.user?.role === "admin"
            ? "dashboard"
            : app.user
              ? "account"
              : "auth",
        );
        break;
      }
      case "admin-login":
        app.navigate("auth", "admin");
        break;
      case "menu":
        toggleMobile();
        break;
      case "mobile-link":
        closeMobile();
        break;
      case "finder":
        openFinder();
        break;
      case "close-finder":
        closeFinder();
        break;
      case "finder-next":
        if (finderStep === 3) finishFinder();
        else {
          finderStep += 1;
          renderFinder();
        }
        break;
      case "finder-option":
        answers = {
          ...answers,
          [questions[finderStep].key]: button.dataset.option,
        };
        renderFinder();
        break;
      case "finder-restart":
        finderStep = 0;
        renderFinder();
        break;
      case "add-match":
        addToCart(results.find((p) => p.id === id));
        closeFinder();
        break;
      case "search":
        $(page, "#shop").scrollIntoView({ behavior: "smooth" });
        timers.add(setTimeout(() => field(page, "search")?.focus(), 450));
        break;
      case "category":
        filter = button.dataset.category;
        renderProducts();
        $(page, "#shop").scrollIntoView({ behavior: "smooth" });
        break;
      case "filter":
        filter = button.dataset.category;
        renderProducts();
        break;
      case "add":
        addToCart(products.find((p) => p.id === id));
        break;
      case "cart":
        openCart();
        break;
      case "checkout":
        openCheckout();
        break;
      case "bundle": {
        const product = products.find((p) => p.category === "Bundles");
        if (product) {
          const panel = dialog(product.name, "bundle-detail");
          field(panel, "description").textContent = product.description;
          field(panel, "price").textContent = peso(product.price);
          field(panel, "image").src = imageSource(product.image);
          field(panel, "image").alt = product.name;
          field(panel, "bundle-add").addEventListener("click", () => {
            panel.close();
            addToCart(product);
          });
        } else
          notice(
            "This bundle is not currently available. Please contact the store.",
          );
        break;
      }
      case "support-info": {
        const panel = dialog(button.textContent.trim(), "support-info");
        const topic = button.dataset.topic;
        const descriptions = {
          delivery:
            "Delivery details are confirmed with your order. For a return, contact the store with your order number before sending an item back.",
          warranty:
            "Warranty coverage depends on the instrument and manufacturer. Contact the store with your order number and a description of the issue.",
          setup:
            "Every instrument benefits from a setup matched to your playing style. Ask the store about action, string gauge, and setup availability.",
        };
        field(panel, "support-copy").textContent =
          descriptions[topic] ||
          "Ask AUDI for guitar guidance or contact the store about an existing order.";
        api("/store")
          .then((data) => {
            if (panel.isConnected) {
              const link = field(panel, "support-email");
              link.textContent = data.store.support_email;
              link.href = `mailto:${data.store.support_email}`;
            }
          })
          .catch((error) => notice(error.message));
        break;
      }
      case "close-cart":
        closeCart();
        break;
      case "increase":
        changeQuantity(id, 1);
        break;
      case "decrease":
        changeQuantity(id, -1);
        break;
      case "like": {
        if (!app.user) {
          notice("Sign in to save instruments.");
          app.navigate("auth");
          break;
        }
        button.disabled = true;
        try {
          const data = await api(`/account/saved/${id}`, {
            method: saved.has(id) ? "DELETE" : "PUT",
          });
          if (data.saved) saved.add(id);
          else saved.delete(id);
          if (alive) renderProducts();
        } catch (error) {
          notice(error.message);
        } finally {
          button.disabled = false;
        }
        break;
      }
      case "sound":
        playSound(button);
        break;
      case "track":
        trackOrder();
        break;
    }
  });
  page.addEventListener("input", (event) => {
    switch (event.target.dataset.field) {
      case "search":
        search = event.target.value;
        renderProducts();
        break;

      case "budget-input":
        answers = { ...answers, budget: Number(event.target.value) };
        text(finder, "budget-value", peso(answers.budget));
        break;
    }
  });
  page.addEventListener("change", (event) => {
    if (event.target.dataset.field === "sort") {
      sort = event.target.value;
      renderProducts();
    }
  });
  field(page, "no-products").hidden = false;
  field(page, "no-products").textContent = "Loading instruments…";
  api("/products")
    .then((data) => {
      if (!alive) return;
      products = data.products;
      $$(page, "[data-category-count]").forEach((node) => {
        node.textContent = products.filter(
          (product) => product.category === node.dataset.categoryCount,
        ).length;
      });
      cart = storedCart
        .map((item) => {
          const product = products.find((p) => p.id === item.id);
          return product ? { ...product, qty: item.qty } : null;
        })
        .filter(Boolean);
      field(page, "no-products").textContent = "No guitar matches that search.";
      renderProducts();
      renderCart();
      if (app.openFinder) {
        app.openFinder = false;
        openFinder();
      }
      if (search || filter !== "All") $(page, "#shop").scrollIntoView();
    })
    .catch((error) => {
      if (alive) {
        field(page, "no-products").hidden = false;
        field(page, "no-products").textContent = error.message;
      }
    });
  if (app.user)
    api("/account/saved")
      .then((data) => {
        if (alive) {
          saved = new Set(data.products.map((p) => p.id));
          if (data.profile) answers = data.profile;
          renderProducts();
        }
      })
      .catch((error) => notice(error.message));
  return {
    destroy() {
      alive = false;
      timers.forEach(clearTimeout);
    },
  };
}

```

## assets/js/chatbot/chatbot-ui.js

```javascript
// DOM behavior only: reuse the existing chat, message and suggestion templates.
import { clone, field, icon, animate } from "../shared/shared.js";

export function createChatUI(host) {
  const toggle = host.querySelector('[data-action="chat"]');
  let panel;
  let typing;

  function scrollToLatestMessage() {
    const messages = field(panel, "messages");
    messages.scrollTop = messages.scrollHeight;
  }

  function addMessage(message, role) {
    const bubble = clone("message");
    if (role === "user") {
      bubble.className =
        "max-w-[86%] rounded-2xl px-4 py-3 text-xs leading-5 ml-auto bg-zinc-950 text-white dark:bg-acid dark:text-ink";
    }
    // Both customer text and model responses are untrusted plain text.
    bubble.textContent = message;
    field(panel, "messages").append(bubble);
    scrollToLatestMessage();
    return bubble;
  }

  function toggleChat() {
    if (!panel) {
      panel = clone("chat");
      host.append(panel);
      field(panel, "messages").append(
        clone("message"),
        clone("chat-suggestions"),
      );
      animate(panel);
    } else {
      panel.hidden = !panel.hidden;
    }
    const open = !panel.hidden;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute(
      "aria-label",
      open ? "Close customer support" : "Open customer support",
    );
    toggle.replaceChildren(icon(open ? "x" : "message-circle", open ? 20 : 21));
    if (open) {
      scrollToLatestMessage();
      field(panel, "chat-input").focus();
    }
  }

  function setChatLoading(loading) {
    // Disable the form while the previous request is still running.
    field(panel, "chat-input").disabled = loading;
    panel.querySelector('button[type="submit"]').disabled = loading;
    panel
      .querySelectorAll('[data-action="chat-suggestion"]')
      .forEach((button) => {
        button.disabled = loading;
      });
    panel
      .querySelector('[data-form="chat"]')
      .setAttribute("aria-busy", String(loading));
    if (!loading && !panel.hidden) field(panel, "chat-input").focus();
  }

  return {
    toggleChat,
    readMessage: () => field(panel, "chat-input").value,
    clearInput: () => {
      field(panel, "chat-input").value = "";
    },
    addUserMessage(message) {
      panel
        .querySelector('[data-action="chat-suggestion"]')
        ?.parentElement.remove();
      addMessage(message, "user");
    },
    addAssistantMessage: (message) => addMessage(message, "assistant"),
    showError: (message) => addMessage(message, "assistant"),
    showTypingIndicator() {
      typing = addMessage("AUDI is typing…", "assistant");
      typing.setAttribute("role", "status");
    },
    hideTypingIndicator() {
      typing?.remove();
      typing = null;
    },
    setChatLoading,
  };
}

```

## assets/js/shared/app.js

```javascript
// Flask chooses the page. This file starts that page's interactive features.
import { initChatbot } from "../chatbot/chatbot.js";
import { mountStore } from "../catalog/storefront.js";
import { mountAuth } from "../auth/auth.js";
import { mountAdmin } from "../admin/admin.js";
import { mountAccount } from "../account/account.js";
import { $$, icon, animate, api, notice, writeCart } from "./shared.js";

const root = document.getElementById("root");
const page = root.firstElementChild;
const pageName = document.body.dataset.page;
let user = null;
let theme = localStorage.getItem("audia-theme") || "dark";

// Keep only small navigation preferences across normal page loads.
const app = {
  get user() {
    return user;
  },
  set user(value) {
    user = value;
  },
  get catalogCategory() {
    return sessionStorage.getItem("audia-category") || "";
  },
  set catalogCategory(value) {
    sessionStorage.setItem("audia-category", value);
  },
  get searchProduct() {
    return sessionStorage.getItem("audia-search") || "";
  },
  set searchProduct(value) {
    sessionStorage.setItem("audia-search", value);
  },
  get openFinder() {
    return sessionStorage.getItem("audia-finder") === "true";
  },
  set openFinder(value) {
    sessionStorage.setItem("audia-finder", String(value));
  },
  resetToken: document.body.dataset.resetToken || "",
  navigate(screen, role = "customer") {
    const pages = {
      landing: "/",
      storefront: "/shop",
      account: "/account",
      dashboard: "/admin",
    };
    let url = pages[screen] || "/login";
    if (screen === "auth" && role === "register") url = "/register";
    if (screen === "auth" && role === "admin") url = "/login?role=admin";
    window.location.assign(url);
  },
  login(account) {
    user = account;
    app.navigate(account.role === "admin" ? "dashboard" : "storefront");
  },
  async logout() {
    try {
      await api("/auth/logout", { method: "POST" });
      user = null;
      writeCart([]);
      app.navigate("landing");
    } catch (error) {
      notice(error.message);
    }
  },
};

function updateTheme() {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("audia-theme", theme);
  $$(root, '[data-action="theme"]').forEach((button) => {
    const label = `Switch to ${theme === "dark" ? "light" : "dark"} mode`;
    button.setAttribute("aria-label", label);
    button.title = label;
    button.replaceChildren(icon(theme === "dark" ? "sun" : "moon", 17));
  });
}
root.addEventListener("click", (event) => {
  if (event.target.closest('[data-action="theme"]')) {
    theme = theme === "dark" ? "light" : "dark";
    updateTheme();
  }
});
window.addEventListener("audia:unauthorized", () => {
  if (!user) return;
  user = null;
  writeCart([]);
  app.navigate("auth");
});

// Old bookmarks and emailed reset links remain usable after the route change.
function followOldBookmark() {
  const legacy = {
    "#storefront": "/shop",
    "#auth": "/login",
    "#account": "/account",
    "#dashboard": "/admin",
    "#landing": "/",
  };
  if (legacy[location.hash]) {
    location.replace(legacy[location.hash]);
    return true;
  }
  if (location.hash.startsWith("#reset/")) {
    location.replace(
      "/reset-password?token=" + encodeURIComponent(location.hash.slice(7)),
    );
    return true;
  }
  return false;
}
window.addEventListener("hashchange", followOldBookmark);

if (!followOldBookmark()) {
  try {
    user = (await api("/auth/session")).user;
  } catch (error) {
    notice(error.message);
  }

  if (["storefront", "account", "dashboard", "tuner", "lessons"].includes(pageName) && !user) {
    app.navigate("auth");
  } else {
    if (pageName === "storefront") mountStore(page, app);
    if (pageName === "auth")
      mountAuth(page, app, document.body.dataset.authMode);
    if (pageName === "account") mountAccount(page, app);
    if (pageName === "dashboard") mountAdmin(page, app);
    if (pageName === "tuner") (await import("../tuner/tuner.js")).mountTuner(page);
    if (pageName === "landing") {
      page.querySelectorAll("[data-auth-entry]").forEach((node) => {
        node.hidden = Boolean(user);
      });
      page.querySelectorAll("[data-member-entry]").forEach((node) => {
        node.hidden = !user;
      });
      page.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action]");
        if (!button) return;
        const action = button.dataset.action;
        if (action === "register") app.navigate("auth", "register");
        if (action === "sign-in") app.navigate("auth");
        if (action === "browse") {
          app.catalogCategory = button.dataset.category || "";
          app.navigate(user ? "storefront" : "auth");
        }
      });
    }
    initChatbot(page);
    updateTheme();
    animate(page);
    // Enable controls after their handlers and session have loaded.
    root.inert = false;
    root.removeAttribute("aria-busy");
  }
}

```

## assets/js/shared/shared.js

```javascript
// Shared browser helpers: DOM, API requests, images, cart storage and dialogs.

// DOM
// Native HTML template helpers. Content from API responses is always assigned as text.
export const $ = (root, selector) => root.querySelector(selector);
export const $$ = (root, selector) => [...root.querySelectorAll(selector)];
export const field = (root, name) => $(root, `[data-field="${name}"]`);
export function text(root, name, value) {
  field(root, name).textContent = value;
}
export function clone(name) {
  return document
    .getElementById(`${name}-template`)
    .content.firstElementChild.cloneNode(true);
}
export function icon(name, size = 17) {
  const svg = clone(`icon-${name}`);
  svg.setAttribute("width", size);
  svg.setAttribute("height", size);
  svg.setAttribute("class", `lucide lucide-${name}`);
  return svg;
}
export const peso = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value);

// Web Animations and IntersectionObserver replace the former motion dependency.
const revealObservers = new Map();
export function disposeAnimations(root) {
  for (const [node, observer] of revealObservers) {
    if (root.contains(node)) {
      observer.disconnect();
      revealObservers.delete(node);
    }
  }
}
function frame(values = {}) {
  const result = {};
  const transform = [];
  for (const [key, value] of Object.entries(values || {})) {
    if (key === "x" || key === "y")
      transform.push(
        `translate${key.toUpperCase()}(${typeof value === "number" ? `${value}px` : value})`,
      );
    else if (key === "scale") transform.push(`scale(${value})`);
    else
      result[key] =
        typeof value === "number" && ["width", "height"].includes(key)
          ? `${value}px`
          : value;
  }
  if (transform.length) result.transform = transform.join(" ");
  return result;
}
export function animate(root) {
  const nodes = [
    ...(root.matches?.("[data-motion]") ? [root] : []),
    ...$$(root, "[data-motion]"),
  ];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  for (const node of nodes) {
    const config = JSON.parse(node.dataset.motion);
    const start = frame(config.initial);
    const end = frame(config.animate);
    Object.assign(node.style, end);
    node.removeAttribute("data-motion");
    if (reduced) continue;
    const run = () => {
      if (!node.isConnected) return;
      node.animate([start, end], {
        duration: (config.transition?.duration || 0.4) * 1000,
        delay: (config.transition?.delay || 0) * 1000,
        easing: "cubic-bezier(.22, 1, .36, 1)",
        fill: "backwards",
      });
    };
    if (config.viewport) {
      Object.assign(node.style, start);
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries.some((entry) => entry.isIntersecting)) {
            Object.assign(node.style, end);
            run();
            observer.disconnect();
            revealObservers.delete(node);
          }
        },
        { threshold: 0.18 },
      );
      revealObservers.set(node, observer);
      observer.observe(node);
    } else run();
  }
}
export async function dismiss(node, type = "fade") {
  if (!node || node.dataset.closing) return;
  node.dataset.closing = "true";
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const panel = $(node, ".cart-panel, .finder-modal") || node;
    const end =
      type === "cart"
        ? { transform: "translateX(100%)" }
        : { opacity: 0, transform: "translateY(16px)" };
    await panel.animate([{}, end], {
      duration: 250,
      easing: "ease-in",
      fill: "forwards",
    }).finished;
  }
  node.remove();
}

// API
// Same-origin API client. Authentication failures never fall back to demo access.
let csrf = "";
export async function api(path, options = {}) {
  const headers = { ...options.headers };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.method && !["GET", "HEAD"].includes(options.method))
    headers["X-CSRF-Token"] = csrf;
  let response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers,
      credentials: "same-origin",
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new Error(
      "Unable to reach AUDIA. Check your connection and try again.",
    );
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/")) {
      window.dispatchEvent(new Event("audia:unauthorized"));
    }
    const error = new Error(
      data.error || "We could not complete that request. Please try again.",
    );
    error.status = response.status;
    throw error;
  }
  if (data.csrf_token) csrf = data.csrf_token;
  return data;
}

// MEDIA
// Product media may use local /static/images/ paths or HTTPS URLs.
export function imageSource(value) {
  return value;
}

document.addEventListener(
  "error",
  (event) => {
    const image = event.target;
    if (image instanceof HTMLImageElement && !image.dataset.fallback) {
      image.dataset.fallback = "true";
      image.alt =
        "Image unavailable; guitar studio photograph shown for illustration.";
      image.src = "/static/images/guitar_front.jpg";
    }
  },
  true,
);

// CART STORAGE
const key = "audia-cart";
export function readCart() {
  try {
    const value = JSON.parse(sessionStorage.getItem(key) || "[]");
    return Array.isArray(value)
      ? value
          .filter(
            (item) =>
              Number.isInteger(item.id) &&
              Number.isInteger(item.qty) &&
              item.qty > 0 &&
              item.qty <= 99,
          )
          .slice(0, 50)
      : [];
  } catch {
    return [];
  }
}
export function writeCart(items) {
  sessionStorage.setItem(
    key,
    JSON.stringify(items.map(({ id, qty }) => ({ id, qty }))),
  );
}

// UI
export function notice(message) {
  let node = document.getElementById("notice");
  if (!node) {
    node = document.createElement("div");
    node.id = "notice";
    node.className = "notice";
    node.setAttribute("role", "status");
    document.body.append(node);
  }
  node.textContent = message;
  node.hidden = false;
  clearTimeout(notice.timer);
  notice.timer = setTimeout(() => {
    node.hidden = true;
  }, 6500);
}

export function dialog(title, template) {
  const node = clone("dialog");
  const titleId = `dialog-title-${crypto.randomUUID()}`;
  field(node, "dialog-title").id = titleId;
  node.setAttribute("aria-labelledby", titleId);
  field(node, "dialog-title").textContent = title;
  if (template) field(node, "dialog-body").append(clone(template));
  document.body.append(node);
  node.addEventListener("click", (event) => {
    if (
      event.target === node ||
      event.target.closest('[data-action="dialog-close"]')
    )
      node.close();
  });
  node.addEventListener("close", () => node.remove(), { once: true });
  const close = node.close.bind(node);
  node.close = () => {
    close();
    node.remove();
  };
  node.showModal();
  return node;
}

export function formError(form, message) {
  const error = field(form, "form-error");
  error.textContent = message;
  error.hidden = !message;
}

export function busy(form, pending, label = "Save changes") {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = pending;
  button.textContent = pending ? "Please wait…" : label;
}

export function empty(node, message) {
  const text = document.createElement("p");
  text.className = "empty-state";
  text.textContent = message;
  node.replaceChildren(text);
}

export function orderDetails(order) {
  const panel = dialog(`Order ${order.id}`, "order-detail");
  for (const key of [
    "status",
    "customer",
    "address",
    "phone",
    "payment",
    "date",
  ]) {
    field(panel, key).textContent = order[key];
  }
  field(panel, "total").textContent = new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(order.amount);
  for (const item of order.items) {
    const row = document.createElement("li");
    row.textContent = `${item.name} × ${item.quantity}`;
    field(panel, "items").append(row);
  }
  return panel;
}

```

## assets/js/shared/theme.js

```javascript
// Apply the saved theme before the first paint, as on the original storefront.
document.documentElement.classList.toggle(
  "dark",
  (localStorage.getItem("audia-theme") || "dark") === "dark",
);

```

## assets/js/tuner/pitch.js

```javascript
// Pure pitch calculations, separate from microphone controls and page rendering.
// YIN: de Cheveigné & Kawahara (2002), doi:10.1121/1.1458024.
const NOTE_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];

export function detectPitch(input, sampleRate) {
  if (!input.length || !Number.isFinite(sampleRate) || sampleRate <= 0) return null;
  let mean = 0;
  for (const value of input) mean += value;
  mean /= input.length;
  let energy = 0;
  for (const value of input) energy += (value - mean) ** 2;
  if (Math.sqrt(energy / input.length) < 0.008) return null;

  // Average groups of samples to reduce work while preserving guitar pitches.
  const step = Math.max(1, Math.floor(sampleRate / 12000));
  const rate = sampleRate / step;
  const samples = new Float32Array(Math.floor(input.length / step));
  for (let index = 0; index < samples.length; index++) {
    let sum = 0;
    for (let offset = 0; offset < step; offset++) sum += input[index * step + offset] - mean;
    samples[index] = sum / step;
  }
  const minLag = Math.floor(rate / 420);
  const maxLag = Math.ceil(rate / 65);
  const windowSize = samples.length - maxLag - 1;
  if (windowSize < maxLag) return null;
  const difference = new Float32Array(maxLag + 1);
  difference[0] = 1;
  let runningSum = 0;
  for (let lag = 1; lag <= maxLag; lag++) {
    let sum = 0;
    for (let index = 0; index < windowSize; index++) {
      const delta = samples[index] - samples[index + lag];
      sum += delta * delta;
    }
    runningSum += sum;
    // Cumulative mean normalized difference rejects nonperiodic input.
    difference[lag] = runningSum ? (sum * lag) / runningSum : 1;
  }
  let lag = minLag;
  while (lag < maxLag && difference[lag] >= 0.15) lag++;
  if (lag >= maxLag) return null;
  while (lag + 1 <= maxLag && difference[lag + 1] < difference[lag]) lag++;
  if (lag >= maxLag) return null;
  const left = difference[lag - 1];
  const center = difference[lag];
  const right = difference[lag + 1];
  const denominator = left - 2 * center + right;
  const refinedLag = lag + (denominator ? (left - right) / (2 * denominator) : 0);
  const frequency = rate / refinedLag;
  if (!Number.isFinite(frequency) || frequency < 65 || frequency > 420) return null;
  return { frequency, confidence: 1 - center };
}

export function describePitch(frequency) {
  const midi = Math.round(69 + 12 * Math.log2(frequency / 440));
  const target = 440 * 2 ** ((midi - 69) / 12);
  const cents = 1200 * Math.log2(frequency / target);
  const note = NOTE_NAMES[((midi % 12) + 12) % 12];
  const octave = Math.floor(midi / 12) - 1;
  const magnitude = Math.abs(cents);
  const status = magnitude <= 5 ? "In Tune"
    : cents < 0 ? (magnitude <= 15 ? "Slightly Flat" : "Too Flat")
    : magnitude <= 15 ? "Slightly Sharp" : "Too Sharp";
  return { note, octave, frequency, cents, status,
    tuning: magnitude <= 5 ? "in-tune" : cents < 0 ? "flat" : "sharp" };
}

export class PitchStabilizer {
  constructor() { this.reset(); }
  reset() { this.readings = []; this.smoothed = null; }
  push(frequency) {
    const semitones = 69 + 12 * Math.log2(frequency / 440);
    if (this.readings.length && Math.abs(semitones - this.readings.at(-1)) > 0.35) {
      this.readings = [];
    }
    this.readings.push(semitones);
    if (this.readings.length > 5) this.readings.shift();
    if (this.readings.length < 3) return null;
    const sorted = [...this.readings].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    this.smoothed = this.smoothed === null || Math.abs(median - this.smoothed) > 0.5
      ? median : this.smoothed * 0.6 + median * 0.4;
    return 440 * 2 ** ((this.smoothed - 69) / 12);
  }
}

```

## assets/js/tuner/tuner.js

```javascript
// Microphone lifecycle and UI for the tuner only. No recordings or audio uploads.
import { detectPitch, describePitch, PitchStabilizer } from "./pitch.js";

export function mountTuner(page) {
  const find = (id) => page.querySelector(`#tuner-${id}`);
  const startButton = find("start");
  const stopButton = find("stop");
  const container = page.querySelector(".tuner-container");
  const stabilizer = new PitchStabilizer();
  let stream = null;
  let context = null;
  let source = null;
  let analyser = null;
  let frame = null;
  let generation = 0;
  let active = false;
  let pending = false;
  let lastRead = 0;
  let lastReliable = 0;

  function clearPitch() {
    find("note").textContent = "—";
    find("octave").textContent = "";
    find("frequency").textContent = "— Hz";
    find("cents").textContent = "— cents";
    find("status").textContent = "Play a string";
    find("indicator").hidden = true;
    find("meter").setAttribute("aria-valuenow", "0");
    find("meter").setAttribute("aria-valuetext", "No reliable pitch");
    delete container.dataset.tuning;
    page.querySelectorAll("[data-tuning-note]").forEach((node) => delete node.dataset.active);
  }

  function showError(state, message) {
    find("microphone").textContent = state;
    find("error").textContent = message;
    find("error").hidden = false;
  }

  function stopTuner() {
    generation++;
    active = false;
    pending = false;
    cancelAnimationFrame(frame);
    frame = null;
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (source) source.disconnect();
    if (analyser) analyser.disconnect();
    if (context) {
      context.onstatechange = null;
      if (context.state !== "closed") void context.close().catch(() => {});
    }
    stream = context = source = analyser = null;
    stabilizer.reset();
    clearPitch();
    find("microphone").textContent = "Microphone inactive";
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  function renderPitch(frequency) {
    const pitch = describePitch(frequency);
    find("note").textContent = pitch.note;
    find("octave").textContent = pitch.octave;
    find("frequency").textContent = `${pitch.frequency.toFixed(1)} Hz`;
    const rounded = Math.round(pitch.cents);
    find("cents").textContent = `${rounded > 0 ? "+" : ""}${rounded === 0 ? 0 : rounded} cents`;
    find("status").textContent = pitch.status;
    container.dataset.tuning = pitch.tuning;
    const cents = Math.max(-50, Math.min(50, pitch.cents));
    find("indicator").hidden = false;
    find("indicator").style.left = `${50 + cents}%`;
    find("meter").setAttribute("aria-valuenow", cents.toFixed(1));
    find("meter").setAttribute("aria-valuetext", `${pitch.note}${pitch.octave}, ${rounded} cents, ${pitch.status}`);
    page.querySelectorAll("[data-tuning-note]").forEach((node) => {
      node.toggleAttribute("data-active", node.dataset.tuningNote === `${pitch.note}${pitch.octave}`);
    });
  }

  async function startTuner() {
    if (active || pending) return;
    find("error").hidden = true;
    if (!window.isSecureContext) {
      showError("Microphone unavailable", "Microphone access requires HTTPS or localhost. Open AUDIA using a secure address.");
      return;
    }
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!navigator.mediaDevices?.getUserMedia || !AudioContextClass) {
      showError("Microphone unavailable", "Your browser does not support the audio features required by the tuner.");
      return;
    }
    const ticket = ++generation;
    pending = true;
    startButton.disabled = true;
    stopButton.disabled = false;
    find("microphone").textContent = "Requesting microphone";
    try {
      // Resume directly from the button gesture, including on mobile browsers.
      const audioContext = new AudioContextClass();
      context = audioContext;
      await audioContext.resume();
      if (ticket !== generation) return;
      const microphone = await navigator.mediaDevices.getUserMedia({ audio: {
        echoCancellation: false, noiseSuppression: false, autoGainControl: false,
      } });
      // Stop may be pressed while the browser's permission prompt is still open.
      if (ticket !== generation) {
        microphone.getTracks().forEach((track) => track.stop());
        return;
      }
      stream = microphone;
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 4096;
      source = audioContext.createMediaStreamSource(microphone);
      source.connect(analyser);
      // No connection to destination: the microphone never plays through speakers.
      const samples = new Float32Array(analyser.fftSize);
      active = true;
      pending = false;
      lastRead = 0;
      lastReliable = performance.now();
      find("microphone").textContent = "Listening";
      microphone.getTracks().forEach((track) => track.addEventListener("ended", () => {
        if (ticket !== generation) return;
        stopTuner();
        showError("Microphone unavailable", "The microphone was disconnected. Reconnect it and start the tuner again.");
      }, { once: true }));
      audioContext.onstatechange = () => {
        if (!active || ticket !== generation || audioContext.state === "running") return;
        stopTuner();
        showError("Microphone inactive", "Audio was interrupted. Press Start Tuner to listen again.");
      };

      function listen(now) {
        if (!active || ticket !== generation) return;
        // About twelve estimates per second keeps processing light on phones.
        if (now - lastRead >= 80) {
          lastRead = now;
          try {
            analyser.getFloatTimeDomainData(samples);
            const pitch = detectPitch(samples, audioContext.sampleRate);
            const frequency = pitch ? stabilizer.push(pitch.frequency) : null;
            if (frequency) { renderPitch(frequency); lastReliable = now; }
            if (now - lastReliable > 650) {
              stabilizer.reset();
              clearPitch();
              lastReliable = now;
            }
          } catch {
            stopTuner();
            showError("Microphone unavailable", "Audio could not be processed. Stop other audio apps and try again.");
            return;
          }
        }
        frame = requestAnimationFrame(listen);
      }
      frame = requestAnimationFrame(listen);
    } catch (error) {
      if (ticket !== generation) return;
      stopTuner();
      if (["NotAllowedError", "PermissionDeniedError", "SecurityError"].includes(error.name)) {
        showError("Permission denied", "Microphone access is required to use the guitar tuner. Please allow microphone access in your browser settings.");
      } else if (["NotFoundError", "DevicesNotFoundError"].includes(error.name)) {
        showError("Microphone unavailable", "No microphone was detected on this device.");
      } else {
        showError("Microphone unavailable", "The microphone could not be started. It may be in use by another app. Close it and try again.");
      }
    }
  }

  startButton.addEventListener("click", startTuner);
  stopButton.addEventListener("click", () => { stopTuner(); find("error").hidden = true; });
  window.addEventListener("pagehide", stopTuner);
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopTuner(); });
}

```

## docs/architecture/after.json

```json
{
  "routes": [
    {
      "endpoint": "account_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/account"
    },
    {
      "endpoint": "admin.add_product",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/admin/products"
    },
    {
      "endpoint": "admin.archive_product",
      "methods": [
        "DELETE",
        "OPTIONS"
      ],
      "rule": "/api/admin/products/<int:product_id>"
    },
    {
      "endpoint": "admin.customers",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/customers"
    },
    {
      "endpoint": "admin.edit_product",
      "methods": [
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/admin/products/<int:product_id>"
    },
    {
      "endpoint": "admin.export_sales",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/sales/export"
    },
    {
      "endpoint": "admin.products",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/products"
    },
    {
      "endpoint": "admin.sales",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/sales"
    },
    {
      "endpoint": "admin.settings",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/admin/settings"
    },
    {
      "endpoint": "admin.summary",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/summary"
    },
    {
      "endpoint": "admin.update_order",
      "methods": [
        "OPTIONS",
        "PATCH"
      ],
      "rule": "/api/admin/sales/<order_id>"
    },
    {
      "endpoint": "auth.change_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/password"
    },
    {
      "endpoint": "auth.current_session",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/auth/session"
    },
    {
      "endpoint": "auth.forgot_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/forgot-password"
    },
    {
      "endpoint": "auth.login",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/login"
    },
    {
      "endpoint": "auth.logout",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/logout"
    },
    {
      "endpoint": "auth.profile",
      "methods": [
        "OPTIONS",
        "PATCH"
      ],
      "rule": "/api/auth/profile"
    },
    {
      "endpoint": "auth.register",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/register"
    },
    {
      "endpoint": "auth.reset_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/reset-password"
    },
    {
      "endpoint": "catalog.finder",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/finder"
    },
    {
      "endpoint": "catalog.product",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/products/<int:product_id>"
    },
    {
      "endpoint": "catalog.products",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/products"
    },
    {
      "endpoint": "catalog.save",
      "methods": [
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/account/saved/<int:product_id>"
    },
    {
      "endpoint": "catalog.saved",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/account/saved"
    },
    {
      "endpoint": "catalog.store_info",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/store"
    },
    {
      "endpoint": "catalog.unsave",
      "methods": [
        "DELETE",
        "OPTIONS"
      ],
      "rule": "/api/account/saved/<int:product_id>"
    },
    {
      "endpoint": "chatbot.chat",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/chat"
    },
    {
      "endpoint": "chatbot.chat_status",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/chat"
    },
    {
      "endpoint": "dashboard",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/admin"
    },
    {
      "endpoint": "health",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/health"
    },
    {
      "endpoint": "index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/"
    },
    {
      "endpoint": "lessons.chord_detail",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/chords/<slug>"
    },
    {
      "endpoint": "lessons.chords",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/chords"
    },
    {
      "endpoint": "lessons.getting_started",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/getting-started"
    },
    {
      "endpoint": "lessons.index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons"
    },
    {
      "endpoint": "lessons.strumming",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/strumming"
    },
    {
      "endpoint": "login_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/login"
    },
    {
      "endpoint": "orders.checkout",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/orders"
    },
    {
      "endpoint": "orders.detail",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/orders/<order_id>"
    },
    {
      "endpoint": "orders.history",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/orders"
    },
    {
      "endpoint": "register_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/register"
    },
    {
      "endpoint": "reset_password_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/reset-password"
    },
    {
      "endpoint": "shop",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/shop"
    },
    {
      "endpoint": "static",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/static/<path:filename>"
    },
    {
      "endpoint": "tuner.index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/tuner"
    }
  ],
  "blueprints": [
    "auth",
    "catalog",
    "orders",
    "admin",
    "chatbot",
    "tuner",
    "lessons"
  ],
  "migration": {
    "modules/auth.py": "modules/auth/routes.py",
    "modules/mail.py": "modules/auth/mail.py",
    "modules/catalog.py": "modules/catalog/routes.py",
    "modules/orders.py": "modules/orders/routes.py",
    "modules/admin.py": "modules/admin/routes.py",
    "modules/chatbot.py": "modules/chatbot/routes.py",
    "modules/ai.py": "modules/ai/services.py",
    "modules/rag_sync.py": "modules/ai/rag_sync.py",
    "modules/tuner.py": "modules/tuner/routes.py",
    "modules/lessons.py": "modules/lessons/routes.py",
    "modules/lessons_content.py": "modules/lessons/data.py",
    "modules/database.py": "modules/database/connection.py",
    "modules/models.py": "modules/database/models.py",
    "templates/base.html": "templates/shared/base.html",
    "templates/shared.html": "templates/shared/components.html",
    "templates/practice/base.html": "templates/shared/practice_base.html",
    "templates/practice/feature_links.html": "templates/shared/practice_links.html",
    "templates/auth.html": "templates/auth/auth.html",
    "templates/storefront.html": "templates/catalog/storefront.html",
    "templates/account.html": "templates/account/account.html",
    "templates/admin.html": "templates/admin/admin.html",
    "templates/chatbot.html": "templates/chatbot/chatbot.html",
    "templates/landing.html": "templates/landing/landing.html",
    "assets/css/auth.css": "assets/css/auth/auth.css",
    "assets/css/storefront.css": "assets/css/catalog/storefront.css",
    "assets/css/account.css": "assets/css/account/account.css",
    "assets/css/admin.css": "assets/css/admin/admin.css",
    "assets/css/landing.css": "assets/css/landing/landing.css",
    "assets/css/tuner.css": "assets/css/tuner/tuner.css",
    "assets/css/lessons.css": "assets/css/lessons/lessons.css",
    "assets/css/shared.css": "assets/css/shared/shared.css",
    "assets/css/practice.css": "assets/css/shared/practice.css",
    "assets/js/auth.js": "assets/js/auth/auth.js",
    "assets/js/storefront.js": "assets/js/catalog/storefront.js",
    "assets/js/account.js": "assets/js/account/account.js",
    "assets/js/admin.js": "assets/js/admin/admin.js",
    "assets/js/tuner.js": "assets/js/tuner/tuner.js",
    "assets/js/tuner-pitch.js": "assets/js/tuner/pitch.js",
    "assets/js/app.js": "assets/js/shared/app.js",
    "assets/js/shared.js": "assets/js/shared/shared.js",
    "assets/js/theme.js": "assets/js/shared/theme.js",
    "docs/guitar-practice-source.md": "docs/archive/guitar-practice-source.md"
  },
  "modified_existing_files": [
    {
      "original": "modules/admin.py",
      "current": "modules/admin/routes.py",
      "sha256": "104c8331cee6cbec533280ab3a55d3c691abbcbc85b81439e71284b1f140ab7e",
      "bytes": 8719
    },
    {
      "original": "modules/ai.py",
      "current": "modules/ai/services.py",
      "sha256": "62296f9b9d6e1fcdadef87e4051f4731a8bb8da39ae9b3bce395410b5272e581",
      "bytes": 28170
    },
    {
      "original": "modules/auth.py",
      "current": "modules/auth/routes.py",
      "sha256": "75e7e4811eb4723ef0fd970f4702b379666a57732790c46fb7f718ca1ac0c579",
      "bytes": 19974
    },
    {
      "original": "modules/catalog.py",
      "current": "modules/catalog/routes.py",
      "sha256": "4b6f35e2ca918fa65344346c8400c4dcd5699646f4ed646bbe1eb019a817a073",
      "bytes": 4168
    },
    {
      "original": "modules/lessons.py",
      "current": "modules/lessons/routes.py",
      "sha256": "7f293bf9d0745efa47c39d0593f7bc67a6f18239e0abb6a0735f01bf7eca06f9",
      "bytes": 1265
    },
    {
      "original": "modules/orders.py",
      "current": "modules/orders/routes.py",
      "sha256": "4c53393f276d257c98ef5ebe95f77d939324490d34edf1cbe3ce93036728414d",
      "bytes": 3127
    },
    {
      "original": "modules/rag_sync.py",
      "current": "modules/ai/rag_sync.py",
      "sha256": "7a949b2febf89fb84bbd805736f621575708aefde98931c3ce80f0b892880cb7",
      "bytes": 4326
    },
    {
      "original": "modules/tuner.py",
      "current": "modules/tuner/routes.py",
      "sha256": "ae7e0e6c201c0b41ec0852c49eaefb116d48c802263a4d973716ff1e0225fde6",
      "bytes": 516
    },
    {
      "original": "templates/account.html",
      "current": "templates/account/account.html",
      "sha256": "8bbda1f61eddac4fb48ce9a6e25fa27f35c49f25fb74ff9daefb0557bdd1ec90",
      "bytes": 5388
    },
    {
      "original": "templates/admin.html",
      "current": "templates/admin/admin.html",
      "sha256": "aaece62785853e0ffed63697a4ede53234fded743d0344761dba97a1d3cf39b6",
      "bytes": 32908
    },
    {
      "original": "templates/auth.html",
      "current": "templates/auth/auth.html",
      "sha256": "4cc790e4aeefa9782d4fc22a4b4d3f07ccb80fe2e5eb4c68092d90578b7442df",
      "bytes": 14449
    },
    {
      "original": "templates/base.html",
      "current": "templates/shared/base.html",
      "sha256": "1d31d02385d0f0510bf4c73342af40985bf555951195e4af5cdacb9996468555",
      "bytes": 1251
    },
    {
      "original": "templates/landing.html",
      "current": "templates/landing/landing.html",
      "sha256": "5af937a0d5a2bf09efd0dc0346df86fd50c712af85746513f4b387f8daeed889",
      "bytes": 8243
    },
    {
      "original": "templates/lessons/chord_detail.html",
      "current": "templates/lessons/chord_detail.html",
      "sha256": "3cbe8053c73b43960fc34e98e9d0eacb92852cd6ffa8d8dce2fa05fc1c739397",
      "bytes": 1415
    },
    {
      "original": "templates/lessons/chords.html",
      "current": "templates/lessons/chords.html",
      "sha256": "fac422659f8884470976435d4e8894613cc52ab7ded9a0d3b282a1f770d0d5a0",
      "bytes": 1004
    },
    {
      "original": "templates/lessons/getting_started.html",
      "current": "templates/lessons/getting_started.html",
      "sha256": "0ac3188e9ecbd8914c53cb115ac399e5eb0bc54b78c23af28b711d0f8d1ba15f",
      "bytes": 3859
    },
    {
      "original": "templates/lessons/index.html",
      "current": "templates/lessons/index.html",
      "sha256": "29e47f74c12a7e3fc84be9b12c4e2e017d682b25984d165e72ae1d6c4bc094be",
      "bytes": 1961
    },
    {
      "original": "templates/lessons/strumming.html",
      "current": "templates/lessons/strumming.html",
      "sha256": "1b5512f006c62feca4df36365bdfbe7d230d5412f8d9cffac76704938a040314",
      "bytes": 2245
    },
    {
      "original": "templates/practice/base.html",
      "current": "templates/shared/practice_base.html",
      "sha256": "ba6bb27303d5b50171cfefa2e8e743f101e4295ffc29ade5e3a40799bfff59b9",
      "bytes": 1011
    },
    {
      "original": "templates/storefront.html",
      "current": "templates/catalog/storefront.html",
      "sha256": "7fa0c7b6e649a6d1c654ca716b1c40da750dd8378b7fc2f04883fe36bfcccea6",
      "bytes": 80637
    },
    {
      "original": "templates/tuner/tuner.html",
      "current": "templates/tuner/tuner.html",
      "sha256": "3375fcd47e6b4c3daa10ab6be9046dfce992aabc916a326a5f683902ef83c57c",
      "bytes": 3045
    },
    {
      "original": "assets/css/account.css",
      "current": "assets/css/account/account.css",
      "sha256": "29f8ea30cc1cbd47b05547662b60e49496c61db873487874f76ee0ae3ec438c6",
      "bytes": 1810
    },
    {
      "original": "assets/css/admin.css",
      "current": "assets/css/admin/admin.css",
      "sha256": "19812559cb0a19b00059561261a37efb37750ae0148ea0024c8be1b1c52c02f7",
      "bytes": 4751
    },
    {
      "original": "assets/css/auth.css",
      "current": "assets/css/auth/auth.css",
      "sha256": "ba2d70059b7356c0c2908df6150f74de772dfbfd577a7ce2c2ee02b51cc34c6c",
      "bytes": 1042
    },
    {
      "original": "assets/css/landing.css",
      "current": "assets/css/landing/landing.css",
      "sha256": "0d40ad73bd29727de84c24486bccc2e303455d3f1ee50873e1b4fd33a8a9c4d9",
      "bytes": 8614
    },
    {
      "original": "assets/css/lessons.css",
      "current": "assets/css/lessons/lessons.css",
      "sha256": "edc0fd5f7c5eb009a70734ac4f9f52778cee83ba9b272b32b1e2d23d3519f1bf",
      "bytes": 4079
    },
    {
      "original": "assets/css/storefront.css",
      "current": "assets/css/catalog/storefront.css",
      "sha256": "0d271ff75427a2dd711d6bbecc6b3df393834b24187fafe0824685103a7ac392",
      "bytes": 12716
    },
    {
      "original": "assets/css/tuner.css",
      "current": "assets/css/tuner/tuner.css",
      "sha256": "2fab6cd8ae71c63d58afb571d9dbee8dbc1478066f29ab8c66f612c83b5257d1",
      "bytes": 3213
    },
    {
      "original": "assets/js/account.js",
      "current": "assets/js/account/account.js",
      "sha256": "598ba9b993039a12eff0c9769cda30df4547461d8f1b8bd0ae365b5fac9dc29e",
      "bytes": 4663
    },
    {
      "original": "assets/js/admin.js",
      "current": "assets/js/admin/admin.js",
      "sha256": "d517dedb01509c83b855eae02e4952d8a6e78f166e58f62729879558933c8f3d",
      "bytes": 17488
    },
    {
      "original": "assets/js/app.js",
      "current": "assets/js/shared/app.js",
      "sha256": "d9696510227fc007a6bd8b4004479ac86eb735ebae4d540d86cfd3defa3f85f7",
      "bytes": 4990
    },
    {
      "original": "assets/js/auth.js",
      "current": "assets/js/auth/auth.js",
      "sha256": "e0a5d37f5f018ebda76c4e52aacb4b421a47da261a64f12bdc5844a4e7d85c70",
      "bytes": 6439
    },
    {
      "original": "assets/js/chatbot/chatbot-ui.js",
      "current": "assets/js/chatbot/chatbot-ui.js",
      "sha256": "02163771f5623d89d4b9136a3cc9b6722c41a3187039d43abe548709887ba352",
      "bytes": 2809
    },
    {
      "original": "assets/js/storefront.js",
      "current": "assets/js/catalog/storefront.js",
      "sha256": "9a38559a4ce2bf1476de4c8e0e25dd490cdeeb75c87324c22a36cceb6bad94d5",
      "bytes": 21099
    },
    {
      "original": "assets/js/tuner.js",
      "current": "assets/js/tuner/tuner.js",
      "sha256": "0e525e2646d9cea5f3709e54ee06e1a8d5745ba87618892e643bb904ff3cf114",
      "bytes": 7390
    },
    {
      "original": "tests/practice.cjs",
      "current": "tests/practice.cjs",
      "sha256": "fb5cf1a7864ddcb26b799355d8951f7f84ef360cc764e2445a5124bb5a73175c",
      "bytes": 14285
    },
    {
      "original": "tests/serve.py",
      "current": "tests/serve.py",
      "sha256": "72adbfc1ea4df265b9ecfc30b109e0295fd36601cc6025df1e68467435a7f267",
      "bytes": 1142
    },
    {
      "original": "tests/test_app.py",
      "current": "tests/test_app.py",
      "sha256": "af64198d0e9de7f615d69aabc85d94ff0de2cda547bbbef563c1d6fcdc63d240",
      "bytes": 19237
    },
    {
      "original": "tests/test_practice.py",
      "current": "tests/test_practice.py",
      "sha256": "583d2429af70f6ebd252578fd85fc7ae02ed45cec6ff0ad0aace48dc4883a615",
      "bytes": 5068
    },
    {
      "original": "tests/tuner-pitch.cjs",
      "current": "tests/tuner-pitch.cjs",
      "sha256": "f79eb6267a78c3e5c9c8927168a4effe57c3cab56029ec8ee777745c269c0536",
      "bytes": 2818
    },
    {
      "original": "docs/guitar-practice.md",
      "current": "docs/guitar-practice.md",
      "sha256": "30b45ef65188735e5c4427eef75e150c8c8bc618e3c3e04d95db993fd9cf4de6",
      "bytes": 14394
    },
    {
      "original": "app.py",
      "current": "app.py",
      "sha256": "cb0b25e8b25de690d0cf36644f2e5521a514d011cc7d848e51983f020899c418",
      "bytes": 12197
    },
    {
      "original": "README.md",
      "current": "README.md",
      "sha256": "744efec4f18e818059a48a7d54ac1a280a9b07469dc78c7172b03ad3f2a90a87",
      "bytes": 16111
    }
  ],
  "created_files": [
    "modules/admin/__init__.py",
    "modules/ai/__init__.py",
    "modules/auth/__init__.py",
    "modules/catalog/__init__.py",
    "modules/chatbot/__init__.py",
    "modules/database/__init__.py",
    "modules/lessons/__init__.py",
    "modules/orders/__init__.py",
    "modules/tuner/__init__.py",
    "PROJECT_STRUCTURE.md",
    "docs/architecture/before.json",
    "docs/architecture/after.json",
    "docs/architecture/migration.json",
    "docs/architecture/tree-before.txt",
    "docs/architecture/tree-after.txt",
    "docs/architecture/routes-before.txt",
    "docs/architecture/routes-after.txt",
    "docs/architecture/removed-empty-folders.json",
    "docs/architecture/updated-files.md",
    "tests/test_structure.py",
    "tests/test_ai.py",
    "tests/structure-browser.cjs"
  ],
  "original_files_preserved": 117,
  "removed_source_files": [],
  "removed_empty_folders": [
    "templates/practice"
  ],
  "verification": {
    "server_tests": 29,
    "visual_comparisons": 56,
    "harmonic_pitch_cases": 90,
    "practice_layout_theme_cases": 130,
    "browser_suites": [
      "browser.cjs",
      "chatbot.cjs",
      "practice.cjs"
    ],
    "gemini_provider": "mocked; actual SQL, RAG, enrichment, and prompts exercised"
  }
}

```

## docs/architecture/before.json

```json
{
  "files": {
    "modules/__init__.py": {
      "sha256": "2fe3a29dbbda0cd7aa6cbe3929239a704a2ec11abcd8cb9ef6a494a1b58795af",
      "bytes": 33,
      "logic_sha256": "4299300987d6fa0dffff449fe772040c521698b5def8493f6758c76ffea57623"
    },
    "modules/admin.py": {
      "sha256": "4ab08fa5bc1dbaa982d1bcf79b90e1ed10f8e9f8015599fdd8201747ec96399a",
      "bytes": 8707,
      "logic_sha256": "22f1794da80825aec1bd4f3f5aadc2866661af4a3a6f9979bdb4fbad8ac9b7b2"
    },
    "modules/ai.py": {
      "sha256": "4717eb17acfc686bff31a737a920e4a7dafd3c4b02c1bc50d4d63ec0c46c5e0d",
      "bytes": 28159,
      "logic_sha256": "a06ff45bf8b174b0581df57c0b7625ddda99e78320330836bd32b150bf90cada"
    },
    "modules/auth.py": {
      "sha256": "2acb024723664ed84f3d5c7fd8b11f7ba31917b0119717eddd264def7623bced",
      "bytes": 19962,
      "logic_sha256": "5df715bd9c67067c6a478832b1e58b1611b26c5a7f774947cfeff3caeb43317c"
    },
    "modules/catalog.py": {
      "sha256": "ca93f894537d563c7350e21033b7e65cb80f525f81989423d3c8d95fdc422800",
      "bytes": 4156,
      "logic_sha256": "98414fd75f6b494c69fb23dce666fa662bb047a52184a71a4e4c742e5d27706b"
    },
    "modules/chatbot.py": {
      "sha256": "e86f85d9c7b3bb3c176c25423f79d172f3ab941cfa3c12f1eb22c70ddef045cf",
      "bytes": 1161,
      "logic_sha256": "d052b29ae60a7dc8eb9f4d03e4fd5adaf53fc98dd8fd49adb4cf076aa75f94bd"
    },
    "modules/database.py": {
      "sha256": "155b8cdf14db677488c2e70e52483deb21913aae2748543378d945b48a914d1e",
      "bytes": 2125,
      "logic_sha256": "0216fd3607b4645bb5ddb711d9c007d64cefbe722fd117d9fb42a453317c4e1e"
    },
    "modules/lessons.py": {
      "sha256": "24b800e555ab8b9c356f99d755fd782f5a1ab2813ec03226d4d21eee3e31421b",
      "bytes": 1268,
      "logic_sha256": "ddfa3aeb0e82b449ed729c4f0e8ec14f1eba79767921da402682e7be20c6c4e9"
    },
    "modules/lessons_content.py": {
      "sha256": "9fcc6445fa70025f3507b7686d02263389b092025096ef0480d48f03ab8ea314",
      "bytes": 5024,
      "logic_sha256": "540525b526da18ad11759f8f87a84d4672b071639d274588d33c1ff076f3765b"
    },
    "modules/mail.py": {
      "sha256": "ac623c8c92fa332d76d57bdca8b6d4f21f5fe5a9f487676745cf2aa6171762bf",
      "bytes": 1772,
      "logic_sha256": "9390148cf3d39e7ced40fc0577d1a7617664ec645ff2f6dd8e26a9ac63130e34"
    },
    "modules/models.py": {
      "sha256": "6657bcbd14b152577d18854908e1ac47426805c8d5acb2734b90693fc3199982",
      "bytes": 5779,
      "logic_sha256": "3935f7ddd6c308f61219914f3e5ecbc117d82fc2d6d2544c9bb6ceed4cf97663"
    },
    "modules/orders.py": {
      "sha256": "1c88ee0c0f896ed0f17c8a7a79da60791657dfec3d5ab372ef4bd06e2ae822b3",
      "bytes": 3115,
      "logic_sha256": "f28bc72eea2bfc385a9ef07648b6ec8efd9a316e94f8f085a0249b777e059a99"
    },
    "modules/rag_sync.py": {
      "sha256": "cf4aedd5bf07b4acea6ad86a8a60252143b736190853059dd26fba5aba11736f",
      "bytes": 4316,
      "logic_sha256": "962fe82fb8d729fc991fafc707cef5b8e500133055211112d946c4d118fd560a"
    },
    "modules/tuner.py": {
      "sha256": "d1fc7b469cb03ecd7181278c1cd92e1fe90b688258144a9512b95b2ccbcc92df",
      "bytes": 510,
      "logic_sha256": "047abb8f5fb02d8e5c1e0d890547a2a94d96fc698d8034c26a3bf155bc090f32"
    },
    "templates/account.html": {
      "sha256": "7ba3e1faad9374aa1695e6de316cfb9b730da1583e3c26563694b010752bc83b",
      "bytes": 5382
    },
    "templates/admin.html": {
      "sha256": "4eb813b82bce47d28181980b8a63f2881b35ad295d4d9eee73a9a49b053673e6",
      "bytes": 32901
    },
    "templates/auth.html": {
      "sha256": "5e45b25e9f86bf7046831b6a8849dd6bc94021a2f9a95888a0212f483f622dde",
      "bytes": 14442
    },
    "templates/base.html": {
      "sha256": "124d21d38a6d182e48e5d2d5ff95581eb3cc983fd87e4275a2128e4826705d0b",
      "bytes": 1219
    },
    "templates/chatbot.html": {
      "sha256": "81708a30947a9c647124a249fdd016a6283aed03201cda0e301f6c96a221366c",
      "bytes": 4915
    },
    "templates/landing.html": {
      "sha256": "491c890da602fc961ff163c8247158841fc5a0521d1063ae1b332d47c666edb2",
      "bytes": 8229
    },
    "templates/lessons/_chord_diagram.html": {
      "sha256": "d3ff41cf4a84b7091619f451b1b2b968ffd33de4a5af5917c6d9ad559cad6546",
      "bytes": 1552
    },
    "templates/lessons/chord_detail.html": {
      "sha256": "48a4413f7c9dbe9fd830f66857561042825cc77051473919541e7d0a6ae037b1",
      "bytes": 1408
    },
    "templates/lessons/chords.html": {
      "sha256": "4422af33c7686ec8ffca1f09e9f7dd9b776b30d3accd9d0c1a0cacfc0f56390f",
      "bytes": 997
    },
    "templates/lessons/getting_started.html": {
      "sha256": "40ef00b59ee2a56ed8eb5ee543439780ccdc3b21c1865e9e0bc94322fee03ca5",
      "bytes": 3852
    },
    "templates/lessons/index.html": {
      "sha256": "1ad620cb792af2809f2082bddfcc6d4d4ec65e15e45717eae9d0a3f5f15bbd47",
      "bytes": 1954
    },
    "templates/lessons/strumming.html": {
      "sha256": "e354af6b39d8bd538f2e0d32c9d513633439772b12157d66adcfb635fd6bd2b4",
      "bytes": 2238
    },
    "templates/practice/base.html": {
      "sha256": "6ec5f8f1b905b7f643000f7eec1774ed83f7d0f928ff43937674adfd182a7b00",
      "bytes": 996
    },
    "templates/practice/feature_links.html": {
      "sha256": "3f227ac38b2240a8037c13a0fcd17f83684ef35694ce38a9eb022f8c72f4e591",
      "bytes": 784
    },
    "templates/shared.html": {
      "sha256": "ccb2093302bc3d4b31730404cc86d3ee96049e14a4f19ee48483830b58a4b2eb",
      "bytes": 6497
    },
    "templates/storefront.html": {
      "sha256": "fbe9846cbfa1b5232075e34dd4002bf7727093dcc5d80037e79fe94c0562fd1e",
      "bytes": 80623
    },
    "templates/tuner/tuner.html": {
      "sha256": "40221f594630d1bbe5ea82ce21a6dcd10587d7885d3bed91fe63cc469baf1949",
      "bytes": 3038
    },
    "assets/css/account.css": {
      "sha256": "32626add35acf96d76a6ba73199d12a315d378e4de36d2053a730980d9750040",
      "bytes": 1802
    },
    "assets/css/admin.css": {
      "sha256": "2885f03e7ee6f3c1cf96ecf56c0cccefdfe4fa3a8adf5810d2345e582c6df2b6",
      "bytes": 4745
    },
    "assets/css/auth.css": {
      "sha256": "b465aca85a3195ac9bdd63ac17eef717b3fcf6e2b2b611b91d42ae38cc3f234c",
      "bytes": 1037
    },
    "assets/css/landing.css": {
      "sha256": "71fc0e1d795a619034263c93cc3826a98f91d14730181ef96e500ee13c926326",
      "bytes": 8606
    },
    "assets/css/lessons.css": {
      "sha256": "a920071b1082b6eb8eae2ed6522cbf3666f6f386ab0db814078c5e2a65ea0457",
      "bytes": 4071
    },
    "assets/css/practice.css": {
      "sha256": "3dcec32f97bbb9cf1a75450d620d135b266568932b0b96698645adea0c429720",
      "bytes": 1763
    },
    "assets/css/shared.css": {
      "sha256": "28fbb2b080ab08a99cdc768c33ca7152ca0898332104d9d3f299d25472010a38",
      "bytes": 69085
    },
    "assets/css/storefront.css": {
      "sha256": "51a4b1c619f64d08cfcf05c7bd3d87503b976a3f902bae9c64103dae922ca657",
      "bytes": 12708
    },
    "assets/css/tuner.css": {
      "sha256": "f21510ee04b0b86d567c15d97af4bfa3e10076bb8a4b965f67a1d82f16b96b44",
      "bytes": 3205
    },
    "assets/icons-LICENSE.txt": {
      "sha256": "b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57",
      "bytes": 3208
    },
    "assets/images/acoustic/Black_Cutaway.png": {
      "sha256": "37166bce95b9ddf16921c203cc4e94ac26db8641bb53119a8399c1c1ea241c58",
      "bytes": 1520429
    },
    "assets/images/acoustic/Figured_Wood.png": {
      "sha256": "7ef4cc954f2848a1f4ceb7a822e8f4248c153bd8d70e7268ae21957969a15251",
      "bytes": 1626611
    },
    "assets/images/acoustic/Mahogany_Orchestra.png": {
      "sha256": "5f17cc916fd7cc8d3bdaa822e6227438367ce5b4e639b75ee573532b041ca41c",
      "bytes": 1671055
    },
    "assets/images/acoustic/Mahogany_Parlor.png": {
      "sha256": "2eb4fdbd240f28146c8107588948a637c2c98cf0844dac71dbe3654d63876ab7",
      "bytes": 1633525
    },
    "assets/images/acoustic/Natural_Cutaway.png": {
      "sha256": "1f4e6ff653237f344b2ea51f2de9bea85ed31873899a85e2a0b71923ecd2394e",
      "bytes": 1623167
    },
    "assets/images/acoustic/Natural_Dreadnought.png": {
      "sha256": "618f0aec98fb5dc4e9a5fa2f0cf9588ad4814fb2a00bca378786da13d59f15b3",
      "bytes": 1605136
    },
    "assets/images/acoustic/Natural_Orchestra.png": {
      "sha256": "f76c15606ac754a59041cf13a081ee06263838a3745f32974b35876e0e4c315a",
      "bytes": 1595511
    },
    "assets/images/acoustic/Sunburst_Dreadnought.png": {
      "sha256": "c9bc4fb7310d198d837704a1db1bdb02092b7bc87c45951d727f76735c335028",
      "bytes": 1754723
    },
    "assets/images/acoustic/Traditional_Natural.png": {
      "sha256": "08d672067910862eb1a1e5095f3f79108c561fa74bb68069bd54a646dba533d2",
      "bytes": 1627108
    },
    "assets/images/acoustic/Vintage_Sunburst.png": {
      "sha256": "49c8d172e592e0cc8626b9fbeba3a6d1bc0d6c94bf6a259c723ecfeff75cd776",
      "bytes": 1666965
    },
    "assets/images/acoustic_studio.jpg": {
      "sha256": "69a5c0d97ecc27683f75ba24ea1e40acbbccb161296c71d88c0042bb7de2f158",
      "bytes": 13740
    },
    "assets/images/bass/Burlwood.png": {
      "sha256": "ff17b233d5bb0d21315fd3cbc5ab322ea1482de470583531d70d54623388e9f8",
      "bytes": 1907569
    },
    "assets/images/bass/Crimson_Red.png": {
      "sha256": "ccf83fbf211f878bbde0b31fd523230a60ad54d018fc3b4ecefe041e03cd9e4d",
      "bytes": 1805283
    },
    "assets/images/bass/Ivory_Semi-Hollow.png": {
      "sha256": "c976265ce2d636e2d2e6afdc0bb7da71e008df52dd0aba58455be142fc79cc98",
      "bytes": 1748374
    },
    "assets/images/bass/Midnight_Black_Modern.png": {
      "sha256": "99b9631374ff3ba964d619029ab5be6e76647b127a72aaf32d57b257cf2bd26a",
      "bytes": 1769411
    },
    "assets/images/bass/Natural_Jazz-Style.png": {
      "sha256": "fd4c463679ed0bdd5b584e70bb0fbff3b019ba5a5b86e5c27a9bb19ff4d88c82",
      "bytes": 1952251
    },
    "assets/images/bass/Natural_Spalted.png": {
      "sha256": "3b14da9508763f4c0f300c59fd3aa65cc281113e30a958e65899645e0777e8b6",
      "bytes": 1879494
    },
    "assets/images/bass/Ocean_Blue_5-String.png": {
      "sha256": "2fe1ff01df7c8f0096a26ef938f36455b55b0ac11ccddd539bf705e79fea6059",
      "bytes": 1887181
    },
    "assets/images/bass/Royal_Purple_5-String.png": {
      "sha256": "28b7533d2445a4cf1677a02014676376181e536b6421e1378b496dfb79cddc3d",
      "bytes": 1969017
    },
    "assets/images/bass/Seafoam_Green.png": {
      "sha256": "5650379b9d954a172b112ee5c2d5765d9edb8e25118b9fcff7cab22bd297bac2",
      "bytes": 1725430
    },
    "assets/images/bass/Sunburst_Vintage.png": {
      "sha256": "931417624d750494c1983da6cb104e6566afc66fec7fbdcb61d8811f37087470",
      "bytes": 1862935
    },
    "assets/images/bass_studio.jpg": {
      "sha256": "c1f9b2b845277e306ddb58ff34503092a9fe30038fb93a2f5eabb16823a6e4eb",
      "bytes": 109169
    },
    "assets/images/classical/Amber_Cedar.png": {
      "sha256": "d044c4dd45eb5186ba071a3677643a6712c53d663c14fdbff131fa6c6184dd34",
      "bytes": 1887921
    },
    "assets/images/classical/Cream_Spruce.png": {
      "sha256": "a514f1429bc1c8592328af55856e1f063a9de635c8e151c8aed8b8a05c339957",
      "bytes": 1822884
    },
    "assets/images/classical/Dark_Rosewood.png": {
      "sha256": "4158e57db852608e736383e8a20d23d24f548d24965360833065f8608e065f80",
      "bytes": 1930327
    },
    "assets/images/classical/Golden_Amber.png": {
      "sha256": "8675a3e6955c78333fb2e7f5bd7c93b403812bcc086a198f1e2e1601f117b1c6",
      "bytes": 1888978
    },
    "assets/images/classical/Light_Spruce.png": {
      "sha256": "2efd44c99c53b45959bef7f500e301539f12a9b391d6cc1793f6c286364ef2eb",
      "bytes": 1788551
    },
    "assets/images/classical/Natural_Spruce.png": {
      "sha256": "87543f7d3813c062f936f1dc69b73feee8a857c352fd33b86a30e15f1125786d",
      "bytes": 1898921
    },
    "assets/images/classical/Orange_Cedar.png": {
      "sha256": "8bb47aef66680da3aadd8bfc84f2f575e85ae14f72caf3883cbfed6393c32175",
      "bytes": 1885219
    },
    "assets/images/classical/Pale_Spruce.png": {
      "sha256": "0fffe4e96ba9e30f2ddb13aff324b0ff694419c9b2921f40fe51c2281b2f8a92",
      "bytes": 1906166
    },
    "assets/images/classical/Walnut_Heritage.png": {
      "sha256": "b9d8e7aa177239caeac5a57554c55b1ec38e082304f2da4a957450bb78a27e33",
      "bytes": 1902635
    },
    "assets/images/classical/Warm_Cedar.png": {
      "sha256": "77f2ddff277c3d73beda5e135a6ef39790014163b3fa0dfa6343d9c860a2900e",
      "bytes": 1927935
    },
    "assets/images/classical_studio.jpg": {
      "sha256": "5f97291407feedd118ab506b3bb265396a5c15cf1b31e5f12b62bd6b574f7e4d",
      "bytes": 20511
    },
    "assets/images/electric/Amber_Flame.png": {
      "sha256": "191f87eb8697965ff7fed2847540750a0615af8dac8dec1a8d6d28d55191926b",
      "bytes": 1697233
    },
    "assets/images/electric/Arctic_White.png": {
      "sha256": "33cf08af2eb3ff33af5c6009919b49192f7b5d29f4e4e1037c04d4ddbe32fd77",
      "bytes": 1579710
    },
    "assets/images/electric/Butterscotch.png": {
      "sha256": "5f9532ad896afcc48477e51269bef07d22fa917a0f5f5e051db4ecf752b6ba42",
      "bytes": 1547493
    },
    "assets/images/electric/Cherry_Red.png": {
      "sha256": "4f730e7cbaeb5b184cbf297d854126f4cd0c4c867315787480d6216777b93d6e",
      "bytes": 1739528
    },
    "assets/images/electric/Cherry_Red_Double-Cut.png": {
      "sha256": "b4fc5baf90c9d6264db165116fa290db240eee13dcd1d280c2fb7fff4fa28ccf",
      "bytes": 1570259
    },
    "assets/images/electric/Midnight_Black.png": {
      "sha256": "601d4f6580db030090d393129121495e96452d9d2ee2ee28997b9e937cc0dda4",
      "bytes": 1498712
    },
    "assets/images/electric/Ocean_Blue.png": {
      "sha256": "1a949faf505ebc91a1d2833b75252fd1278fe2d4ffb3151b6190c5b0b9476cd0",
      "bytes": 1808038
    },
    "assets/images/electric/Royal_Purple.png": {
      "sha256": "21676cf632b139bbc1b5b596d090d5bbd2986f13ffa3e37b2769d7013ce8fbfc",
      "bytes": 1773117
    },
    "assets/images/electric/Seafoam.png": {
      "sha256": "1eb8802eceaa100bde57bbff021b8035b1acf8e659e50a3d744630992f32382f",
      "bytes": 1426827
    },
    "assets/images/electric/Sunburst_Classic.png": {
      "sha256": "d4cc5e68914225df7535bb8b723b2cbf45421033716d6c955a1f2b534d94baea",
      "bytes": 1674477
    },
    "assets/images/electric_studio.jpg": {
      "sha256": "e2837d0ad664eb9f0174f1e6a01f0cdd78e47d85525abbaf93003f8400179242",
      "bytes": 252627
    },
    "assets/images/essentials.jpeg": {
      "sha256": "5a941cc5dc93b6dced703c06817fd811d2d857dc392f7649a12b2af7137d22ad",
      "bytes": 529072
    },
    "assets/images/guitar_front.jpg": {
      "sha256": "1de7adbd011a7dfa2b8c09da5298cbfee0b759d3ac63b022897582fb61875d24",
      "bytes": 47883
    },
    "assets/images/guitar_performance.jpg": {
      "sha256": "126b0f8232f241f6262cd8de6f5a48b26963763ca2550419c8f386603a34b8e6",
      "bytes": 237503
    },
    "assets/images/SOURCES.md": {
      "sha256": "a37d4f1f6120ab5790d45b974f3565c110d3e1f08bdbf46e75a7ebd1f52772e5",
      "bytes": 4682
    },
    "assets/js/account.js": {
      "sha256": "fe8d7935c2dbc37e655ef963e1e3f6670e08b9a0e9544ab1c14769b0675102e9",
      "bytes": 4655
    },
    "assets/js/admin.js": {
      "sha256": "ddc9b18ac7ce365029b71ee5cb4d7fa4626b40c150d6d17ac964bef7997cff2a",
      "bytes": 17480
    },
    "assets/js/app.js": {
      "sha256": "d378e20086dd1e100748119b6597c4b36a339dde547716bd87d9370ff02da113",
      "bytes": 4951
    },
    "assets/js/auth.js": {
      "sha256": "3a4b69f58aace8a8c13761df9df05a3542f0252f8474aa626f95f2549946f0e4",
      "bytes": 6431
    },
    "assets/js/chatbot/chatbot-api.js": {
      "sha256": "19a83b6dce32444b0904066ce82a79fdf902ac4e569333c8086da050b0214cfd",
      "bytes": 2624
    },
    "assets/js/chatbot/chatbot-ui.js": {
      "sha256": "94960c6912cba4e103d437e77daf07a10031f506c2d2d51da7ed1f6548d116e4",
      "bytes": 2802
    },
    "assets/js/chatbot/chatbot.js": {
      "sha256": "d35de20c26633e54066dc490319087380ceadf3783432c8c6d49ae9aa92875c7",
      "bytes": 1905
    },
    "assets/js/shared.js": {
      "sha256": "9219749e1ee21cdb3005d4dbb0e8db9fd9cf61c3e2b1a0a580a0315e859925a1",
      "bytes": 8360
    },
    "assets/js/storefront.js": {
      "sha256": "4463305c53676cc30ce6578380703855448f5009623b1f8b71b2491f10f0b6b3",
      "bytes": 21091
    },
    "assets/js/theme.js": {
      "sha256": "a92b5528f65110b376110ec2d32533219064e1e36e4663391acc6f4d9060f865",
      "bytes": 198
    },
    "assets/js/tuner-pitch.js": {
      "sha256": "64db3d759d078e968cf1066a29a85e4001c5e518e462d9e83ef769c8aae3c681",
      "bytes": 3728
    },
    "assets/js/tuner.js": {
      "sha256": "f9727191f5d808bbb7e4177b53727147325157ee09f417e8dc6e92b352510cb6",
      "bytes": 7396
    },
    "tests/browser.cjs": {
      "sha256": "3f5cf5edbbc1850748edf61da64157e984b1fc28b5a54957fe48d7ecedef53ad",
      "bytes": 14924
    },
    "tests/chatbot.cjs": {
      "sha256": "389f6890e0131b38348107b3599979dd665e70484c7d50d50bbb1c44b5006fbd",
      "bytes": 10814
    },
    "tests/practice.cjs": {
      "sha256": "88e2e66afe58b1a1239812714e9a371d6e800874b90f8b2dba2b47dad8e7338a",
      "bytes": 14020
    },
    "tests/serve.py": {
      "sha256": "115baceb19cfe82b03c17619f47d40954f9b5a0ac026e565f2799c1c65e1993c",
      "bytes": 1133,
      "logic_sha256": "4254fd18b12dc241d142307c6cba9de7c9afb29e5360c368033618404a5f0f89"
    },
    "tests/support.py": {
      "sha256": "751bab4db59aff61e3e1dcce01b3f066fa1dbe653024b1ceb3a2abfcaf0e8c7e",
      "bytes": 1415,
      "logic_sha256": "644c2e5ae2c38fa0c59aee6e973b83483758d27e25006551f197713d2c643def"
    },
    "tests/test_app.py": {
      "sha256": "6036ead2728fa3b50023adfa7ce12266c4019deed5c6afbe0ebdb619279cb9d3",
      "bytes": 19219,
      "logic_sha256": "0b4ed8d53dced4940439f83cb74750e62281a50f34aed1e552cee3eb9b1248c2"
    },
    "tests/test_practice.py": {
      "sha256": "2652bc5e0baf64b51e43daea79fee97d4ad4abba5101e4fb004259bfec85d2fa",
      "bytes": 5032,
      "logic_sha256": "e0bdb481479c5fe46193133d53a5f2586ac92a38087fb1ff1d32c77b03153463"
    },
    "tests/tuner-pitch.cjs": {
      "sha256": "c68872ba61ccafc60d2158a9ca23d05b49fb83620454d9279148d090d965d02b",
      "bytes": 2818
    },
    ".vscode/settings.json": {
      "sha256": "2718064407cc104a7727a2118a488348fb3308c0734c56bd8dd91734b6d921be",
      "bytes": 68
    },
    "docs/guitar-practice-source.md": {
      "sha256": "bd2b99ad79f32ee49959b4076df20e82600f612ecf9081463b19958d24b98dfe",
      "bytes": 196359
    },
    "docs/guitar-practice.md": {
      "sha256": "3fec5cb97f59eba20748bac325ba4fc440cf47c439eb10ca843e0749038fd092",
      "bytes": 13953
    },
    "database/catalog.json": {
      "sha256": "640f9e8978ddca8218a2cdd329c3ac8a2bee94a4006c17695dd64176d577fbcf",
      "bytes": 27566
    },
    "app.py": {
      "sha256": "911fc42f1aa1c3892feb2e3f01dd652cbaed14374ca721c229a8bf18c614abbb",
      "bytes": 12095,
      "logic_sha256": "cacd30d2b5b3e7ede0d01bd5afab45fb1a05e4a973a02c40ae4cc4a9b872024a"
    },
    "README.md": {
      "sha256": "f4c725240ce9a00ebb72ccdffb2aaa554589d84be3d84ed2fbdb702fb7810a1f",
      "bytes": 15033
    },
    "requirements.txt": {
      "sha256": "9ec6d970d8cc7b43819dd6517066dd7fca2b2b23138d0e012c841960e06fd388",
      "bytes": 75
    },
    ".gitignore": {
      "sha256": "67d58c4193eb86f664d972fc5fc7c2d89e63fae205fa8cd932a30d3d8ea44d18",
      "bytes": 90
    }
  },
  "routes": [
    {
      "endpoint": "account_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/account"
    },
    {
      "endpoint": "admin.add_product",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/admin/products"
    },
    {
      "endpoint": "admin.archive_product",
      "methods": [
        "DELETE",
        "OPTIONS"
      ],
      "rule": "/api/admin/products/<int:product_id>"
    },
    {
      "endpoint": "admin.customers",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/customers"
    },
    {
      "endpoint": "admin.edit_product",
      "methods": [
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/admin/products/<int:product_id>"
    },
    {
      "endpoint": "admin.export_sales",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/sales/export"
    },
    {
      "endpoint": "admin.products",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/products"
    },
    {
      "endpoint": "admin.sales",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/sales"
    },
    {
      "endpoint": "admin.settings",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/admin/settings"
    },
    {
      "endpoint": "admin.summary",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/admin/summary"
    },
    {
      "endpoint": "admin.update_order",
      "methods": [
        "OPTIONS",
        "PATCH"
      ],
      "rule": "/api/admin/sales/<order_id>"
    },
    {
      "endpoint": "auth.change_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/password"
    },
    {
      "endpoint": "auth.current_session",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/auth/session"
    },
    {
      "endpoint": "auth.forgot_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/forgot-password"
    },
    {
      "endpoint": "auth.login",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/login"
    },
    {
      "endpoint": "auth.logout",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/logout"
    },
    {
      "endpoint": "auth.profile",
      "methods": [
        "OPTIONS",
        "PATCH"
      ],
      "rule": "/api/auth/profile"
    },
    {
      "endpoint": "auth.register",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/register"
    },
    {
      "endpoint": "auth.reset_password",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/auth/reset-password"
    },
    {
      "endpoint": "catalog.finder",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/finder"
    },
    {
      "endpoint": "catalog.product",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/products/<int:product_id>"
    },
    {
      "endpoint": "catalog.products",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/products"
    },
    {
      "endpoint": "catalog.save",
      "methods": [
        "OPTIONS",
        "PUT"
      ],
      "rule": "/api/account/saved/<int:product_id>"
    },
    {
      "endpoint": "catalog.saved",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/account/saved"
    },
    {
      "endpoint": "catalog.store_info",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/store"
    },
    {
      "endpoint": "catalog.unsave",
      "methods": [
        "DELETE",
        "OPTIONS"
      ],
      "rule": "/api/account/saved/<int:product_id>"
    },
    {
      "endpoint": "chatbot.chat",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/chat"
    },
    {
      "endpoint": "chatbot.chat_status",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/chat"
    },
    {
      "endpoint": "dashboard",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/admin"
    },
    {
      "endpoint": "health",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/health"
    },
    {
      "endpoint": "index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/"
    },
    {
      "endpoint": "lessons.chord_detail",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/chords/<slug>"
    },
    {
      "endpoint": "lessons.chords",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/chords"
    },
    {
      "endpoint": "lessons.getting_started",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/getting-started"
    },
    {
      "endpoint": "lessons.index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons"
    },
    {
      "endpoint": "lessons.strumming",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/lessons/strumming"
    },
    {
      "endpoint": "login_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/login"
    },
    {
      "endpoint": "orders.checkout",
      "methods": [
        "OPTIONS",
        "POST"
      ],
      "rule": "/api/orders"
    },
    {
      "endpoint": "orders.detail",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/orders/<order_id>"
    },
    {
      "endpoint": "orders.history",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/api/orders"
    },
    {
      "endpoint": "register_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/register"
    },
    {
      "endpoint": "reset_password_page",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/reset-password"
    },
    {
      "endpoint": "shop",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/shop"
    },
    {
      "endpoint": "static",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/static/<path:filename>"
    },
    {
      "endpoint": "tuner.index",
      "methods": [
        "GET",
        "HEAD",
        "OPTIONS"
      ],
      "rule": "/tuner"
    }
  ],
  "blueprints": [
    "auth",
    "catalog",
    "orders",
    "admin",
    "chatbot",
    "tuner",
    "lessons"
  ]
}

```

## docs/architecture/migration.json

```json
{
  "modules/auth.py": "modules/auth/routes.py",
  "modules/mail.py": "modules/auth/mail.py",
  "modules/catalog.py": "modules/catalog/routes.py",
  "modules/orders.py": "modules/orders/routes.py",
  "modules/admin.py": "modules/admin/routes.py",
  "modules/chatbot.py": "modules/chatbot/routes.py",
  "modules/ai.py": "modules/ai/services.py",
  "modules/rag_sync.py": "modules/ai/rag_sync.py",
  "modules/tuner.py": "modules/tuner/routes.py",
  "modules/lessons.py": "modules/lessons/routes.py",
  "modules/lessons_content.py": "modules/lessons/data.py",
  "modules/database.py": "modules/database/connection.py",
  "modules/models.py": "modules/database/models.py",
  "templates/base.html": "templates/shared/base.html",
  "templates/shared.html": "templates/shared/components.html",
  "templates/practice/base.html": "templates/shared/practice_base.html",
  "templates/practice/feature_links.html": "templates/shared/practice_links.html",
  "templates/auth.html": "templates/auth/auth.html",
  "templates/storefront.html": "templates/catalog/storefront.html",
  "templates/account.html": "templates/account/account.html",
  "templates/admin.html": "templates/admin/admin.html",
  "templates/chatbot.html": "templates/chatbot/chatbot.html",
  "templates/landing.html": "templates/landing/landing.html",
  "assets/css/auth.css": "assets/css/auth/auth.css",
  "assets/css/storefront.css": "assets/css/catalog/storefront.css",
  "assets/css/account.css": "assets/css/account/account.css",
  "assets/css/admin.css": "assets/css/admin/admin.css",
  "assets/css/landing.css": "assets/css/landing/landing.css",
  "assets/css/tuner.css": "assets/css/tuner/tuner.css",
  "assets/css/lessons.css": "assets/css/lessons/lessons.css",
  "assets/css/shared.css": "assets/css/shared/shared.css",
  "assets/css/practice.css": "assets/css/shared/practice.css",
  "assets/js/auth.js": "assets/js/auth/auth.js",
  "assets/js/storefront.js": "assets/js/catalog/storefront.js",
  "assets/js/account.js": "assets/js/account/account.js",
  "assets/js/admin.js": "assets/js/admin/admin.js",
  "assets/js/tuner.js": "assets/js/tuner/tuner.js",
  "assets/js/tuner-pitch.js": "assets/js/tuner/pitch.js",
  "assets/js/app.js": "assets/js/shared/app.js",
  "assets/js/shared.js": "assets/js/shared/shared.js",
  "assets/js/theme.js": "assets/js/shared/theme.js",
  "docs/guitar-practice-source.md": "docs/archive/guitar-practice-source.md"
}

```

## docs/architecture/removed-empty-folders.json

```json
"templates/practice"

```

## docs/architecture/routes-after.txt

```text
Endpoint                 Methods   Rule                                
-----------------------  --------  ------------------------------------
account_page             GET       /account                            
admin.add_product        POST      /api/admin/products                 
admin.archive_product    DELETE    /api/admin/products/<int:product_id>
admin.customers          GET       /api/admin/customers                
admin.edit_product       PUT       /api/admin/products/<int:product_id>
admin.export_sales       GET       /api/admin/sales/export             
admin.products           GET       /api/admin/products                 
admin.sales              GET       /api/admin/sales                    
admin.settings           GET, PUT  /api/admin/settings                 
admin.summary            GET       /api/admin/summary                  
admin.update_order       PATCH     /api/admin/sales/<order_id>         
auth.change_password     POST      /api/auth/password                  
auth.current_session     GET       /api/auth/session                   
auth.forgot_password     POST      /api/auth/forgot-password           
auth.login               POST      /api/auth/login                     
auth.logout              POST      /api/auth/logout                    
auth.profile             PATCH     /api/auth/profile                   
auth.register            POST      /api/auth/register                  
auth.reset_password      POST      /api/auth/reset-password            
catalog.finder           POST      /api/finder                         
catalog.product          GET       /api/products/<int:product_id>      
catalog.products         GET       /api/products                       
catalog.save             PUT       /api/account/saved/<int:product_id> 
catalog.saved            GET       /api/account/saved                  
catalog.store_info       GET       /api/store                          
catalog.unsave           DELETE    /api/account/saved/<int:product_id> 
chatbot.chat             POST      /api/chat                           
chatbot.chat_status      GET       /api/chat                           
dashboard                GET       /admin                              
health                   GET       /api/health                         
index                    GET       /                                   
lessons.chord_detail     GET       /lessons/chords/<slug>              
lessons.chords           GET       /lessons/chords                     
lessons.getting_started  GET       /lessons/getting-started            
lessons.index            GET       /lessons                            
lessons.strumming        GET       /lessons/strumming                  
login_page               GET       /login                              
orders.checkout          POST      /api/orders                         
orders.detail            GET       /api/orders/<order_id>              
orders.history           GET       /api/orders                         
register_page            GET       /register                           
reset_password_page      GET       /reset-password                     
shop                     GET       /shop                               
static                   GET       /static/<path:filename>             
tuner.index              GET       /tuner

```

## docs/architecture/routes-before.txt

```text
Endpoint                 Methods   Rule                                
-----------------------  --------  ------------------------------------
account_page             GET       /account                            
admin.add_product        POST      /api/admin/products                 
admin.archive_product    DELETE    /api/admin/products/<int:product_id>
admin.customers          GET       /api/admin/customers                
admin.edit_product       PUT       /api/admin/products/<int:product_id>
admin.export_sales       GET       /api/admin/sales/export             
admin.products           GET       /api/admin/products                 
admin.sales              GET       /api/admin/sales                    
admin.settings           GET, PUT  /api/admin/settings                 
admin.summary            GET       /api/admin/summary                  
admin.update_order       PATCH     /api/admin/sales/<order_id>         
auth.change_password     POST      /api/auth/password                  
auth.current_session     GET       /api/auth/session                   
auth.forgot_password     POST      /api/auth/forgot-password           
auth.login               POST      /api/auth/login                     
auth.logout              POST      /api/auth/logout                    
auth.profile             PATCH     /api/auth/profile                   
auth.register            POST      /api/auth/register                  
auth.reset_password      POST      /api/auth/reset-password            
catalog.finder           POST      /api/finder                         
catalog.product          GET       /api/products/<int:product_id>      
catalog.products         GET       /api/products                       
catalog.save             PUT       /api/account/saved/<int:product_id> 
catalog.saved            GET       /api/account/saved                  
catalog.store_info       GET       /api/store                          
catalog.unsave           DELETE    /api/account/saved/<int:product_id> 
chatbot.chat             POST      /api/chat                           
chatbot.chat_status      GET       /api/chat                           
dashboard                GET       /admin                              
health                   GET       /api/health                         
index                    GET       /                                   
lessons.chord_detail     GET       /lessons/chords/<slug>              
lessons.chords           GET       /lessons/chords                     
lessons.getting_started  GET       /lessons/getting-started            
lessons.index            GET       /lessons                            
lessons.strumming        GET       /lessons/strumming                  
login_page               GET       /login                              
orders.checkout          POST      /api/orders                         
orders.detail            GET       /api/orders/<order_id>              
orders.history           GET       /api/orders                         
register_page            GET       /register                           
reset_password_page      GET       /reset-password                     
shop                     GET       /shop                               
static                   GET       /static/<path:filename>             
tuner.index              GET       /tuner

```

## docs/architecture/tree-after.txt

```text
AUDIA_V2/
|-- .vscode/
|   `-- settings.json
|-- assets/
|   |-- css/
|   |   |-- account/
|   |   |   `-- account.css
|   |   |-- admin/
|   |   |   `-- admin.css
|   |   |-- auth/
|   |   |   `-- auth.css
|   |   |-- catalog/
|   |   |   `-- storefront.css
|   |   |-- landing/
|   |   |   `-- landing.css
|   |   |-- lessons/
|   |   |   `-- lessons.css
|   |   |-- shared/
|   |   |   |-- practice.css
|   |   |   `-- shared.css
|   |   `-- tuner/
|   |       `-- tuner.css
|   |-- images/
|   |   |-- acoustic/
|   |   |   |-- Black_Cutaway.png
|   |   |   |-- Figured_Wood.png
|   |   |   |-- Mahogany_Orchestra.png
|   |   |   |-- Mahogany_Parlor.png
|   |   |   |-- Natural_Cutaway.png
|   |   |   |-- Natural_Dreadnought.png
|   |   |   |-- Natural_Orchestra.png
|   |   |   |-- Sunburst_Dreadnought.png
|   |   |   |-- Traditional_Natural.png
|   |   |   `-- Vintage_Sunburst.png
|   |   |-- bass/
|   |   |   |-- Burlwood.png
|   |   |   |-- Crimson_Red.png
|   |   |   |-- Ivory_Semi-Hollow.png
|   |   |   |-- Midnight_Black_Modern.png
|   |   |   |-- Natural_Jazz-Style.png
|   |   |   |-- Natural_Spalted.png
|   |   |   |-- Ocean_Blue_5-String.png
|   |   |   |-- Royal_Purple_5-String.png
|   |   |   |-- Seafoam_Green.png
|   |   |   `-- Sunburst_Vintage.png
|   |   |-- classical/
|   |   |   |-- Amber_Cedar.png
|   |   |   |-- Cream_Spruce.png
|   |   |   |-- Dark_Rosewood.png
|   |   |   |-- Golden_Amber.png
|   |   |   |-- Light_Spruce.png
|   |   |   |-- Natural_Spruce.png
|   |   |   |-- Orange_Cedar.png
|   |   |   |-- Pale_Spruce.png
|   |   |   |-- Walnut_Heritage.png
|   |   |   `-- Warm_Cedar.png
|   |   |-- electric/
|   |   |   |-- Amber_Flame.png
|   |   |   |-- Arctic_White.png
|   |   |   |-- Butterscotch.png
|   |   |   |-- Cherry_Red.png
|   |   |   |-- Cherry_Red_Double-Cut.png
|   |   |   |-- Midnight_Black.png
|   |   |   |-- Ocean_Blue.png
|   |   |   |-- Royal_Purple.png
|   |   |   |-- Seafoam.png
|   |   |   `-- Sunburst_Classic.png
|   |   |-- acoustic_studio.jpg
|   |   |-- bass_studio.jpg
|   |   |-- classical_studio.jpg
|   |   |-- electric_studio.jpg
|   |   |-- essentials.jpeg
|   |   |-- guitar_front.jpg
|   |   |-- guitar_performance.jpg
|   |   `-- SOURCES.md
|   |-- js/
|   |   |-- account/
|   |   |   `-- account.js
|   |   |-- admin/
|   |   |   `-- admin.js
|   |   |-- auth/
|   |   |   `-- auth.js
|   |   |-- catalog/
|   |   |   `-- storefront.js
|   |   |-- chatbot/
|   |   |   |-- chatbot-api.js
|   |   |   |-- chatbot-ui.js
|   |   |   `-- chatbot.js
|   |   |-- shared/
|   |   |   |-- app.js
|   |   |   |-- shared.js
|   |   |   `-- theme.js
|   |   `-- tuner/
|   |       |-- pitch.js
|   |       `-- tuner.js
|   `-- icons-LICENSE.txt
|-- database/
|   `-- catalog.json
|-- docs/
|   |-- architecture/
|   |   |-- after.json
|   |   |-- before.json
|   |   |-- migration.json
|   |   |-- removed-empty-folders.json
|   |   |-- routes-after.txt
|   |   |-- routes-before.txt
|   |   |-- tree-after.txt
|   |   |-- tree-before.txt
|   |   `-- updated-files.md
|   |-- archive/
|   |   `-- guitar-practice-source.md
|   `-- guitar-practice.md
|-- modules/
|   |-- admin/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- ai/
|   |   |-- __init__.py
|   |   |-- rag_sync.py
|   |   `-- services.py
|   |-- auth/
|   |   |-- __init__.py
|   |   |-- mail.py
|   |   `-- routes.py
|   |-- catalog/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- chatbot/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- database/
|   |   |-- __init__.py
|   |   |-- connection.py
|   |   `-- models.py
|   |-- lessons/
|   |   |-- __init__.py
|   |   |-- data.py
|   |   `-- routes.py
|   |-- orders/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- tuner/
|   |   |-- __init__.py
|   |   `-- routes.py
|   `-- __init__.py
|-- templates/
|   |-- account/
|   |   `-- account.html
|   |-- admin/
|   |   `-- admin.html
|   |-- auth/
|   |   `-- auth.html
|   |-- catalog/
|   |   `-- storefront.html
|   |-- chatbot/
|   |   `-- chatbot.html
|   |-- landing/
|   |   `-- landing.html
|   |-- lessons/
|   |   |-- _chord_diagram.html
|   |   |-- chord_detail.html
|   |   |-- chords.html
|   |   |-- getting_started.html
|   |   |-- index.html
|   |   `-- strumming.html
|   |-- shared/
|   |   |-- base.html
|   |   |-- components.html
|   |   |-- practice_base.html
|   |   `-- practice_links.html
|   `-- tuner/
|       `-- tuner.html
|-- tests/
|   |-- browser.cjs
|   |-- chatbot.cjs
|   |-- practice.cjs
|   |-- serve.py
|   |-- structure-browser.cjs
|   |-- support.py
|   |-- test_ai.py
|   |-- test_app.py
|   |-- test_practice.py
|   |-- test_structure.py
|   `-- tuner-pitch.cjs
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- debug.log
|-- PROJECT_STRUCTURE.md
|-- README.md
`-- requirements.txt

```

## docs/architecture/tree-before.txt

```text
AUDIA_V2/
|-- .vscode/
|   `-- settings.json
|-- assets/
|   |-- css/
|   |   |-- account.css
|   |   |-- admin.css
|   |   |-- auth.css
|   |   |-- landing.css
|   |   |-- lessons.css
|   |   |-- practice.css
|   |   |-- shared.css
|   |   |-- storefront.css
|   |   `-- tuner.css
|   |-- images/
|   |   |-- acoustic/
|   |   |   |-- Black_Cutaway.png
|   |   |   |-- Figured_Wood.png
|   |   |   |-- Mahogany_Orchestra.png
|   |   |   |-- Mahogany_Parlor.png
|   |   |   |-- Natural_Cutaway.png
|   |   |   |-- Natural_Dreadnought.png
|   |   |   |-- Natural_Orchestra.png
|   |   |   |-- Sunburst_Dreadnought.png
|   |   |   |-- Traditional_Natural.png
|   |   |   `-- Vintage_Sunburst.png
|   |   |-- bass/
|   |   |   |-- Burlwood.png
|   |   |   |-- Crimson_Red.png
|   |   |   |-- Ivory_Semi-Hollow.png
|   |   |   |-- Midnight_Black_Modern.png
|   |   |   |-- Natural_Jazz-Style.png
|   |   |   |-- Natural_Spalted.png
|   |   |   |-- Ocean_Blue_5-String.png
|   |   |   |-- Royal_Purple_5-String.png
|   |   |   |-- Seafoam_Green.png
|   |   |   `-- Sunburst_Vintage.png
|   |   |-- classical/
|   |   |   |-- Amber_Cedar.png
|   |   |   |-- Cream_Spruce.png
|   |   |   |-- Dark_Rosewood.png
|   |   |   |-- Golden_Amber.png
|   |   |   |-- Light_Spruce.png
|   |   |   |-- Natural_Spruce.png
|   |   |   |-- Orange_Cedar.png
|   |   |   |-- Pale_Spruce.png
|   |   |   |-- Walnut_Heritage.png
|   |   |   `-- Warm_Cedar.png
|   |   |-- electric/
|   |   |   |-- Amber_Flame.png
|   |   |   |-- Arctic_White.png
|   |   |   |-- Butterscotch.png
|   |   |   |-- Cherry_Red.png
|   |   |   |-- Cherry_Red_Double-Cut.png
|   |   |   |-- Midnight_Black.png
|   |   |   |-- Ocean_Blue.png
|   |   |   |-- Royal_Purple.png
|   |   |   |-- Seafoam.png
|   |   |   `-- Sunburst_Classic.png
|   |   |-- acoustic_studio.jpg
|   |   |-- bass_studio.jpg
|   |   |-- classical_studio.jpg
|   |   |-- electric_studio.jpg
|   |   |-- essentials.jpeg
|   |   |-- guitar_front.jpg
|   |   |-- guitar_performance.jpg
|   |   `-- SOURCES.md
|   |-- js/
|   |   |-- chatbot/
|   |   |   |-- chatbot-api.js
|   |   |   |-- chatbot-ui.js
|   |   |   `-- chatbot.js
|   |   |-- account.js
|   |   |-- admin.js
|   |   |-- app.js
|   |   |-- auth.js
|   |   |-- shared.js
|   |   |-- storefront.js
|   |   |-- theme.js
|   |   |-- tuner-pitch.js
|   |   `-- tuner.js
|   `-- icons-LICENSE.txt
|-- database/
|   `-- catalog.json
|-- docs/
|   |-- guitar-practice-source.md
|   `-- guitar-practice.md
|-- modules/
|   |-- __init__.py
|   |-- admin.py
|   |-- ai.py
|   |-- auth.py
|   |-- catalog.py
|   |-- chatbot.py
|   |-- database.py
|   |-- lessons.py
|   |-- lessons_content.py
|   |-- mail.py
|   |-- models.py
|   |-- orders.py
|   |-- rag_sync.py
|   `-- tuner.py
|-- templates/
|   |-- lessons/
|   |   |-- _chord_diagram.html
|   |   |-- chord_detail.html
|   |   |-- chords.html
|   |   |-- getting_started.html
|   |   |-- index.html
|   |   `-- strumming.html
|   |-- practice/
|   |   |-- base.html
|   |   `-- feature_links.html
|   |-- tuner/
|   |   `-- tuner.html
|   |-- account.html
|   |-- admin.html
|   |-- auth.html
|   |-- base.html
|   |-- chatbot.html
|   |-- landing.html
|   |-- shared.html
|   `-- storefront.html
|-- tests/
|   |-- browser.cjs
|   |-- chatbot.cjs
|   |-- practice.cjs
|   |-- serve.py
|   |-- support.py
|   |-- test_app.py
|   |-- test_practice.py
|   `-- tuner-pitch.cjs
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- debug.log
|-- README.md
`-- requirements.txt

```

## docs/guitar-practice.md

````markdown
# AUDIA guitar tuner and lessons

The feature behavior described here is unchanged. Paths below reflect the
feature-based architecture; see [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)
for the migration map and current architecture.

The two features are integrated into the existing Flask application. Sign in and
open **Guitar Tuner** or **Guitar Lessons** from the landing, store, or account
page. The new pages link back to the store, products, account, and each other,
and include the existing AUDIA Assistant.

## Architecture findings

AUDIA creates its Flask app in `app.py`. Existing HTML page routes use Jinja
templates; authentication, catalog, orders, administration, and chatbot APIs
are registered as blueprints. Those APIs use `/api` prefixes. `modules/ai/services.py`
provides the Gemini/RAG service called by `modules/chatbot/routes.py`; it is not a
separate page blueprint. The database lifecycle lives in `modules/database/connection.py`,
and SQLAlchemy records live in `modules/database/models.py`. Normal development uses
PostgreSQL; tests use disposable SQLite databases.

Templates extend `templates/shared/base.html`. It loads `assets/css/shared/shared.css`, the
page's stylesheet, and `assets/js/shared/app.js`. Assets are served at `/static/`.
The shared stylesheet contains existing utilities, typography, cards, buttons,
dialogs, chatbot styling, and theme variables. Page controllers use ordinary
JavaScript modules. Repeated client-side components use HTML templates, and
navigation uses normal page URLs. Icons use the existing inline SVG style.

`modules/auth/routes.py` installs app-wide session restoration, CSRF checks, security
headers, and validation handlers. Pages inspect `g.user` and redirect guests
to `/login`; protected APIs use `require_user`. Mutating APIs require
`X-CSRF-Token`. `theme.js` and `app.js` apply the saved `audia-theme` preference
and the `html.dark` class. No new theme or authentication system was introduced.

The new modules use page blueprints to keep them independent, registered by
the same `app.register_blueprint` mechanism as existing modules. They follow
the existing page authentication and `render_template` conventions. Their
routes are read-only. No new database tables, migrations, npm dependencies,
Python dependencies, or audio upload endpoints were added.

## Files created and what each does

| File | Purpose |
| --- | --- |
| `modules/tuner/routes.py` | Authenticated `/tuner` page blueprint; no audio reaches Python. |
| `modules/lessons/routes.py` | Authenticated lesson routes and missing-chord 404 handling. |
| `modules/lessons/data.py` | Static chord shapes, finger instructions, and strumming patterns. |
| `templates/shared/practice_base.html` | Shared header, content area, and existing chatbot for both new features. |
| `templates/shared/practice_links.html` | Reusable links added below existing page headers, visible on mobile too. |
| `templates/tuner/tuner.html` | Live note readout, meter, microphone controls, errors, privacy text, and string reference. |
| `templates/lessons/index.html` | Lesson landing page and category links. |
| `templates/lessons/getting_started.html` | Guitar parts, posture, pick grip, string names, and tuning instructions. |
| `templates/lessons/chords.html` | Library of eight chords. |
| `templates/lessons/chord_detail.html` | One chord's diagram and playing instructions. |
| `templates/lessons/_chord_diagram.html` | Reusable Jinja macro that draws an accessible SVG chord diagram. |
| `templates/lessons/strumming.html` | Down/up strokes, beat counts, patterns, and practice tips. |
| `assets/css/shared/practice.css` | Shared layout for these two features, using AUDIA's existing theme variables. |
| `assets/css/tuner/tuner.css` | Tuner layout, meter, note display, and string highlight. Imports `practice.css`. |
| `assets/css/lessons/lessons.css` | Lesson grids, chord diagrams, and strumming pattern layouts. Imports `practice.css`. |
| `assets/js/tuner/tuner.js` | Start/stop controls, audio resource cleanup, errors, and pitch display. |
| `assets/js/tuner/pitch.js` | Independent YIN pitch estimator, note/cents conversion, and stabilization. |
| `tests/test_practice.py` | Routes, auth, assets, navigation, chord structure, and session revocation tests. |
| `tests/tuner-pitch.cjs` | Deterministic pitch tests with generated harmonic signals. |
| `tests/practice.cjs` | Browser audio, error/lifecycle, lessons, responsive, and theme checks. |
| `docs/guitar-practice.md` | This architecture and operating guide. |
| `docs/archive/guitar-practice-source.md` | Historical implementation snapshot from before the architecture migration. |

Lessons are static server-rendered pages, so they do not need a `lessons.js`
controller. SVG diagrams and ordinary links work without another frontend
framework or external image service.

## Existing files minimally modified

| File | Change made for this task |
| --- | --- |
| `app.py` | Import and register the `tuner` and `lessons` blueprints: four added lines. |
| `assets/js/shared/app.js` | Include the two new page names in its existing signed-in check; dynamically start the tuner controller on the tuner page only. |
| `templates/landing/landing.html` | Include the practice navigation partial after the existing header. |
| `templates/catalog/storefront.html` | Include the same navigation partial after the existing header. |
| `templates/account/account.html` | Include the same navigation partial after the existing header. |

The working tree already contained many modified/deleted/untracked files before
this task. Those changes were preserved. The table above describes only this
task's additions to existing files, not the entire difference from Git HEAD.
Authentication, CSRF hooks, catalog/order/admin handlers, models, database
behavior, AI/RAG code, and chatbot code were not intentionally changed.

## Routes added

| URL | Content |
| --- | --- |
| `/tuner` | Microphone guitar tuner |
| `/lessons` | Learn Guitar landing page |
| `/lessons/getting-started` | Five linked beginner topics |
| `/lessons/chords` | Eight-chord library |
| `/lessons/chords/<slug>` | Individual chord lesson |
| `/lessons/strumming` | Three strumming patterns |

Chord slugs are `c-major`, `g-major`, `d-major`, `a-major`, `e-major`, `a-minor`,
`e-minor`, and `d-minor`. An unknown slug returns HTTP 404 for signed-in users.
Guests are redirected to login. GET routes also support Flask's normal HEAD
and OPTIONS behavior; they do not accept POST audio or lesson updates.

## How the tuner works

1. The page starts with the microphone inactive. Only **Start Tuner** requests
   microphone permission through `getUserMedia`.
2. An `AudioContext` connects the microphone to an `AnalyserNode`. It never
   connects the microphone to the speakers. Echo cancellation, automatic gain,
   and noise suppression are requested off to preserve sustained guitar tones;
   browsers may decide how to honor those constraints.
3. The analyser supplies a 4,096-sample waveform. Around twelve times per
   second, the pitch estimator examines it locally. No `MediaRecorder`, saved
   audio, microphone network request, or server audio processing is used.
4. Weak input and unreliable periodicity are discarded. Several consistent
   readings are required before a pitch is shown. Median filtering and gentle
   smoothing reduce jitter. Silence clears the readout and displays **Play a
   string**, and playing again restores it.
5. The closest chromatic note and octave appear with frequency and cents.
   Matching E2, A2, D3, G3, B3, or E4 highlights the standard string reference.
6. **Stop Tuner** stops every track, disconnects nodes, cancels the animation
   frame, and closes the audio context. Hiding or leaving the page does the
   same. Stopping during a pending permission request also stops any stream
   that arrives later. Errors allow the player to try again.

The pitch estimator follows [YIN by de Cheveigné and Kawahara](https://pubmed.ncbi.nlm.nih.gov/12002874/).
It compares a waveform with delayed copies, calculates the cumulative mean
normalized difference, selects a reliable period, and refines it with
parabolic interpolation. Frequency is sample rate divided by period. The
working signal is averaged into a lower sample rate to reduce processing.
The range is approximately 65–420 Hz, covering the six standard guitar strings
and nearby chromatic pitches.

With A4 = 440 Hz, note selection uses:

```text
midi = round(69 + 12 × log2(frequency / 440))
targetFrequency = 440 × 2^((midi - 69) / 12)
cents = 1200 × log2(frequency / targetFrequency)
```

Within ±5 cents is **In Tune**. Offsets up to ±15 cents are **Slightly Flat**
or **Slightly Sharp**; larger offsets are **Too Flat** or **Too Sharp**. The
meter centers on zero and spans −50 to +50 cents. The tuner chooses the
nearest musical note automatically, rather than locking to a manually
selected string. If a string is far from its intended note, consult the
standard string reference and check the octave.

## How chord diagrams are generated

Each chord has six `frets` entries, from low E (left) to high E (right).
`None` means muted (X), `0` means open (O), and a positive number places a
finger on that fret. Matching `fingers` entries specify 1 index, 2 middle,
3 ring, or 4 little finger. The macro draws six vertical strings, a thick
nut, four fret spaces, labels, open/muted indicators, and numbered circles.
It includes a title and description for screen readers, uses theme colors,
and preserves its SVG aspect ratio at every screen size.

To add a chord, add a record to `CHORDS` in `modules/lessons/data.py` with
its name, symbol, frets, fingers, placements, strings played/muted, and tip.
The library, detail route, and diagram will use that record automatically.

Strumming patterns store eight slots representing `1 & 2 & 3 & 4 &`. Empty
strokes remain visible as dashes, so syncopated patterns keep their beat
alignment. In `D D U U D U`, the sounding strokes land on 1, 2, & after 2,
& after 3, 4, and & after 4.

## Run and test

Use the existing configured environment and run:

```powershell
.venv/Scripts/python.exe app.py
```

Sign in normally, then visit `http://localhost:5000/tuner` and
`http://localhost:5000/lessons`. Existing PostgreSQL and Gemini configuration
requirements remain as they were. This task did not change runtime dependency
installation or environment files.

Server and algorithm checks:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py'
node tests/tuner-pitch.cjs
```

Browser checks use the existing disposable test server:

```powershell
# Terminal 1
.venv/Scripts/python.exe tests/serve.py

# Terminal 2: with Playwright available
node tests/practice.cjs
node tests/browser.cjs
node tests/chatbot.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright installation. This
session used the existing npm cache installation, not a new project dependency:

```powershell
$env:PLAYWRIGHT_MODULE = 'C:\Users\daniel jay bernadas\AppData\Local\npm-cache\_npx\e41f203b7505f1fb\node_modules\playwright'
$env:SCREENSHOT_DIR = 'test-results/practice'
node tests/practice.cjs
```

Do not run fixture browser tests against a real customer database. The default
test URL is `http://127.0.0.1:5056`. Optional screenshots are ignored by Git.

## Verification results and limits

- Existing 20 server tests pass; four added tests pass. Python compilation
  succeeds. Route/asset checks include all new pages and every chord detail.
- Ninety generated harmonic pitch cases pass for six strings, three sample
  rates (44.1, 48, and 96 kHz), and five offsets (−25, −10, 0, +10, +25 cents).
  Silence, weak input, DC, broadband noise, and outlier stabilization pass.
- Chromium uses real Web Audio oscillators, media streams, analysers, and the
  application's pitch detector for all six string readings and meter states.
  It also checks actual `getUserMedia` capture with Chromium's fake device.
- Browser tests cover denial, missing/busy microphones, permission-pending
  cancellation, disconnect, stop/restart, silence recovery, hidden/left-page
  cleanup, unsupported audio APIs, and the insecure-address error. Some error
  and lifecycle conditions are simulated deterministically.
- All thirteen new pages pass both themes at 320, 375, 768, 1024, and 1440 px:
  130 layout cases without horizontal overflow or clipped target components.
  Chord SVGs retain their proportions, and patterns keep eight aligned beats.
  Screenshots were inspected in light and dark mode on desktop and mobile.
- Existing storefront/account/admin browser checks and chatbot browser checks
  pass, including shopping, orders, authorization, session revocation, error
  recovery, responsive layouts, themes, and CSRF retry behavior. No JavaScript
  errors or audio uploads were observed in the new feature browser suite.

Physical guitar/microphone quality and Safari/Firefox behavior have not been
verified with hardware here. AI browser checks use mocked responses; this
task did not call the paid Gemini service or change production PostgreSQL data.

Browsers require a secure context for microphone access: use HTTPS when
deployed or localhost for local development. A phone opening an ordinary
HTTP LAN IP generally needs HTTPS instead. Permissions may also be blocked
by OS settings, enterprise policy, embedding policy, or another app using the
microphone. See [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).
Audio resource release uses track stops and [AudioContext.close](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/close).

The tuner works best with one open string in a quiet room. Chords, background
music, heavy distortion, very weak sustain, or strong harmonics can confuse
pitch estimation; it does not identify multiple simultaneous notes. Real
guitar tuning remains the final manual check: test all six strings, deny and
restore permission, stop and confirm the browser microphone indicator clears,
then repeat on a phone over HTTPS.

The historical implementation snapshot is preserved in
`archive/guitar-practice-source.md`. Complete current files changed by the
architecture migration are in `architecture/updated-files.md`, including
whole files rather than isolated snippets.

````

## modules/admin/__init__.py

```python
"""Store administration API blueprint."""
from .routes import admin

```

## modules/admin/routes.py

```python
"""Protected inventory, sales, customer, reporting, and store settings endpoints."""
import csv
import io
import json
from pathlib import Path
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from flask import Blueprint, current_app, jsonify, request, Response
from sqlalchemy import select
from ..auth import payload, require_user, string, validate_email
from ..database import db
from ..database.models import Order, Product, Setting, User, now

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def sales_records():
    return list(db().scalars(select(Order).order_by(Order.created_at.desc())))


@admin.get('/sales')
@require_user(admin=True)
def sales():
    items = [order.public() for order in sales_records()]
    return jsonify(sales=items, count=len(items))


@admin.get('/sales/export')
@require_user(admin=True)
def export_sales():
    output = io.StringIO(newline='')
    columns = ['id', 'customer', 'email', 'product', 'date', 'amount', 'payment', 'status']
    writer = csv.writer(output)
    writer.writerow(columns)
    query, status = request.args.get('q', '').lower(), request.args.get('status', 'All')
    for order in sales_records():
        row = order.public()
        if status != 'All' and row['status'] != status:
            continue
        if query not in ' '.join(str(row[key]) for key in ('id', 'customer', 'email', 'product')).lower():
            continue
        # Neutralize spreadsheet formulas in user-controlled cells.
        values = [str(row[key]) for key in columns]
        writer.writerow(["'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value for value in values])
    return Response('\ufeff' + output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename="audia-sales.csv"'})


@admin.patch('/sales/<order_id>')
@require_user(admin=True)
def update_order(order_id):
    status = string(payload(), 'status', 30, 1)
    order = db().scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order:
        return jsonify(error='Order not found.'), 404
    transitions = {'Pending': ['Processing', 'Cancelled'], 'Processing': ['Shipped', 'Cancelled'],
                   'Shipped': ['Delivered'], 'Delivered': ['Refunded'], 'Cancelled': [], 'Refunded': []}
    if status == order.status:
        return jsonify(order=order.public())
    if status not in transitions.get(order.status, []):
        raise ValueError('That order status transition is not allowed.')
    if status in ('Cancelled', 'Refunded'):
        for item in sorted(order.items, key=lambda item: item.product_id):
            product = db().scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            product.stock += item.quantity
    order.status = status
    db().commit()
    return jsonify(order=order.public())


@admin.get('/products')
@require_user(admin=True)
def products():
    return jsonify(products=[p.public() for p in db().scalars(select(Product).order_by(Product.id))])


def product_values(data):
    values = {key: string(data, key, maximum, minimum) for key, maximum, minimum in (
        ('name', 150, 2), ('brand', 80, 1), ('category', 30, 1), ('level', 30, 1),
        ('color', 60, 0), ('badge', 40, 0), ('image', 2000, 1), ('description', 3000, 1))}
    if values['category'] not in ('Electric', 'Acoustic', 'Bass', 'Classical', 'Accessories', 'Bundles'):
        raise ValueError('Choose a valid product category.')
    if values['level'] not in ('Beginner', 'Intermediate', 'Advanced'):
        raise ValueError('Choose a valid experience level.')
    url = urlparse(values['image'])
    is_local = False
    if values['image'].startswith('/static/images/'):
        image_root = (Path(current_app.static_folder) / 'images').resolve()
        local_image = (image_root / values['image'].removeprefix('/static/images/')).resolve()
        is_local = (local_image.is_relative_to(image_root) and local_image.is_file()
                    and local_image.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.svg'))
    if not is_local and (url.scheme != 'https' or not url.netloc):
        raise ValueError('Use an HTTPS image URL or an existing /static/images/ file.')
    try:
        price = Decimal(str(data.get('price')))
    except InvalidOperation as error:
        raise ValueError('Enter a valid price.') from error
    if not price.is_finite() or not 0 < price <= 10000000 or price != price.quantize(Decimal('.01')):
        raise ValueError('Enter a positive price with at most two decimal places.')
    stock = data.get('stock')
    if type(stock) is not int or not 0 <= stock <= 100000:
        raise ValueError('Stock must be a whole number between 0 and 100,000.')
    specs = data.get('specs', [])
    if not isinstance(specs, list) or len(specs) > 20 or any(not isinstance(s, str) or len(s) > 200 for s in specs):
        raise ValueError('Enter up to 20 short specifications.')
    values.update(price=price, stock=stock, specs=json.dumps(specs), active=data.get('active', True) is True)
    return values


@admin.post('/products')
@require_user(admin=True)
def add_product():
    product = Product(**product_values(payload()))
    db().add(product)
    db().commit()
    return jsonify(product=product.public()), 201


@admin.put('/products/<int:product_id>')
@require_user(admin=True)
def edit_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    for key, value in product_values(payload()).items():
        setattr(product, key, value)
    db().commit()
    return jsonify(product=product.public())


@admin.delete('/products/<int:product_id>')
@require_user(admin=True)
def archive_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    product.active = False
    db().commit()
    return jsonify(message='Product archived. Existing order records are preserved.')


@admin.get('/customers')
@require_user(admin=True)
def customers():
    totals = defaultdict(lambda: {'orders': 0, 'amount': 0})
    for order in sales_records():
        totals[order.user_id]['orders'] += 1
        if order.status not in ('Cancelled', 'Refunded'):
            totals[order.user_id]['amount'] += float(order.total)
    return jsonify(customers=[dict(user.public(), **totals[user.id]) for user in
                              db().scalars(select(User).where(User.role == 'customer').order_by(User.created_at.desc()))])


@admin.get('/summary')
@require_user(admin=True)
def summary():
    days = 30 if request.args.get('period') == 'month' else 7
    today = now().date()
    start = today - timedelta(days=days - 1)
    records = [order for order in sales_records() if order.created_at.date() >= start]
    earned = [order for order in records if order.status == 'Delivered']
    by_day, categories = defaultdict(float), defaultdict(float)
    for order in earned:
        by_day[order.created_at.date().isoformat()] += float(order.total)
        for item in order.items:
            categories[item.category] += float(item.price * item.quantity)
    low_stock = list(db().scalars(select(Product).where(Product.active.is_(True), Product.stock <= 4)))
    customers = list(db().scalars(select(User).where(User.role == 'customer')))
    pending = sum(order.status == 'Pending' for order in sales_records())
    return jsonify(gross_revenue=sum(float(order.total) for order in earned), total_orders=len(records),
                   new_customers=sum(user.created_at.date() >= start for user in customers),
                   low_stock_items=len(low_stock), low_stock=[p.public() for p in low_stock], pending_orders=pending,
                   chart=[dict(date=(start + timedelta(days=i)).isoformat(), amount=by_day[(start + timedelta(days=i)).isoformat()])
                          for i in range(days)], categories=dict(categories), period_days=days)


@admin.route('/settings', methods=['GET', 'PUT'])
@require_user(admin=True)
def settings():
    if request.method == 'PUT':
        data = payload()
        name = string(data, 'store_name', 100, 2)
        email = validate_email(data.get('support_email'))
        for key, value in dict(store_name=name, support_email=email).items():
            db().merge(Setting(key=key, value=value))
        db().commit()
    return jsonify(settings={item.key: item.value for item in db().scalars(select(Setting))})

```

## modules/ai/__init__.py

```python
"""Gemini and RAG entry points used by the chatbot and knowledge sync."""
from .services import ask_audia, create_embedding

```

## modules/ai/rag_sync.py

```python
import json

from sqlalchemy import select, text

from .services import create_embedding
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

```

## modules/ai/services.py

```python
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

```

## modules/auth/__init__.py

```python
"""Authentication blueprint and shared security helpers."""
from .routes import (
    auth, install_security, payload, require_user, string,
    validate_email, validate_password,
)

```

## modules/auth/mail.py

```python
"""Password reset delivery; local outbox is opt-in and never served as an asset."""
import smtplib
import ssl
import uuid
from email.message import EmailMessage
from pathlib import Path
from flask import current_app
from werkzeug.exceptions import ServiceUnavailable


def send_reset(recipient, token):
    config = current_app.config
    message = EmailMessage()
    message['Subject'] = 'Reset your AUDIA password'
    message['From'] = config['SMTP_FROM']
    message['To'] = recipient
    message.set_content('Use this link within 30 minutes to reset your password:\n\n'
                        f'{config["APP_URL"]}/reset-password?token={token}\n\n'
                        'If you did not request this, you can ignore this email.')
    backend = config['MAIL_BACKEND']
    if backend == 'memory' and current_app.testing:
        current_app.extensions.setdefault('outbox', []).append(message)
    elif backend == 'file':
        folder = Path(current_app.instance_path) / 'mail'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f'{uuid.uuid4().hex}.eml').write_text(message.as_string(), encoding='utf-8')
    elif backend == 'smtp':
        try:
            with smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT'], timeout=15) as server:
                server.starttls(context=ssl.create_default_context())
                if config['SMTP_USER']:
                    server.login(config['SMTP_USER'], config['SMTP_PASSWORD'])
                server.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            raise ServiceUnavailable('Password recovery is temporarily unavailable.') from error
    else:
        raise ServiceUnavailable('Password recovery is unavailable.')

```

## modules/auth/routes.py

```python

import hashlib
import re
import secrets
from datetime import timedelta, timezone
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    request,
    session,
)
from sqlalchemy import case, delete, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from ..database import db
from ..database.models import (
    LoginSession,
    RateLimit,
    ResetToken,
    User,
    now,
)


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth",
)


# A fake hash used during failed login attempts so that
# checking a nonexistent email takes roughly the same amount
# of work as checking a real account.
DUMMY_HASH = generate_password_hash(
    secrets.token_urlsafe(32)
)


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def digest(value):
    """Create a SHA-256 hash for session/reset identifiers."""

    return hashlib.sha256(
        value.encode()
    ).hexdigest()


def expired(value):
    """Return True when a stored expiration time has passed."""

    return (
        value.replace(tzinfo=timezone.utc)
        <= now()
    )


def payload():
    """Read and validate a JSON request body."""

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Please send a valid form."
        )

    return data


def string(
    data,
    key,
    maximum=200,
    minimum=0,
):
    """Read and validate a string field from request data."""

    value = data.get(
        key,
        "",
    )

    if (
        not isinstance(value, str)
        or not minimum
        <= len(value.strip())
        <= maximum
    ):
        raise ValueError(
            f"Please enter a valid "
            f'{key.replace("_", " ")}.'
        )

    return value.strip()


def validate_email(value):
    """Validate and normalize an email address."""

    if (
        not isinstance(value, str)
        or len(value) > 254
        or not re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+",
            value.strip(),
        )
    ):
        raise ValueError(
            "Please enter a valid email address."
        )

    return value.strip().lower()


def validate_password(value):
    """Validate password length."""

    if (
        not isinstance(value, str)
        or not 10 <= len(value) <= 128
    ):
        raise ValueError(
            "Use a password between "
            "10 and 128 characters."
        )

    return value


# ---------------------------------------------------------
# Authentication decorator
# ---------------------------------------------------------

def require_user(admin=False):
    """
    Require a logged-in user.

    When admin=True, the user must also have
    the admin role.
    """

    def decorate(function):

        @wraps(function)
        def wrapped(*args, **kwargs):

            if g.user is None:
                return jsonify(
                    error="Please sign in to continue."
                ), 401

            if (
                admin
                and g.user.role != "admin"
            ):
                return jsonify(
                    error=(
                        "Administrator access "
                        "is required."
                    )
                ), 403

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorate


# ---------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------

def limit(
    action,
    identity="",
    maximum=8,
):
    """
    Atomic persistent counters shared across workers.

    Raw IP addresses / identities are not stored.
    """

    key = digest(
        f"{action}:"
        f"{request.remote_addr}:"
        f"{identity}"
    )

    from sqlalchemy.dialects.postgresql import (
        insert as pg_insert,
    )

    from sqlalchemy.dialects.sqlite import (
        insert as sqlite_insert,
    )

    insert = (
        pg_insert
        if db().bind.dialect.name == "postgresql"
        else sqlite_insert
    )

    current = now()

    statement = insert(
        RateLimit
    ).values(
        key=key,
        count=1,
        expires_at=(
            current
            + timedelta(minutes=15)
        ),
    )

    statement = statement.on_conflict_do_update(
        index_elements=["key"],
        set_={
            "count": case(
                (
                    RateLimit.expires_at
                    <= current,
                    1,
                ),
                else_=RateLimit.count + 1,
            ),
            "expires_at": case(
                (
                    RateLimit.expires_at
                    <= current,
                    current
                    + timedelta(minutes=15),
                ),
                else_=RateLimit.expires_at,
            ),
        },
    ).returning(
        RateLimit.count
    )

    count = (
        db()
        .execute(statement)
        .scalar_one()
    )

    db().commit()

    if count > maximum:

        from werkzeug.exceptions import (
            TooManyRequests,
        )

        raise TooManyRequests(
            "Too many attempts. "
            "Try again in 15 minutes."
        )


# ---------------------------------------------------------
# Login session creation
# ---------------------------------------------------------

def begin_session(
    user,
    remember=False,
):
    """
    Create a new authenticated session.

    A new CSRF token is generated whenever
    a new login session begins.
    """

    if session.get("sid"):

        db().execute(
            delete(
                LoginSession
            ).where(
                LoginSession.token_hash
                == digest(session["sid"])
            )
        )

    session.clear()

    token = secrets.token_urlsafe(32)

    session.update(
        sid=token,
        csrf=secrets.token_urlsafe(32),
    )

    session.permanent = remember

    db().add(
        LoginSession(
            token_hash=digest(token),
            user_id=user.id,
            expires_at=(
                now()
                + (
                    timedelta(days=30)
                    if remember
                    else timedelta(hours=12)
                )
            ),
        )
    )

    db().commit()

    return jsonify(
        user=user.public(),
        csrf_token=session["csrf"],
    )


# ---------------------------------------------------------
# Global security hooks
# ---------------------------------------------------------

def install_security(app):
    """
    Install session authentication, CSRF protection,
    security headers, and common error handlers.
    """

    @app.before_request
    def security():

        g.user = None

        # Static files do not require API security checks.
        if request.endpoint == "static":
            return

        # ---------------------------------------------
        # CSRF protection
        # ---------------------------------------------
        #
        # GET, HEAD, and OPTIONS do not modify server
        # state, so they do not require a CSRF token.
        #
        # POST, PUT, PATCH, DELETE, etc. must include:
        #
        # X-CSRF-Token: <token>
        #
        # The token must match the token stored inside
        # the user's Flask session.
        # ---------------------------------------------

        if (
            request.path.startswith("/api/")
            and request.method
            not in (
                "GET",
                "HEAD",
                "OPTIONS",
            )
        ):

            token = request.headers.get(
                "X-CSRF-Token",
                "",
            )

            stored_token = session.get(
                "csrf",
                "",
            )

            if (
                not token
                or not stored_token
                or not secrets.compare_digest(
                    token,
                    stored_token,
                )
            ):

                return jsonify(
                    error=(
                        "Your session has changed. "
                        "Refresh the page and try again."
                    )
                ), 403

        # ---------------------------------------------
        # Restore authenticated user
        # ---------------------------------------------

        if (
            session.get("sid")
            and "engine"
            in app.extensions
        ):

            record = db().get(
                LoginSession,
                digest(
                    session["sid"]
                ),
            )

            if (
                record is not None
                and not expired(
                    record.expires_at
                )
            ):

                g.user = db().get(
                    User,
                    record.user_id,
                )

            else:

                # Session ID is no longer valid.
                session.pop(
                    "sid",
                    None,
                )

    # -------------------------------------------------
    # Security headers
    # -------------------------------------------------

    @app.after_request
    def headers(response):

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "SAMEORIGIN"

        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        if (
            request.path.startswith("/api/")
            or response.mimetype == "text/html"
        ):

            response.headers[
                "Cache-Control"
            ] = "no-store"

        return response

    # -------------------------------------------------
    # Validation errors
    # -------------------------------------------------

    @app.errorhandler(ValueError)
    def invalid(error):

        db_session = g.get(
            "db"
        )

        if db_session:
            db_session.rollback()

        return jsonify(
            error=str(error)
        ), 400

    # -------------------------------------------------
    # Rate-limit errors
    # -------------------------------------------------

    @app.errorhandler(429)
    def throttled(error):

        return jsonify(
            error=error.description
        ), 429, {
            "Retry-After": "900"
        }


# ---------------------------------------------------------
# Session / CSRF initialization
# ---------------------------------------------------------

@auth.get("/session")
def current_session():
    """
    Return the currently signed-in user and initialize
    a CSRF token for this browser session.

    This endpoint can also be used by guests before
    sending POST requests such as /api/chat.
    """

    session.setdefault(
        "csrf",
        secrets.token_urlsafe(32),
    )

    return jsonify(
        user=(
            g.user.public()
            if g.user
            else None
        ),
        csrf_token=session["csrf"],
        services_ready=(
            "engine"
            in current_app.extensions
        ),
    )


# ---------------------------------------------------------
# Registration
# ---------------------------------------------------------

@auth.post("/register")
def register():

    data = payload()

    email = validate_email(
        data.get("email")
    )

    password = validate_password(
        data.get("password")
    )

    name = string(
        data,
        "name",
        100,
        2,
    )

    limit(
        "register",
        maximum=10,
    )

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(
            password
        ),
        role="customer",
    )

    db().add(user)

    try:

        db().flush()

    except IntegrityError:

        db().rollback()

        return jsonify(
            error=(
                "An account with that email "
                "already exists. "
                "Sign in or reset your password."
            )
        ), 409

    # Creating an account does not automatically
    # sign the customer in.
    db().commit()

    return jsonify(
        message=(
            "Account created successfully. "
            "Please sign in."
        )
    ), 201


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@auth.post("/login")
def login():

    data = payload()

    email = validate_email(
        data.get("email")
    )

    password = data.get(
        "password",
        "",
    )

    if (
        not isinstance(password, str)
        or len(password) > 128
    ):

        raise ValueError(
            "Please enter a valid password."
        )

    limit(
        "login-ip",
        maximum=40,
    )

    limit(
        "login",
        email,
    )

    user = db().scalar(
        select(
            User
        ).where(
            User.email == email
        )
    )

    valid = check_password_hash(
        (
            user.password_hash
            if user
            else DUMMY_HASH
        ),
        password,
    )

    if (
        not valid
        or not user
        or (
            data.get("role") == "admin"
            and user.role != "admin"
        )
    ):

        return jsonify(
            error=(
                "Incorrect email or password."
            )
        ), 401

    return begin_session(
        user,
        data.get("remember") is True,
    )


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@auth.post("/logout")
def logout():

    if session.get("sid"):

        db().execute(
            delete(
                LoginSession
            ).where(
                LoginSession.token_hash
                == digest(
                    session["sid"]
                )
            )
        )

        db().commit()

    session.clear()

    # Immediately provide a new CSRF token so that
    # the browser can continue making guest requests.
    session["csrf"] = (
        secrets.token_urlsafe(32)
    )

    return jsonify(
        message="Signed out.",
        csrf_token=session["csrf"],
    )


# ---------------------------------------------------------
# Profile
# ---------------------------------------------------------

@auth.patch("/profile")
@require_user()
def profile():

    data = payload()

    g.user.name = string(
        data,
        "name",
        100,
        2,
    )

    g.user.address = string(
        data,
        "address",
        500,
    )

    g.user.phone = string(
        data,
        "phone",
        30,
    )

    db().commit()

    return jsonify(
        user=g.user.public()
    )


# ---------------------------------------------------------
# Change password
# ---------------------------------------------------------

@auth.post("/password")
@require_user()
def change_password():

    data = payload()

    password = validate_password(
        data.get("password")
    )

    limit(
        "change-password",
        str(g.user.id),
    )

    current = data.get(
        "current_password",
        "",
    )

    if (
        not isinstance(current, str)
        or not check_password_hash(
            g.user.password_hash,
            current,
        )
    ):

        return jsonify(
            error=(
                "Your current password "
                "is incorrect."
            )
        ), 400

    g.user.password_hash = (
        generate_password_hash(
            password
        )
    )

    # Revoke every existing login session
    # belonging to this account.
    db().execute(
        delete(
            LoginSession
        ).where(
            LoginSession.user_id
            == g.user.id
        )
    )

    # Revoke active password-reset tokens.
    db().execute(
        delete(
            ResetToken
        ).where(
            ResetToken.user_id
            == g.user.id
        )
    )

    # Create a fresh session.
    return begin_session(
        g.user,
        session.permanent,
    )


# ---------------------------------------------------------
# Forgot password
# ---------------------------------------------------------

@auth.post("/forgot-password")
def forgot_password():

    from .mail import send_reset

    data = payload()

    email = validate_email(
        data.get("email")
    )

    limit(
        "recovery",
        maximum=8,
    )

    if (
        current_app.config[
            "MAIL_BACKEND"
        ]
        == "disabled"
    ):

        return jsonify(
            error=(
                "Password recovery is unavailable. "
                "Please contact the store."
            )
        ), 503

    user = db().scalar(
        select(
            User
        ).where(
            User.email == email
        )
    )

    if user:

        token = (
            secrets.token_urlsafe(32)
        )

        db().execute(
            delete(
                ResetToken
            ).where(
                ResetToken.user_id
                == user.id
            )
        )

        db().add(
            ResetToken(
                token_hash=digest(
                    token
                ),
                user_id=user.id,
                expires_at=(
                    now()
                    + timedelta(
                        minutes=30
                    )
                ),
            )
        )

        send_reset(
            user.email,
            token,
        )

        db().commit()

    # Same response whether or not the email exists.
    return jsonify(
        message=(
            "If an account exists for that email, "
            "a password reset link has been sent."
        )
    )


# ---------------------------------------------------------
# Reset password
# ---------------------------------------------------------

@auth.post("/reset-password")
def reset_password():

    data = payload()

    password = validate_password(
        data.get("password")
    )

    token = string(
        data,
        "token",
        100,
        20,
    )

    limit(
        "reset",
        maximum=10,
    )

    record = db().scalar(
        select(
            ResetToken
        )
        .where(
            ResetToken.token_hash
            == digest(token)
        )
        .with_for_update()
    )

    if (
        not record
        or expired(
            record.expires_at
        )
    ):

        return jsonify(
            error=(
                "This reset link is invalid "
                "or expired. "
                "Request a new one."
            )
        ), 400

    user = db().get(
        User,
        record.user_id,
    )

    user.password_hash = (
        generate_password_hash(
            password
        )
    )

    # Revoke all existing sessions.
    db().execute(
        delete(
            LoginSession
        ).where(
            LoginSession.user_id
            == user.id
        )
    )

    # Revoke reset tokens.
    db().execute(
        delete(
            ResetToken
        ).where(
            ResetToken.user_id
            == user.id
        )
    )

    db().commit()

    session.clear()

    # Create a new guest CSRF token after reset.
    session["csrf"] = (
        secrets.token_urlsafe(32)
    )

    return jsonify(
        message=(
            "Password updated. "
            "You can now sign in."
        ),
        csrf_token=session["csrf"],
    )

```

## modules/catalog/__init__.py

```python
"""Store, recommendations, and saved-instrument API blueprint."""
from .routes import catalog

```

## modules/catalog/routes.py

```python
"""Catalog, guitar recommendations, saved instruments, and the support guide."""
import json
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select
from ..auth import payload, require_user, string
from ..database import db, seed_catalog
from ..database.models import FinderProfile, Product, Wishlist, Setting

catalog = Blueprint('catalog', __name__, url_prefix='/api')


@catalog.get('/store')
def store_info():
    values = {'store_name': 'AUDIA Flagship', 'support_email': 'support@audia.ph'}
    if 'engine' in current_app.extensions:
        values.update({item.key: item.value for item in db().scalars(select(Setting))
                       if item.key in values})
    return jsonify(store=values)


def products_data():
    if 'engine' not in current_app.extensions:
        return seed_catalog(current_app)
    return [p.public() for p in db().scalars(select(Product).where(Product.active.is_(True)).order_by(Product.id))]


@catalog.get('/products')
@require_user()
def products():
    category = request.args.get('category', 'all').lower()
    query = request.args.get('q', '').lower()
    items = [p for p in products_data() if (category == 'all' or p['category'].lower() == category)
             and query in f'{p["name"]} {p["brand"]}'.lower()]
    return jsonify(products=items, count=len(items), preview='engine' not in current_app.extensions)


@catalog.get('/products/<int:product_id>')
@require_user()
def product(product_id):
    item = next((p for p in products_data() if p['id'] == product_id), None)
    return jsonify(item) if item else (jsonify(error='Product not found.'), 404)


@catalog.post('/finder')
@require_user()
def finder():
    data = payload()
    budget = data.get('budget', 20000)
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or not 1000 <= budget <= 500000:
        raise ValueError('Choose a budget between ₱1,000 and ₱500,000.')
    category = string(data, 'category', 30, 1)
    level = string(data, 'level', 30, 1)
    if category not in ('Electric', 'Acoustic', 'Bass', 'Classical') or level not in ('Beginner', 'Intermediate', 'Advanced'):
        raise ValueError('Choose a valid guitar type and experience level.')
    profile = dict(budget=budget, category=category, level=level, genre=string(data, 'genre', 40))
    def score(item):
        return ((50 if item['category'] == category else 0) + (25 if item['level'] == level else 0)
                + max(0, 25 - abs(item['price'] - budget) / budget * 25))
    items = [p for p in products_data() if p['stock'] > 0 and p['category'] in ('Electric', 'Acoustic', 'Bass', 'Classical')]
    ranked = sorted(items, key=score, reverse=True)[:2]
    if g.user:
        db().merge(FinderProfile(user_id=g.user.id, profile=json.dumps(profile)))
        db().commit()
    return jsonify(profile=profile, recommendations=ranked)


@catalog.get('/account/saved')
@require_user()
def saved():
    items = db().scalars(select(Product).join(Wishlist).where(Wishlist.user_id == g.user.id, Product.active.is_(True)))
    profile = db().get(FinderProfile, g.user.id)
    return jsonify(products=[p.public() for p in items], profile=json.loads(profile.profile) if profile else None)


@catalog.put('/account/saved/<int:product_id>')
@require_user()
def save(product_id):
    product = db().get(Product, product_id)
    if not product or not product.active:
        return jsonify(error='This instrument is no longer available.'), 404
    # ON CONFLICT makes repeated save requests idempotent.
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    insert = pg_insert if db().bind.dialect.name == 'postgresql' else sqlite_insert
    db().execute(insert(Wishlist).values(user_id=g.user.id, product_id=product_id).on_conflict_do_nothing())
    db().commit()
    return jsonify(saved=True)


@catalog.delete('/account/saved/<int:product_id>')
@require_user()
def unsave(product_id):
    record = db().get(Wishlist, (g.user.id, product_id))
    if record:
        db().delete(record)
        db().commit()
    return jsonify(saved=False)


```

## modules/chatbot/__init__.py

```python
"""AUDIA Assistant HTTP API blueprint."""
from .routes import chatbot

```

## modules/chatbot/routes.py

```python
from flask import Blueprint, current_app, jsonify, request

from modules.ai import ask_audia
from modules.database import db

chatbot = Blueprint(
    "chatbot",
    __name__,
    url_prefix="/api"
)


@chatbot.get("/chat")
def chat_status():
    return jsonify({
        "status": "ok",
        "service": "AUDIA Assistant",
        "message": "AUDIA chatbot API is running."
    })


@chatbot.post("/chat")
def chat():

    data = request.get_json(
        silent=True
    ) or {}

    message = str(
        data.get("message", "")
    ).strip()

    if not message:
        return jsonify({
            "error": "Message is required."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "Message is too long."
        }), 400

    try:
        result = ask_audia(message)

        return jsonify(result)

    except Exception:
        db().rollback()

        current_app.logger.exception(
        "AUDIA AI request failed"
        )

        return jsonify({
        "error": (
            "AUDIA Assistant is currently unavailable."
        )
        }), 503

```

## modules/database/__init__.py

```python
"""Shared database connection lifecycle and non-destructive initialization."""
from .connection import db, init_database, initialize, seed_catalog

```

## modules/database/connection.py

```python
"""Database connection lifecycle and non-destructive initial schema setup."""
import json
from pathlib import Path
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Setting


def init_database(app):
    url = app.config['DATABASE_URL']
    if url:
        url = make_url(url)
        if url.drivername in ('postgres', 'postgresql'):
            url = url.set(drivername='postgresql+psycopg')
        if not app.testing and url.drivername != 'postgresql+psycopg':
            raise ValueError('DATABASE_URL must point to PostgreSQL.')
        engine = create_engine(url, pool_pre_ping=True)
        app.extensions['engine'] = engine
        app.extensions['db_factory'] = sessionmaker(engine, expire_on_commit=False)

    @app.teardown_appcontext
    def close_session(error=None):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()


def db():
    if 'db' not in g:
        factory = current_app.extensions.get('db_factory')
        if not factory:
            from werkzeug.exceptions import ServiceUnavailable
            raise ServiceUnavailable('Configure DATABASE_URL first.')
        g.db = factory()
    return g.db


def seed_catalog(app):
    return json.loads((Path(app.root_path) / 'database/catalog.json').read_text(encoding='utf-8'))


def initialize(app):
    engine = app.extensions.get('engine')
    if engine is None:
        raise RuntimeError('Set DATABASE_URL in .env before initializing the database.')
    Base.metadata.create_all(engine)
    with app.app_context():
        if not db().query(Product).first():
            for item in seed_catalog(app):
                item.pop('id')
                item['specs'] = json.dumps(item['specs'])
                db().add(Product(**item))
        for key, value in {'store_name': 'AUDIA Flagship', 'support_email': 'support@audia.ph'}.items():
            if db().get(Setting, key) is None:
                db().add(Setting(key=key, value=value))
        db().commit()

```

## modules/database/models.py

```python
"""Persistent records shared by feature modules."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16), default='customer')
    address: Mapped[str] = mapped_column(Text, default='')
    phone: Mapped[str] = mapped_column(String(30), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    def public(self):
        return {key: getattr(self, key) for key in ('id', 'name', 'email', 'role', 'address', 'phone')}


class LoginSession(Base):
    __tablename__ = 'login_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ResetToken(Base):
    __tablename__ = 'password_resets'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RateLimit(Base):
    __tablename__ = 'rate_limits'
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    brand: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    stock: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(30), default='Beginner')
    color: Mapped[str] = mapped_column(String(60), default='')
    badge: Mapped[str] = mapped_column(String(40), default='')
    image: Mapped[str] = mapped_column(Text, default='')
    description: Mapped[str] = mapped_column(Text, default='')
    specs: Mapped[str] = mapped_column(Text, default='[]')
    rating: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def public(self):
        import json
        data = {key: getattr(self, key) for key in ('id', 'name', 'brand', 'category', 'stock', 'level',
                 'color', 'badge', 'image', 'description', 'reviews', 'active')}
        return dict(data, price=float(self.price), rating=float(self.rating), specs=json.loads(self.specs))


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    customer: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))
    address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(30))
    total: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(24), default='Pending')
    payment: Mapped[str] = mapped_column(String(30), default='Cash on delivery')
    request_key: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    items: Mapped[list['OrderItem']] = relationship(cascade='all, delete-orphan', lazy='selectin')
    __table_args__ = (UniqueConstraint('user_id', 'request_key'),)

    def public(self):
        return dict(id=self.id, customer=self.customer, email=self.email, address=self.address,
                    phone=self.phone, amount=float(self.total), status=self.status, payment=self.payment,
                    date=self.created_at.strftime('%b %d, %Y'), created_at=self.created_at.isoformat(),
                    product=', '.join(f'{item.name} × {item.quantity}' for item in self.items),
                    items=[item.public() for item in self.items])


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    name: Mapped[str] = mapped_column(String(150))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(30))

    def public(self):
        return dict(product_id=self.product_id, name=self.name, quantity=self.quantity, price=float(self.price))


class Wishlist(Base):
    __tablename__ = 'wishlist'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)


class FinderProfile(Base):
    __tablename__ = 'finder_profiles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    profile: Mapped[str] = mapped_column(Text)


class Setting(Base):
    __tablename__ = 'settings'
    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[str] = mapped_column(Text)

```

## modules/lessons/__init__.py

```python
"""Beginner guitar lesson page blueprint."""
from .routes import lessons

```

## modules/lessons/data.py

```python
"""Beginner shapes ordered from string 6 (low E) to string 1 (high E).

A fret of None means mute; zero means open. Finger numbers: 1 index,
2 middle, 3 ring, 4 little. Add another entry to extend the chord library.
"""
CHORDS = {
    "c-major": {
        "name": "C Major", "symbol": "C",
        "frets": [None, 3, 2, 0, 1, 0], "fingers": [None, 3, 2, None, 1, None],
        "placement": ["Index: 1st fret, B string (2nd).", "Middle: 2nd fret, D string (4th).", "Ring: 3rd fret, A string (5th)."],
        "played": "Strum strings 5 to 1, starting on A. Leave G and high E open.",
        "muted": "Do not play the low E string (6th).",
        "tip": "Curve your fingers so the open G and high E strings can ring. Keep your thumb behind the neck.",
    },
    "g-major": {
        "name": "G Major", "symbol": "G",
        "frets": [3, 2, 0, 0, 0, 3], "fingers": [2, 1, None, None, None, 3],
        "placement": ["Index: 2nd fret, A string (5th).", "Middle: 3rd fret, low E string (6th).", "Ring: 3rd fret, high E string (1st)."],
        "played": "Strum all six strings. Leave D, G and B open.",
        "muted": "No strings are muted in this shape.",
        "tip": "Keep your middle finger from touching the A string and let the open middle strings ring.",
    },
    "d-major": {
        "name": "D Major", "symbol": "D",
        "frets": [None, None, 0, 2, 3, 2], "fingers": [None, None, None, 1, 3, 2],
        "placement": ["Index: 2nd fret, G string (3rd).", "Middle: 2nd fret, high E string (1st).", "Ring: 3rd fret, B string (2nd)."],
        "played": "Strum strings 4 to 1, starting on the open D string.",
        "muted": "Do not play low E (6th) or A (5th).",
        "tip": "Make a small triangle with your fingertips. Keep the ring finger clear of high E.",
    },
    "a-major": {
        "name": "A Major", "symbol": "A",
        "frets": [None, 0, 2, 2, 2, 0], "fingers": [None, None, 1, 2, 3, None],
        "placement": ["Index: 2nd fret, D string (4th).", "Middle: 2nd fret, G string (3rd).", "Ring: 2nd fret, B string (2nd)."],
        "played": "Strum strings 5 to 1. Leave A and high E open.",
        "muted": "Do not play low E (6th).",
        "tip": "Fit your fingertips into the second fret without resting the ring finger on high E.",
    },
    "e-major": {
        "name": "E Major", "symbol": "E",
        "frets": [0, 2, 2, 1, 0, 0], "fingers": [None, 2, 3, 1, None, None],
        "placement": ["Index: 1st fret, G string (3rd).", "Middle: 2nd fret, A string (5th).", "Ring: 2nd fret, D string (4th)."],
        "played": "Strum all six strings. Leave low E, B and high E open.",
        "muted": "No strings are muted in this shape.",
        "tip": "Use the tips of your fingers so your index does not mute the open B string.",
    },
    "a-minor": {
        "name": "A Minor", "symbol": "Am",
        "frets": [None, 0, 2, 2, 1, 0], "fingers": [None, None, 2, 3, 1, None],
        "placement": ["Index: 1st fret, B string (2nd).", "Middle: 2nd fret, D string (4th).", "Ring: 2nd fret, G string (3rd)."],
        "played": "Strum strings 5 to 1. Leave A and high E open.",
        "muted": "Do not play low E (6th).",
        "tip": "Keep the index finger curved to let high E ring. This shape has a darker sound than A major.",
    },
    "e-minor": {
        "name": "E Minor", "symbol": "Em",
        "frets": [0, 2, 2, 0, 0, 0], "fingers": [None, 2, 3, None, None, None],
        "placement": ["Middle: 2nd fret, A string (5th).", "Ring: 2nd fret, D string (4th)."],
        "played": "Strum all six strings. Leave low E, G, B and high E open.",
        "muted": "No strings are muted in this shape.",
        "tip": "A useful first chord: play each string separately and check that all six ring clearly.",
    },
    "d-minor": {
        "name": "D Minor", "symbol": "Dm",
        "frets": [None, None, 0, 2, 3, 1], "fingers": [None, None, None, 2, 3, 1],
        "placement": ["Index: 1st fret, high E string (1st).", "Middle: 2nd fret, G string (3rd).", "Ring: 3rd fret, B string (2nd)."],
        "played": "Strum strings 4 to 1, starting on the open D string.",
        "muted": "Do not play low E (6th) or A (5th).",
        "tip": "Reach with your ring finger gently. Press just behind each fret, rather than on the metal.",
    },
}

STRUMMING_PATTERNS = [
    {"name": "Quarter-note downstrokes", "strokes": ["D", "–", "D", "–", "D", "–", "D", "–"],
     "description": "Play D D D D: one downstroke on each numbered beat. On each &, keep moving your hand upward without touching the strings."},
    {"name": "Eighth-note alternating", "strokes": ["D", "U", "D", "U", "D", "U", "D", "U"],
     "description": "Play D U D U D U D U. Downstrokes land on numbers; upstrokes land on &. Keep both strokes even and light."},
    {"name": "Common beginner pattern", "strokes": ["D", "–", "D", "U", "–", "U", "D", "U"],
     "description": "Play D D U U D U. Skip the upstroke after 1 and the downstroke on 3, but keep your hand moving through those gaps."},
]

```

## modules/lessons/routes.py

```python
"""Read-only beginner lesson pages using static content and Jinja diagrams."""
from flask import Blueprint, abort, g, redirect, render_template, url_for

from .data import CHORDS, STRUMMING_PATTERNS

lessons = Blueprint("lessons", __name__, url_prefix="/lessons")


@lessons.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


def lesson_page(template, title, **content):
    return render_template(
        "lessons/" + template, title=title, page_name="lessons",
        stylesheet="lessons/lessons", practice_area="lessons", **content,
    )


@lessons.get("")
def index():
    return lesson_page("index.html", "Learn Guitar")


@lessons.get("/getting-started")
def getting_started():
    return lesson_page("getting_started.html", "Getting Started")


@lessons.get("/chords")
def chords():
    return lesson_page("chords.html", "Basic Chords", chords=CHORDS)


@lessons.get("/chords/<slug>")
def chord_detail(slug):
    chord = CHORDS.get(slug)
    if chord is None:
        abort(404)
    return lesson_page("chord_detail.html", chord["name"], chord=chord, slug=slug)


@lessons.get("/strumming")
def strumming():
    return lesson_page("strumming.html", "Strumming", patterns=STRUMMING_PATTERNS)

```

## modules/orders/__init__.py

```python
"""Customer checkout and order-access API blueprint."""
from .routes import orders

```

## modules/orders/routes.py

```python
"""Customer orders with server prices, inventory locking, and idempotent checkout."""
import secrets
from decimal import Decimal
from flask import Blueprint, g, jsonify
from sqlalchemy import select
from ..auth import payload, require_user, string
from ..database import db
from ..database.models import Order, OrderItem, Product, User

orders = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders.get('')
@require_user()
def history():
    items = db().scalars(select(Order).where(Order.user_id == g.user.id).order_by(Order.created_at.desc()))
    return jsonify(orders=[item.public() for item in items])


@orders.get('/<order_id>')
@require_user()
def detail(order_id):
    item = db().get(Order, order_id.upper())
    if not item or (item.user_id != g.user.id and g.user.role != 'admin'):
        return jsonify(error='No order found for this account.'), 404
    return jsonify(order=item.public())


@orders.post('')
@require_user()
def checkout():
    data = payload()
    key = string(data, 'request_key', 80, 16)
    # Serializes checkouts for the same user, including concurrent retries.
    db().scalar(select(User).where(User.id == g.user.id).with_for_update())
    existing = db().scalar(select(Order).where(Order.user_id == g.user.id, Order.request_key == key))
    if existing:
        return jsonify(order=existing.public()), 200
    address = string(data, 'address', 500, 10)
    phone = string(data, 'phone', 30, 7)
    items = data.get('items')
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        raise ValueError('Your cart must contain between 1 and 50 products.')
    quantities = {}
    for item in items:
        if not isinstance(item, dict) or type(item.get('product_id')) is not int or type(item.get('quantity')) is not int:
            raise ValueError('A cart item is invalid.')
        product_id, quantity = item['product_id'], item['quantity']
        if not 1 <= quantity <= 99 or product_id in quantities:
            raise ValueError('Please check the quantities in your cart.')
        quantities[product_id] = quantity
    products = list(db().scalars(select(Product).where(Product.id.in_(quantities)).order_by(Product.id).with_for_update()))
    if len(products) != len(quantities):
        raise ValueError('An item is no longer available. Please update your cart.')
    order = Order(id='AUD-' + secrets.token_hex(6).upper(), user_id=g.user.id, customer=g.user.name,
                  email=g.user.email, address=address, phone=phone, total=Decimal('0'), request_key=key)
    for product in products:
        quantity = quantities[product.id]
        if not product.active or product.stock < quantity:
            raise ValueError(f'{product.name} does not have enough stock. Please update your cart.')
        product.stock -= quantity
        order.total += product.price * quantity
        order.items.append(OrderItem(product_id=product.id, name=product.name, category=product.category,
                                     quantity=quantity, price=product.price))
    db().add(order)
    db().commit()
    return jsonify(order=order.public()), 201

```

## modules/tuner/__init__.py

```python
"""Guitar tuner page blueprint."""
from .routes import tuner

```

## modules/tuner/routes.py

```python
"""The signed-in guitar tuner page; microphone audio stays in the browser."""
from flask import Blueprint, g, redirect, render_template, url_for

tuner = Blueprint("tuner", __name__, url_prefix="/tuner")


@tuner.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


@tuner.get("")
def index():
    return render_template(
        "tuner/tuner.html", title="Guitar Tuner", page_name="tuner",
        stylesheet="tuner/tuner", practice_area="tuner",
    )

```

## templates/account/account.html

```html
{% extends "shared/base.html" %} {% block content %}
<div class="account-page min-h-screen">
  <header class="account-header shell">
    <button class="audia-mark" data-action="store">AUDIA</button>
    <div class="flex items-center gap-3">
      <button class="secondary-btn" data-action="store">Back to store</button
      ><button
        class="icon-btn"
        data-action="theme"
        aria-label="Change theme"
      ></button
      ><button class="secondary-btn" data-action="logout">Sign out</button>
    </div>
  </header>
  {% include 'shared/practice_links.html' %}
  <main class="shell account-main">
    <p class="section-label">Your AUDIA</p>
    <h1
      class="font-display text-4xl font-semibold mt-3"
      data-field="greeting"
    ></h1>
    <p class="mt-3 text-sm text-zinc-500">
      Your instruments, orders, and account details, together.
    </p>
    <div class="account-grid">
      <section class="surface-card account-section">
        <h2 class="font-display text-xl font-semibold">
          Profile &amp; delivery
        </h2>
        <form method="post" class="stack-form mt-6" data-form="profile">
          <label
            >Full name<input
              name="name"
              required
              minlength="2"
              maxlength="100"
              autocomplete="name" /></label
          ><label
            >Email address<input name="email" type="email" disabled /></label
          ><label
            >Phone number<input
              name="phone"
              maxlength="30"
              autocomplete="tel" /></label
          ><label
            >Delivery address<textarea
              name="address"
              maxlength="500"
              autocomplete="street-address"
            ></textarea>
          </label>
          <p class="form-error" role="alert" data-field="form-error" hidden></p>
          <button class="primary-btn" type="submit">Save profile</button>
        </form>
      </section>
      <section class="surface-card account-section">
        <h2 class="font-display text-xl font-semibold">Account security</h2>
        <p class="form-hint mt-3">
          Changing your password signs out your other sessions.
        </p>
        <form method="post" class="stack-form mt-6" data-form="password">
          <label
            >Current password<input
              name="current_password"
              type="password"
              required
              autocomplete="current-password"
              maxlength="128" /></label
          ><label
            >New password<input
              name="password"
              type="password"
              required
              minlength="10"
              maxlength="128"
              autocomplete="new-password" /></label
          ><label
            >Confirm new password<input
              name="confirm"
              type="password"
              required
              minlength="10"
              maxlength="128"
              autocomplete="new-password"
          /></label>
          <p class="form-error" role="alert" data-field="form-error" hidden></p>
          <button class="primary-btn" type="submit">Update password</button>
        </form>
      </section>
    </div>
    <section class="surface-card account-section mt-7">
      <div class="flex items-center justify-between gap-4">
        <h2 class="font-display text-xl font-semibold">Your orders</h2>
        <button class="secondary-btn" data-action="refresh-orders">
          Refresh
        </button>
      </div>
      <div class="account-orders" data-field="orders">
        <p class="empty-state">Loading your orders…</p>
      </div>
    </section>
    <section class="surface-card account-section mt-7">
      <h2 class="font-display text-xl font-semibold">Saved instruments</h2>
      <div class="saved-grid" data-field="saved">
        <p class="empty-state">Loading your saved instruments…</p>
      </div>
      <div class="finder-profile-summary">
        <p class="form-hint" data-field="finder-profile"></p>
        <button class="secondary-btn" data-action="find-guitar">
          Open Guitar Finder
        </button>
      </div>
    </section>
  </main>
</div>
{% endblock %} {% block components %}
<!-- Related cards and dialogs live here with the page that uses them. -->

<!-- Order Card -->
<template id="order-card-template">
  <article class="account-order">
    <div>
      <h3 class="font-semibold text-sm" data-field="id"></h3>
      <p class="form-hint" data-field="date"></p>
      <p class="text-xs mt-2" data-field="product"></p>
    </div>
    <div class="account-order-actions">
      <span class="order-status" data-field="status"></span
      ><strong data-field="amount"></strong
      ><button class="secondary-btn" data-action="view-order">
        View order
      </button>
    </div>
  </article>
</template>

<!-- Saved Item -->
<template id="saved-item-template">
  <article class="saved-item">
    <img data-field="image" alt="" />
    <div>
      <h3 class="font-semibold text-sm" data-field="name"></h3>
      <p class="form-hint" data-field="price"></p>
      <div class="form-actions">
        <button class="secondary-btn" data-action="saved-shop">
          Shop instrument</button
        ><button class="danger-btn" data-action="unsave">Remove</button>
      </div>
    </div>
  </article>
</template>
{% endblock %}

```

## templates/admin/admin.html

```html
{% extends "shared/base.html" %} {% block content %}
<div class="admin-page min-h-screen bg-stone-50 dark:bg-ink">
  <aside
    class="fixed inset-y-0 left-0 z-50 flex w-[270px] flex-col border-r border-zinc-200 bg-white p-5 transition-transform dark:border-white/10 dark:bg-[#0d0d10] lg:translate-x-0 -translate-x-full"
  >
    <div class="flex h-12 items-center justify-between px-2">
      <button
        class="audia-mark flex items-center text-left text-lg"
        aria-label="Go to AUDIA home"
        data-action="overview"
      >
        <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
      </button>
      <button
        class="icon-btn lg:hidden"
        data-action="close-sidebar"
        aria-label="Close admin menu"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-x"
          aria-hidden="true"
        >
          <path d="M18 6 6 18"></path>
          <path d="m6 6 12 12"></path>
        </svg>
      </button>
    </div>
    <div class="mt-7 rounded-2xl bg-zinc-100 p-3 dark:bg-white/[.055]">
      <div class="flex items-center gap-3">
        <div
          class="grid h-10 w-10 place-items-center rounded-xl bg-zinc-950 text-white dark:bg-acid dark:text-ink"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-store"
            aria-hidden="true"
          >
            <path d="M15 21v-5a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v5"></path>
            <path
              d="M17.774 10.31a1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.451 0 1.12 1.12 0 0 0-1.548 0 2.5 2.5 0 0 1-3.452 0 1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.77-3.248l2.889-4.184A2 2 0 0 1 7 2h10a2 2 0 0 1 1.653.873l2.895 4.192a2.5 2.5 0 0 1-3.774 3.244"
            ></path>
            <path d="M4 10.95V19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8.05"></path>
          </svg>
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold" data-field="store-name">
            AUDIA Flagship
          </p>
          <p class="text-[10px] text-zinc-500">Main storefront</p>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-chevron-down ml-auto text-zinc-500"
          aria-hidden="true"
        >
          <path d="m6 9 6 6 6-6"></path>
        </svg>
      </div>
    </div>
    <nav class="mt-7 space-y-1">
      <p
        class="mb-3 px-3 text-[9px] font-bold uppercase tracking-[.18em] text-zinc-400"
      >
        Workspace
      </p>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition bg-zinc-950 text-white dark:bg-acid dark:text-ink"
        data-action="overview"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-layout-dashboard"
          aria-hidden="true"
        >
          <rect width="7" height="9" x="3" y="3" rx="1"></rect>
          <rect width="7" height="5" x="14" y="3" rx="1"></rect>
          <rect width="7" height="9" x="14" y="12" rx="1"></rect>
          <rect width="7" height="5" x="3" y="16" rx="1"></rect>
        </svg>
        Overview
      </button>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition text-zinc-500 hover:bg-zinc-100 hover:text-zinc-950 dark:hover:bg-white/5 dark:hover:text-white"
        data-action="sales"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-circle-dollar-sign"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"></path>
          <path d="M12 18V6"></path>
        </svg>
        Sales directory<span
          class="ml-auto rounded-full px-2 py-0.5 text-[9px] bg-zinc-100 dark:bg-white/5"
          data-field="order-count"
          >0</span
        >
      </button>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition text-zinc-500 hover:bg-zinc-100 hover:text-zinc-950 dark:hover:bg-white/5 dark:hover:text-white"
        data-action="products"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-package"
          aria-hidden="true"
        >
          <path
            d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"
          ></path>
          <path d="M12 22V12"></path>
          <polyline points="3.29 7 12 12 20.71 7"></polyline>
          <path d="m7.5 4.27 9 5.15"></path>
        </svg>
        Products
      </button>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition text-zinc-500 hover:bg-zinc-100 hover:text-zinc-950 dark:hover:bg-white/5 dark:hover:text-white"
        data-action="customers"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-users"
          aria-hidden="true"
        >
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
          <path d="M16 3.128a4 4 0 0 1 0 7.744"></path>
          <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
          <circle cx="9" cy="7" r="4"></circle>
        </svg>
        Customers
      </button>
    </nav>
    <div
      class="mt-auto space-y-1 border-t border-zinc-200 pt-4 dark:border-white/10"
    >
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-500 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="settings"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-settings"
          aria-hidden="true"
        >
          <path
            d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"
          ></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
        Settings
      </button>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-500 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="store"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-arrow-left"
          aria-hidden="true"
        >
          <path d="m12 19-7-7 7-7"></path>
          <path d="M19 12H5"></path>
        </svg>
        View storefront
      </button>
      <button
        class="w-full px-3 pt-3 text-left text-[11px] text-zinc-400 hover:text-rose-500"
        data-action="logout"
      >
        Sign out of admin
      </button>
    </div>
  </aside>
  <div class="lg:pl-[270px]">
    <header
      class="sticky top-0 z-30 flex h-[78px] items-center justify-between border-b border-zinc-200 bg-stone-50/90 px-5 backdrop-blur-xl dark:border-white/10 dark:bg-ink/90 sm:px-8"
    >
      <div class="flex items-center gap-3">
        <button
          class="icon-btn lg:hidden"
          data-action="sidebar"
          aria-label="Open admin menu"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-menu"
            aria-hidden="true"
          >
            <path d="M4 5h16"></path>
            <path d="M4 12h16"></path>
            <path d="M4 19h16"></path>
          </svg>
        </button>
        <div>
          <p class="text-[10px] uppercase tracking-[.15em] text-zinc-400">
            Administration
          </p>
          <h1
            class="font-display text-xl font-semibold"
            data-field="admin-title"
          >
            Overview
          </h1>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="icon-btn relative"
          aria-label="Notifications"
          data-action="notifications"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-bell"
            aria-hidden="true"
          >
            <path d="M10.268 21a2 2 0 0 0 3.464 0"></path>
            <path
              d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"
            ></path>
          </svg>
          <span
            class="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-500"
          ></span>
        </button>
        <button
          class="theme-toggle relative flex items-center rounded-full border border-zinc-200 bg-white text-zinc-700 shadow-sm transition hover:border-zinc-300 dark:border-white/10 dark:bg-white/[.05] dark:text-zinc-200 h-10 w-10 justify-center"
          aria-label="Switch to light mode"
          title="Switch to light mode"
          data-action="theme"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-sun"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2"></path>
            <path d="M12 20v2"></path>
            <path d="m4.93 4.93 1.41 1.41"></path>
            <path d="m17.66 17.66 1.41 1.41"></path>
            <path d="M2 12h2"></path>
            <path d="M20 12h2"></path>
            <path d="m6.34 17.66-1.41 1.41"></path>
            <path d="m19.07 4.93-1.41 1.41"></path>
          </svg>
        </button>
        <div
          class="ml-1 hidden items-center gap-3 border-l border-zinc-200 pl-4 dark:border-white/10 sm:flex"
        >
          <div
            class="grid h-9 w-9 place-items-center rounded-full bg-violet-100 text-xs font-bold text-violet-700 dark:bg-violet-400/15 dark:text-violet-300"
          >
            AJ
          </div>
          <div>
            <p class="text-xs font-semibold" data-field="admin-name">
              AUDIA Admin
            </p>
            <p class="text-[10px] text-zinc-500">Store manager</p>
          </div>
        </div>
      </div>
    </header>
    <main class="p-5 sm:p-8 xl:p-10" data-field="admin-view"></main>
  </div>
</div>
{% endblock %} {% block components %}
<!-- Related cards and dialogs live here with the page that uses them. -->

<!-- Overview -->
<template id="overview-template">
  <div>
    <div class="admin-section-heading">
      <div>
        <p class="text-sm text-zinc-500" data-field="today"></p>
        <h2
          class="mt-1 font-display text-3xl font-semibold"
          data-field="admin-greeting"
        >
          Welcome back.
        </h2>
      </div>
      <button class="primary-btn" data-action="add-product">
        <span aria-hidden="true">+</span> Add product
      </button>
    </div>
    <div class="stats-grid mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div class="stat-card surface-card p-6">
        <div class="stat-glyph" aria-hidden="true">₱</div>
        <p class="mt-4 text-xs text-zinc-500">Delivered revenue</p>
        <p
          class="mt-2 font-display text-3xl font-semibold"
          data-field="gross_revenue"
        >
          —
        </p>
      </div>
      <div class="stat-card surface-card p-6">
        <div class="stat-glyph" aria-hidden="true">↗</div>
        <p class="mt-4 text-xs text-zinc-500">Total orders</p>
        <p
          class="mt-2 font-display text-3xl font-semibold"
          data-field="total_orders"
        >
          —
        </p>
      </div>
      <div class="stat-card surface-card p-6">
        <div class="stat-glyph" aria-hidden="true">◎</div>
        <p class="mt-4 text-xs text-zinc-500">New customers</p>
        <p
          class="mt-2 font-display text-3xl font-semibold"
          data-field="new_customers"
        >
          —
        </p>
      </div>
      <div class="stat-card surface-card p-6">
        <div class="stat-glyph" aria-hidden="true">◇</div>
        <p class="mt-4 text-xs text-zinc-500">Low stock items</p>
        <p
          class="mt-2 font-display text-3xl font-semibold"
          data-field="low_stock_items"
        >
          —
        </p>
      </div>
    </div>
    <div class="report-grid mt-6">
      <section class="surface-card p-6 revenue-chart">
        <div class="admin-section-heading">
          <div>
            <h3 class="font-display text-lg font-semibold">
              Revenue performance
            </h3>
            <p class="mt-1 text-xs text-zinc-500">
              Delivered orders in the selected period
            </p>
          </div>
          <label class="input-shell"
            ><select data-field="report-period" aria-label="Reporting period">
              <option value="week">Last 7 days</option>
              <option value="month">Last 30 days</option>
            </select></label
          >
        </div>
        <div class="revenue-plot" data-field="revenue-chart"></div>
      </section>
      <section class="surface-card p-6">
        <h3 class="font-display text-lg font-semibold">Sales by category</h3>
        <p class="mt-1 text-xs text-zinc-500">Delivered revenue</p>
        <div class="category-report" data-field="category-report"></div>
      </section>
    </div>
    <div class="surface-card mt-7 overflow-hidden">
      <div
        class="flex items-center justify-between border-b border-zinc-200 p-6 dark:border-white/10"
      >
        <div>
          <h3 class="font-display text-lg font-semibold">Recent sales</h3>
          <p class="mt-1 text-xs text-zinc-500">
            Latest completed and active orders
          </p>
        </div>
        <button class="text-xs font-semibold" data-action="sales">
          View all
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[680px] text-left">
          <thead>
            <tr class="text-[9px] uppercase tracking-widest text-zinc-500">
              <th class="px-6 py-4">Order</th>
              <th class="px-6 py-4">Customer</th>
              <th class="px-6 py-4">Product</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4 text-right">Total</th>
            </tr>
          </thead>
          <tbody
            data-field="sales-rows"
            class="divide-y divide-zinc-100 dark:divide-white/5"
          ></tbody>
        </table>
        <p class="empty-state" data-field="sales-empty" hidden>
          No orders yet. New orders will appear here.
        </p>
      </div>
    </div>
  </div>
</template>

<!-- Recent Sale -->
<template id="recent-sale-template">
  <tr class="text-xs transition hover:bg-zinc-50 dark:hover:bg-white/[.025]">
    <td class="px-5 py-4 font-semibold" data-field="id"></td>
    <td class="px-5 py-4">
      <p class="font-medium" data-field="customer"></p>
      <p class="mt-1 text-[10px] text-zinc-500" data-field="email"></p>
    </td>
    <td
      class="max-w-[180px] truncate px-5 py-4 text-zinc-500"
      data-field="product"
    ></td>
    <td class="px-5 py-4">
      <span
        class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300"
        data-field="status"
      ></span>
    </td>
    <td class="px-5 py-4 text-right font-semibold" data-field="amount"></td>
  </tr>
</template>

<!-- Sales -->
<template id="sales-template">
  <div
    data-motion='{"initial":{"opacity":0,"y":10},"animate":{"opacity":1,"y":0},"viewport":false}'
  >
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-sm text-zinc-500">All storefront transactions</p>
        <h2 class="mt-1 font-display text-3xl font-semibold tracking-tight">
          Sales directory
        </h2>
      </div>
      <button class="secondary-btn self-start" data-action="export-sales">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-download"
          aria-hidden="true"
        >
          <path d="M12 15V3"></path>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <path d="m7 10 5 5 5-5"></path>
        </svg>
        Export CSV
      </button>
    </div>
    <div class="surface-card mt-7 overflow-hidden">
      <div
        class="flex flex-col gap-3 border-b border-zinc-200 p-5 dark:border-white/10 sm:flex-row"
      >
        <label class="input-shell flex-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-search"
            aria-hidden="true"
          >
            <path d="m21 21-4.34-4.34"></path>
            <circle cx="11" cy="11" r="8"></circle>
          </svg>
          <input
            class="w-full bg-transparent py-3 text-sm outline-none"
            placeholder="Search order, customer, email, or product"
            value=""
            data-field="sales-query"
            aria-label="Search sales"
          />
        </label>
        <label class="input-shell">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-sliders-horizontal"
            aria-hidden="true"
          >
            <path d="M10 5H3"></path>
            <path d="M12 19H3"></path>
            <path d="M14 3v4"></path>
            <path d="M16 17v4"></path>
            <path d="M21 12h-9"></path>
            <path d="M21 19h-5"></path>
            <path d="M21 5h-7"></path>
            <path d="M8 10v4"></path>
            <path d="M8 12H3"></path>
          </svg>
          <select
            class="appearance-none bg-transparent py-3 pr-6 text-sm outline-none"
            data-field="sales-status"
            aria-label="Order status"
          >
            <option selected="">All</option>
            <option>Shipped</option>
            <option>Delivered</option>
            <option>Cancelled</option>
            <option>Processing</option>
            <option>Pending</option>
            <option>Refunded</option>
          </select>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-chevron-down"
            aria-hidden="true"
          >
            <path d="m6 9 6 6 6-6"></path>
          </svg>
        </label>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px] text-left">
          <thead>
            <tr
              class="bg-zinc-50 text-[9px] uppercase tracking-[.15em] text-zinc-400 dark:bg-white/[.025]"
            >
              <th class="px-5 py-4">Order ID</th>
              <th class="px-5 py-4">Customer</th>
              <th class="px-5 py-4">Product</th>
              <th class="px-5 py-4">Date</th>
              <th class="px-5 py-4">Payment</th>
              <th class="px-5 py-4">Status</th>
              <th class="px-5 py-4 text-right">Total</th>
              <th class="w-12"></th>
            </tr>
          </thead>
          <tbody
            class="divide-y divide-zinc-100 dark:divide-white/5"
            data-field="sales-rows"
          ></tbody>
        </table>
        <p class="empty-state" data-field="sales-empty" hidden>
          No orders match your search.
        </p>
      </div>
      <div
        class="flex items-center justify-between border-t border-zinc-200 px-5 py-4 text-xs text-zinc-500 dark:border-white/10"
      >
        <span data-field="sales-count">Showing 6 of 6 sales</span>
        <div class="flex gap-2">
          <button
            class="rounded-lg border border-zinc-200 px-3 py-2 dark:border-white/10"
            data-action="sales-previous"
          >
            Previous
          </button>
          <button
            class="rounded-lg border border-zinc-200 px-3 py-2 dark:border-white/10"
            data-action="sales-next"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- Sale Row -->
<template id="sale-row-template">
  <tr class="text-xs hover:bg-zinc-50 dark:hover:bg-white/[.025]">
    <td class="px-5 py-4 font-semibold" data-field="id"></td>
    <td class="px-5 py-4">
      <p class="font-medium" data-field="customer"></p>
      <p class="mt-1 text-[10px] text-zinc-500" data-field="email"></p>
    </td>
    <td
      class="max-w-[210px] truncate px-5 py-4 text-zinc-500"
      data-field="product"
    ></td>
    <td class="px-5 py-4 text-zinc-500" data-field="date"></td>
    <td class="px-5 py-4 text-zinc-500" data-field="payment"></td>
    <td class="px-5 py-4">
      <span
        class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300"
        data-field="status"
      ></span>
    </td>
    <td class="px-5 py-4 text-right font-semibold" data-field="amount"></td>
    <td class="pr-4">
      <button
        class="icon-btn h-8 w-8"
        data-action="edit-order"
        aria-label="Manage order"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-ellipsis"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="1"></circle>
          <circle cx="19" cy="12" r="1"></circle>
          <circle cx="5" cy="12" r="1"></circle>
        </svg>
      </button>
    </td>
  </tr>
</template>

<!-- Admin Products -->
<template id="admin-products-template">
  <div>
    <div class="admin-section-heading">
      <div>
        <p class="text-sm text-zinc-500">Catalog management</p>
        <h2 class="mt-1 font-display text-3xl font-semibold">Products</h2>
      </div>
      <button class="primary-btn" data-action="add-product">
        <span aria-hidden="true">+</span> Add product
      </button>
    </div>
    <label class="input-shell mt-7"
      ><input
        class="w-full bg-transparent py-3 text-sm outline-none"
        data-field="product-query"
        placeholder="Search inventory"
        aria-label="Search inventory"
    /></label>
    <div
      class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
      data-field="admin-products"
    ></div>
  </div>
</template>

<!-- Admin Product -->
<template id="admin-product-template">
  <article class="surface-card flex gap-4 p-4">
    <img data-field="image" alt="" class="h-24 w-20 rounded-xl object-cover" />
    <div class="min-w-0 flex-1">
      <p
        class="text-[10px] uppercase tracking-widest text-zinc-500"
        data-field="category"
      ></p>
      <h3 class="mt-2 text-sm font-semibold" data-field="name"></h3>
      <div class="mt-4 flex items-end justify-between gap-2">
        <div>
          <p class="text-sm font-semibold" data-field="price"></p>
          <p class="mt-1 text-[10px] text-zinc-500" data-field="stock"></p>
        </div>
        <button class="secondary-btn" data-action="edit-product">Edit</button>
      </div>
    </div>
  </article>
</template>

<!-- Product Form -->
<template id="product-form-template">
  <form method="post" class="form-grid" data-form="product">
    <label class="form-wide"
      >Product name<input name="name" required minlength="2" maxlength="150"
    /></label>
    <label>Brand<input name="brand" required maxlength="80" /></label>
    <label
      >Category<select name="category">
        <option>Electric</option>
        <option>Acoustic</option>
        <option>Bass</option>
        <option>Classical</option>
        <option>Accessories</option>
        <option>Bundles</option>
      </select></label
    >
    <label
      >Price (PHP)<input
        name="price"
        type="number"
        min="0.01"
        max="10000000"
        step="0.01"
        required
    /></label>
    <label
      >Stock quantity<input
        name="stock"
        type="number"
        min="0"
        max="100000"
        step="1"
        required
    /></label>
    <label
      >Experience level<select name="level">
        <option>Beginner</option>
        <option>Intermediate</option>
        <option>Advanced</option>
      </select></label
    >
    <label>Color<input name="color" maxlength="60" /></label>
    <label
      >Badge<input name="badge" maxlength="40" placeholder="Optional"
    /></label>
    <label class="checkbox-label"
      ><input type="checkbox" name="active" checked /> Visible in store</label
    >
    <label class="form-wide"
      >Image URL or local path<input
        name="image"
        type="text"
        required
        maxlength="2000"
        placeholder="/static/images/electric/Amber_Flame.png"
    /></label>
    <label class="form-wide"
      >Description<textarea
        name="description"
        required
        maxlength="3000"
      ></textarea>
    </label>
    <label class="form-wide"
      >Specifications, one per line<textarea
        name="specs"
        maxlength="4000"
      ></textarea>
    </label>
    <p
      class="form-error form-wide"
      data-field="form-error"
      role="alert"
      hidden
    ></p>
    <div class="form-actions form-wide">
      <button
        type="button"
        class="danger-btn"
        data-action="archive-product"
        hidden
      >
        Archive product</button
      ><button type="submit" class="primary-btn">Save product</button>
    </div>
  </form>
</template>

<!-- Customers -->
<template id="customers-template">
  <div
    data-motion='{"initial":{"opacity":0,"y":10},"animate":{"opacity":1,"y":0},"viewport":false}'
  >
    <p class="text-sm text-zinc-500">Customer records</p>
    <h2 class="mt-1 font-display text-3xl font-semibold">Customers</h2>
    <label class="input-shell mt-7"
      ><input
        class="w-full bg-transparent py-3 text-sm outline-none"
        placeholder="Search customers"
        aria-label="Search customers"
        data-field="customer-query"
    /></label>
    <div class="surface-card mt-7 overflow-hidden">
      <div
        class="grid gap-px bg-zinc-200 dark:bg-white/10 sm:grid-cols-2 xl:grid-cols-3"
        data-field="customers"
      ></div>
    </div>
  </div>
</template>

<!-- Customer -->
<template id="customer-template">
  <div class="bg-white p-5 dark:bg-panel">
    <div class="flex items-center gap-3">
      <div
        class="grid h-11 w-11 place-items-center rounded-full bg-zinc-100 text-sm font-bold dark:bg-white/5"
        data-field="initials"
      ></div>
      <div>
        <p class="text-sm font-semibold" data-field="customer"></p>
        <p class="text-[10px] text-zinc-500" data-field="email"></p>
      </div>
    </div>
    <div
      class="mt-5 flex justify-between border-t border-zinc-100 pt-4 text-xs dark:border-white/5"
    >
      <span class="text-zinc-500" data-field="order"></span>
      <span class="font-semibold" data-field="amount"></span>
    </div>
  </div>
</template>

<!-- Settings -->
<template id="settings-template">
  <section class="surface-card settings-panel">
    <p class="section-label">Store preferences</p>
    <h2 class="mt-3 font-display text-3xl font-semibold">Settings</h2>
    <form method="post" class="stack-form mt-7" data-form="settings">
      <label
        >Store name<input
          name="store_name"
          minlength="2"
          maxlength="100"
          required /></label
      ><label
        >Support email<input
          name="support_email"
          type="email"
          maxlength="254"
          required
      /></label>
      <p class="form-error" data-field="form-error" role="alert" hidden></p>
      <button class="primary-btn" type="submit">Save settings</button>
    </form>
    <div class="settings-security">
      <h3 class="font-semibold">Your administrator account</h3>
      <p class="form-hint mt-2">Update your profile or change your password.</p>
      <button class="secondary-btn mt-4" data-action="admin-account">
        Manage account
      </button>
    </div>
  </section>
</template>

<!-- Notifications -->
<template id="notifications-template">
  <div>
    <p class="form-hint">Inventory and order alerts for your store.</p>
    <ul class="notification-list" data-field="alerts"></ul>
  </div>
</template>

<!-- Order Status -->
<template id="order-status-template">
  <form method="post" class="stack-form mt-6">
    <label>Update order status<select name="status" required></select></label>
    <p class="form-hint">
      Cancelled and refunded orders return their items to inventory. Refund
      status records an offline refund; it does not transfer money.
    </p>
    <p class="form-error" data-field="form-error" role="alert" hidden></p>
    <button type="submit" class="primary-btn">Update order</button>
  </form>
</template>

<!-- Sidebar Backdrop -->
<template id="sidebar-backdrop-template">
  <button
    data-action="close-sidebar"
    class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
    data-motion='{"initial":{"opacity":0},"animate":{"opacity":1}}'
  ></button>
</template>
{% endblock %}

```

## templates/auth/auth.html

```html
{% extends "shared/base.html" %} {% block content %}
<div
  class="auth-page grid min-h-screen bg-stone-50 dark:bg-ink lg:grid-cols-[1.03fr_.97fr]"
>
  <div class="auth-art relative hidden overflow-hidden bg-zinc-950 lg:block">
    <img
      src="{{ url_for('static', filename='images/guitar_performance.jpg') }}"
      alt="Guitarist on stage"
      class="absolute inset-0 h-full w-full object-cover opacity-70"
      data-motion='{"initial":{"scale":1.08},"animate":{"scale":1},"transition":{"duration":1.3,"ease":[0.22,1,0.36,1]},"viewport":false}'
    />
    <div
      class="absolute inset-0 bg-gradient-to-t from-black via-black/15 to-black/30"
    ></div>
    <div
      class="relative flex h-full flex-col justify-between p-12 text-white xl:p-16"
    >
      <button
        class="audia-mark flex items-center text-left text-2xl"
        aria-label="Go to AUDIA home"
        data-action="home"
      >
        <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
      </button>
      <div class="max-w-xl">
        <p
          class="text-[10px] font-semibold uppercase tracking-[.2em] text-white/55"
        >
          AUDIA member access
        </p>
        <h1
          class="mt-5 font-display text-5xl font-semibold leading-[1.03] tracking-[-.04em] xl:text-6xl"
        >
          Your next guitar is closer than you think.
        </h1>
        <p class="mt-6 max-w-lg leading-7 text-white/65">
          Save instruments, keep your Guitar Finder results, review purchases,
          and track every delivery from one account.
        </p>
        <div class="mt-9 flex gap-7 text-xs text-white/65">
          <span class="flex items-center gap-2"
            ><svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-check text-acid"
              aria-hidden="true"
            >
              <path d="M20 6 9 17l-5-5"></path>
            </svg>
            Saved gear</span
          >
          <span class="flex items-center gap-2"
            ><svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-check text-acid"
              aria-hidden="true"
            >
              <path d="M20 6 9 17l-5-5"></path>
            </svg>
            Order history</span
          >
          <span class="flex items-center gap-2"
            ><svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-check text-acid"
              aria-hidden="true"
            >
              <path d="M20 6 9 17l-5-5"></path>
            </svg>
            Faster checkout</span
          >
        </div>
      </div>
      <p class="text-xs text-white/40">AUDIA — Find Your Sound.</p>
    </div>
  </div>
  <div class="auth-panel flex min-h-screen flex-col">
    <header class="flex items-center justify-between p-5 sm:p-8">
      <button class="secondary-btn px-4 py-2.5" data-action="store">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-arrow-left"
          aria-hidden="true"
        >
          <path d="m12 19-7-7 7-7"></path>
          <path d="M19 12H5"></path>
        </svg>
        Back to store
      </button>
      <button
        class="theme-toggle relative flex items-center rounded-full border border-zinc-200 bg-white text-zinc-700 shadow-sm transition hover:border-zinc-300 dark:border-white/10 dark:bg-white/[.05] dark:text-zinc-200 h-10 w-10 justify-center"
        aria-label="Switch to light mode"
        title="Switch to light mode"
        data-action="theme"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-sun"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="4"></circle>
          <path d="M12 2v2"></path>
          <path d="M12 20v2"></path>
          <path d="m4.93 4.93 1.41 1.41"></path>
          <path d="m17.66 17.66 1.41 1.41"></path>
          <path d="M2 12h2"></path>
          <path d="M20 12h2"></path>
          <path d="m6.34 17.66-1.41 1.41"></path>
          <path d="m19.07 4.93-1.41 1.41"></path>
        </svg>
      </button>
    </header>
    <div
      class="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 pb-14 sm:px-8"
    >
      <div class="mb-9 lg:hidden">
        <button
          class="audia-mark flex items-center text-left text-2xl"
          aria-label="Go to AUDIA home"
          data-action="home"
        >
          <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
        </button>
      </div>
      <div
        data-motion='{"initial":{"opacity":0,"y":12},"animate":{"opacity":1,"y":0},"transition":{"duration":0.35},"viewport":false}'
      >
        <p class="section-label">Secure account access</p>
        <h1
          class="mt-3 font-display text-4xl font-semibold tracking-tight"
          data-field="auth-title"
        >
          Welcome to AUDIA.
        </h1>
        <p
          class="mt-3 text-sm leading-6 text-zinc-500"
          data-field="auth-subtitle"
        >
          Sign in to continue as a customer or open the store administration
          workspace.
        </p>
      </div>
      <div
        data-field="roles"
        class="mt-8 grid grid-cols-2 rounded-2xl bg-zinc-100 p-1.5 dark:bg-white/[.055]"
      >
        <button
          class="flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white"
          data-action="role-customer"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-user-round"
            aria-hidden="true"
          >
            <circle cx="12" cy="8" r="5"></circle>
            <path d="M20 21a8 8 0 0 0-16 0"></path>
          </svg>
          Customer
        </button>
        <button
          class="flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition text-zinc-500"
          data-action="role-admin"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shield-check"
            aria-hidden="true"
          >
            <path
              d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
            ></path>
            <path d="m9 12 2 2 4-4"></path>
          </svg>
          Administrator
        </button>
      </div>
      <form method="post" class="mt-7 space-y-5" data-form="auth">
        <label class="block" data-field="name-wrap" hidden
          ><span class="mb-2 block text-xs font-semibold">Full name</span
          ><span class="input-shell rounded-xl px-4"
            ><input
              class="w-full bg-transparent py-3.5 text-sm outline-none"
              autocomplete="name"
              maxlength="100"
              minlength="2"
              data-field="name" /></span
        ></label>
        <label class="block" data-field="email-wrap">
          <span class="mb-2 block text-xs font-semibold">Email address</span>
          <span class="input-shell rounded-xl px-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-mail"
              aria-hidden="true"
            >
              <path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"></path>
              <rect x="2" y="4" width="20" height="16" rx="2"></rect>
            </svg>
            <input
              required=""
              type="email"
              class="w-full bg-transparent py-3.5 text-sm outline-none"
              autocomplete="email"
              maxlength="254"
              data-field="email"
            />
          </span>
        </label>
        <label class="block" data-field="password-wrap">
          <span class="mb-2 block text-xs font-semibold">Password</span>
          <span class="input-shell rounded-xl px-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-lock-keyhole"
              aria-hidden="true"
            >
              <circle cx="12" cy="16" r="1"></circle>
              <rect x="3" y="10" width="18" height="12" rx="2"></rect>
              <path d="M7 10V7a5 5 0 0 1 10 0v3"></path>
            </svg>
            <input
              required=""
              type="password"
              class="w-full bg-transparent py-3.5 text-sm outline-none"
              autocomplete="current-password"
              maxlength="128"
              data-field="password"
            />
            <button
              type="button"
              class="text-zinc-500"
              aria-label="Show password"
              data-action="password"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-eye"
                aria-hidden="true"
              >
                <path
                  d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"
                ></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
          </span>
        </label>
        <label class="block" data-field="confirm-wrap" hidden
          ><span class="mb-2 block text-xs font-semibold">Confirm password</span
          ><span class="input-shell rounded-xl px-4"
            ><input
              type="password"
              autocomplete="new-password"
              maxlength="128"
              class="w-full bg-transparent py-3.5 text-sm outline-none"
              data-field="confirm" /></span
        ></label>
        <p class="form-hint" data-field="password-hint" hidden>
          Use at least 10 characters. A longer, unique passphrase works well.
        </p>
        <div
          class="flex items-center justify-between text-xs"
          data-field="login-options"
        >
          <label class="flex items-center gap-2 text-zinc-500"
            ><input
              type="checkbox"
              class="range-acid"
              checked=""
              data-field="remember"
            />
            Remember me</label
          >
          <button
            type="button"
            class="font-semibold hover:underline"
            data-action="forgot"
          >
            Forgot password?
          </button>
        </div>
        <p
          class="rounded-xl bg-rose-50 px-4 py-3 text-xs text-rose-600 dark:bg-rose-500/10 dark:text-rose-300"
          role="alert"
          hidden=""
          data-field="login-error"
        ></p>
        <p
          class="form-success"
          role="status"
          hidden
          data-field="auth-success"
        ></p>
        <button
          type="submit"
          class="primary-btn w-full py-4"
          data-field="login-submit"
        >
          Sign in
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-arrow-right"
            aria-hidden="true"
          >
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        </button>
      </form>
      <button
        class="mt-6 text-sm font-semibold"
        data-action="back-login"
        data-field="back-login"
        hidden
      >
        Back to sign in
      </button>
      <p class="mt-7 text-center text-xs text-zinc-500" data-field="signup">
        New to AUDIA?
        <button
          class="font-semibold text-zinc-950 hover:underline dark:text-white"
          data-action="register"
        >
          Create an account
        </button>
      </p>
    </div>
  </div>
</div>
{% endblock %}

```

## templates/catalog/storefront.html

```html
{% extends "shared/base.html" %} {% block content %}
<div class="storefront min-h-screen overflow-x-clip">
  <div
    class="announcement px-5 py-2.5 text-center font-semibold uppercase tracking-[.18em]"
  >
    Free nationwide delivery over ₱15,000
    <span class="mx-2 opacity-40">•</span> Professional setup included
  </div>
  <header
    class="store-header sticky top-0 z-40 border-b border-zinc-200/80 bg-stone-50/90 backdrop-blur-xl dark:border-white/10 dark:bg-ink/90"
  >
    <div class="shell flex h-[76px] items-center justify-between">
      <button
        class="audia-mark flex items-center text-left text-lg"
        aria-label="Go to AUDIA home"
        data-action="home"
      >
        <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
      </button>
      <nav
        class="hidden items-center gap-8 text-sm font-medium text-zinc-600 dark:text-zinc-400 lg:flex"
      >
        <a class="nav-link" href="#shop">Shop</a>
        <a class="nav-link" href="#categories">Guitars</a>
        <button class="nav-link flex items-center gap-2" data-action="finder">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-compass"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path
              d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
            ></path>
          </svg>
          Guitar finder
        </button>
        <a class="nav-link" href="#bundles">Bundles</a>
        <a class="nav-link" href="#track">Track order</a>
      </nav>
      <div class="flex items-center gap-1.5">
        <button
          class="theme-toggle relative flex items-center rounded-full border border-zinc-200 bg-white text-zinc-700 shadow-sm transition hover:border-zinc-300 dark:border-white/10 dark:bg-white/[.05] dark:text-zinc-200 h-10 w-10 justify-center"
          aria-label="Switch to light mode"
          title="Switch to light mode"
          data-action="theme"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-sun"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2"></path>
            <path d="M12 20v2"></path>
            <path d="m4.93 4.93 1.41 1.41"></path>
            <path d="m17.66 17.66 1.41 1.41"></path>
            <path d="M2 12h2"></path>
            <path d="M20 12h2"></path>
            <path d="m6.34 17.66-1.41 1.41"></path>
            <path d="m19.07 4.93-1.41 1.41"></path>
          </svg>
        </button>
        <button class="icon-btn" aria-label="Search" data-action="search">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-search"
            aria-hidden="true"
          >
            <path d="m21 21-4.34-4.34"></path>
            <circle cx="11" cy="11" r="8"></circle>
          </svg>
        </button>
        <button
          class="icon-btn hidden sm:grid"
          aria-label="Sign in"
          data-action="account"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-circle-user-round"
            aria-hidden="true"
          >
            <path d="M17.925 20.056a6 6 0 0 0-11.851.001"></path>
            <circle cx="12" cy="11" r="4"></circle>
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
        </button>
        <button
          class="icon-btn relative"
          aria-label="Open cart"
          data-action="cart"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shopping-bag"
            aria-hidden="true"
          >
            <path d="M16 10a4 4 0 0 1-8 0"></path>
            <path d="M3.103 6.034h17.794"></path>
            <path
              d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
            ></path>
          </svg>
        </button>
        <button
          class="icon-btn lg:hidden"
          aria-label="Open menu"
          data-action="menu"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-menu"
            aria-hidden="true"
          >
            <path d="M4 5h16"></path>
            <path d="M4 12h16"></path>
            <path d="M4 19h16"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>
  {% include 'shared/practice_links.html' %}
  <main>
    <section
      id="top"
      class="hero-section relative overflow-hidden border-b border-zinc-200 dark:border-white/10"
    >
      <div aria-hidden="true" class="hero-mesh absolute inset-0"></div>
      <div
        class="shell hero-layout relative grid items-center gap-12 py-16 lg:grid-cols-[1.05fr_1fr] lg:py-10"
      >
        <div
          class="hero-copy relative z-10 max-w-xl"
          data-motion='{"initial":{"opacity":0,"y":32},"animate":{"opacity":1,"y":0},"transition":{"duration":0.8,"ease":[0.22,1,0.36,1]},"viewport":false}'
        >
          <p class="section-label hero-eyebrow">
            <span class="status-dot" aria-hidden="true"></span> The 2026
            electric edit
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-up-right"
              aria-hidden="true"
            >
              <path d="M7 7h10v10"></path>
              <path d="M7 17 17 7"></path>
            </svg>
          </p>
          <h1
            class="mt-5 font-display text-[clamp(3.4rem,7.5vw,7rem)] font-semibold leading-[.88] tracking-[-.065em]"
          >
            Make some<br /><span class="hero-gradient">noise.</span>
          </h1>
          <p
            class="mt-7 max-w-lg text-base leading-7 text-zinc-600 dark:text-zinc-400 sm:text-lg"
          >
            Discover guitars chosen for feel, tone, and lasting value. Compare
            the details, listen to a preview, and find an instrument you’ll keep
            reaching for.
          </p>
          <div class="mt-9 flex flex-col gap-3 sm:flex-row">
            <a href="#shop" class="primary-btn"
              >Shop guitars
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-arrow-right"
                aria-hidden="true"
              >
                <path d="M5 12h14"></path>
                <path d="m12 5 7 7-7 7"></path></svg
            ></a>
            <button class="secondary-btn" data-action="finder">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-compass"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <path
                  d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
                ></path>
              </svg>
              Find my guitar
            </button>
          </div>
          <div
            class="hero-stats mt-12 grid grid-cols-3 border-t border-zinc-200 pt-6 dark:border-white/10"
          >
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                120+
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                instruments
              </div>
            </div>
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                4.9
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                buyer rating
              </div>
            </div>
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                2-year
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                warranty
              </div>
            </div>
          </div>
        </div>
        <div
          class="hero-visual relative"
          data-motion='{"initial":{"opacity":0,"scale":0.96},"animate":{"opacity":1,"scale":1},"transition":{"duration":1,"delay":0.12,"ease":[0.22,1,0.36,1]},"viewport":false}'
        >
          <div class="sound-orbit orbit-one" aria-hidden="true"></div>
          <div class="sound-orbit orbit-two" aria-hidden="true"></div>
          <div class="hero-photo absolute overflow-hidden bg-zinc-900">
            <img
              class="h-full w-full object-cover object-center transition duration-1000 hover:scale-[1.025]"
              src="{{ url_for('static', filename='images/guitar_front.jpg') }}"
              alt="Guitars and amplifiers in a studio"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-black/5"
            ></div>
            <div
              class="hero-photo-caption absolute bottom-6 left-6 right-6 flex items-end justify-between gap-3 text-white sm:left-8 sm:right-8"
            >
              <div>
                <p
                  class="text-[10px] font-semibold uppercase tracking-[.18em] text-white/60"
                >
                  Featured sound
                </p>
                <h2 class="mt-2 font-display text-2xl font-semibold">
                  Midnight Drive
                </h2>
                <p class="mt-1 text-xs text-white/60">
                  Warm humbuckers · crisp overdrive
                </p>
              </div>
              <button
                class="h-11 gap-2 px-4 inline-flex items-center justify-center rounded-full bg-white text-zinc-950 shadow-lg transition hover:scale-105"
                aria-label="Play guitar tone"
                data-action="sound"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-play"
                  aria-hidden="true"
                >
                  <path
                    d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"
                  ></path>
                </svg>
                <span class="text-xs font-semibold">Hear the tone</span>
              </button>
            </div>
          </div>
          <div
            class="setup-note absolute right-0 top-3 rounded-2xl border border-zinc-200 bg-white p-4 shadow-xl dark:border-white/10 dark:bg-zinc-900 sm:right-1 sm:top-12"
          >
            <div class="flex items-center gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-guitar"
                aria-hidden="true"
              >
                <path d="m11.9 12.1 4.514-4.514"></path>
                <path
                  d="M20.1 2.3a1 1 0 0 0-1.4 0l-1.114 1.114A2 2 0 0 0 17 4.828v1.344a2 2 0 0 1-.586 1.414A2 2 0 0 1 17.828 7h1.344a2 2 0 0 0 1.414-.586L21.7 5.3a1 1 0 0 0 0-1.4z"
                ></path>
                <path d="m6 16 2 2"></path>
                <path
                  d="M8.23 9.85A3 3 0 0 1 11 8a5 5 0 0 1 5 5 3 3 0 0 1-1.85 2.77l-.92.38A2 2 0 0 0 12 18a4 4 0 0 1-4 4 6 6 0 0 1-6-6 4 4 0 0 1 4-4 2 2 0 0 0 1.85-1.23z"
                ></path>
              </svg>
              <div>
                <p class="text-xs font-semibold">Free setup</p>
                <p class="mt-0.5 text-[10px] text-zinc-500">
                  Ready to play on arrival
                </p>
              </div>
            </div>
          </div>
          <div class="sound-signature" aria-hidden="true">
            <span class="sound-signature-icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-volume2 lucide-volume-2"
                aria-hidden="true"
              >
                <path
                  d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"
                ></path>
                <path d="M16 9a5 5 0 0 1 0 6"></path>
                <path d="M19.364 18.364a9 9 0 0 0 0-12.728"></path>
              </svg>
            </span>
            <div>
              <span class="sound-signature-label">Find your frequency</span>
              <div class="sound-wave">
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
              </div>
            </div>
            <span class="sound-signature-type">100% YOU</span>
          </div>
        </div>
      </div>
      <div class="hero-bottom">
        <div class="shell flex flex-wrap items-center justify-between gap-4">
          <span>GOOD GEAR. GREAT POSSIBILITIES.</span>
          <span class="flex items-center gap-2"
            ><span class="status-dot" aria-hidden="true"></span> Your sound
            starts here
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-right"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path></svg
          ></span>
        </div>
      </div>
    </section>
    <section id="categories" class="shell py-24 sm:py-28">
      <div
        class="mb-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div>
          <p class="section-label">Browse the collection</p>
          <h2 class="section-title">Choose your voice.</h2>
        </div>
        <p class="max-w-sm text-sm leading-6 text-zinc-500">
          Start with the instrument family that fits the sound in your head.
        </p>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Electric"
          >
            <img
              src="{{ url_for('static', filename='images/electric_studio.jpg') }}"
              alt="Electric guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  01 · <span data-category-count="Electric">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Electric
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.07,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Acoustic"
          >
            <img
              src="{{ url_for('static', filename='images/acoustic_studio.jpg') }}"
              alt="Acoustic guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  02 · <span data-category-count="Acoustic">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Acoustic
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.14,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Classical"
          >
            <img
              src="{{ url_for('static', filename='images/classical_studio.jpg') }}"
              alt="Classical guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  03 · <span data-category-count="Classical">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Classical
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.21000000000000002,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Bass"
          >
            <img
              src="{{ url_for('static', filename='images/bass_studio.jpg') }}"
              alt="Bass guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  04 · <span data-category-count="Bass">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">Bass</h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
      </div>
    </section>
    <section
      id="shop"
      class="border-y border-zinc-200 bg-white py-24 dark:border-white/10 dark:bg-[#0c0c0f] sm:py-28"
    >
      <div class="shell">
        <div
          class="flex flex-col justify-between gap-7 lg:flex-row lg:items-end"
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <div>
            <p class="section-label">Curated instruments</p>
            <h2 class="section-title">Guitars worth playing.</h2>
            <p class="form-hint mt-3">
              School project catalog: illustrative brands, prices and stock.
            </p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row">
            <label class="input-shell min-w-[270px]">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-search"
                aria-hidden="true"
              >
                <path d="m21 21-4.34-4.34"></path>
                <circle cx="11" cy="11" r="8"></circle>
              </svg>
              <input
                class="w-full bg-transparent py-3 text-sm outline-none"
                placeholder="Search guitars or brands"
                aria-label="Search guitars or brands"
                value=""
                data-field="search"
              />
            </label>
            <label class="input-shell">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-sliders-horizontal"
                aria-hidden="true"
              >
                <path d="M10 5H3"></path>
                <path d="M12 19H3"></path>
                <path d="M14 3v4"></path>
                <path d="M16 17v4"></path>
                <path d="M21 12h-9"></path>
                <path d="M21 19h-5"></path>
                <path d="M21 5h-7"></path>
                <path d="M8 10v4"></path>
                <path d="M8 12H3"></path>
              </svg>
              <select
                class="appearance-none bg-transparent py-3 pr-4 text-sm outline-none"
                data-field="sort"
                aria-label="Sort instruments"
              >
                <option selected="">Featured</option>
                <option>Price: low</option>
                <option>Price: high</option>
                <option>Rating</option>
              </select>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-chevron-down"
                aria-hidden="true"
              >
                <path d="m6 9 6 6 6-6"></path>
              </svg>
            </label>
          </div>
        </div>
        <div class="mt-8 flex gap-2 overflow-x-auto pb-2">
          <button
            class="filter-chip filter-chip-active"
            data-action="filter"
            data-category="All"
          >
            All
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Electric"
          >
            Electric
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Acoustic"
          >
            Acoustic
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Classical"
          >
            Classical
          </button>
          <button class="filter-chip" data-action="filter" data-category="Bass">
            Bass
          </button>
        </div>
        <div
          class="mt-9 grid gap-x-5 gap-y-12 sm:grid-cols-2 lg:grid-cols-3"
          data-field="products"
        ></div>
        <div
          class="mt-9 rounded-2xl border border-dashed border-zinc-300 py-20 text-center text-sm text-zinc-500 dark:border-white/15"
          hidden=""
          data-field="no-products"
        >
          No guitar matches that search.
        </div>
      </div>
    </section>
    <section class="shell py-24 sm:py-28">
      <div
        class=""
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div
          class="finder-banner relative overflow-hidden rounded-[2rem] bg-zinc-950 px-7 py-16 text-white dark:bg-gradient-to-br dark:from-[#1c1330] dark:via-zinc-950 dark:to-zinc-950 sm:px-12 lg:px-20 lg:py-20"
        >
          <div
            class="absolute -right-28 -top-28 h-80 w-80 rounded-full bg-violet-500/25 blur-[100px]"
          ></div>
          <div
            class="relative grid items-center gap-12 lg:grid-cols-[1fr_.72fr]"
          >
            <div>
              <p
                class="text-[10px] font-semibold uppercase tracking-[.2em] text-acid"
              >
                Guitar finder
              </p>
              <h2
                class="mt-4 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl"
              >
                Four questions.<br />A much better shortlist.
              </h2>
              <p class="mt-5 max-w-xl leading-7 text-zinc-400">
                Choose your budget, experience, preferred style, and guitar
                type. AUDIA will narrow the catalog to practical matches.
              </p>
              <button class="primary-btn mt-8" data-action="finder">
                Start guitar finder
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-compass"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <path
                    d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
                  ></path>
                </svg>
              </button>
            </div>
            <div
              class="finder-profile rounded-3xl border border-white/10 bg-white/[.055] p-6 backdrop-blur"
            >
              <p
                class="text-xs font-semibold uppercase tracking-[.16em] text-zinc-500"
              >
                Example profile
              </p>
              <div class="mt-6 divide-y divide-white/10">
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Budget</span>
                  <span class="font-medium">₱10k – ₱20k</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Experience</span>
                  <span class="font-medium">Beginner</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Genre</span>
                  <span class="font-medium">Rock</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Type</span>
                  <span class="font-medium">Electric</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section id="bundles" class="shell pb-24 sm:pb-28">
      <div
        class="grid overflow-hidden rounded-[2rem] border border-zinc-200 bg-white shadow-sm dark:border-white/10 dark:bg-panel lg:grid-cols-2"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div class="relative min-h-[430px] overflow-hidden">
          <img
            src="{{ url_for('static', filename='images/electric_studio.jpg') }}"
            alt="Electric guitar beside a practice amplifier"
            class="absolute inset-0 h-full w-full object-cover transition duration-1000 hover:scale-105"
          />
          <span
            class="absolute left-6 top-6 rounded-full bg-white px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-zinc-950"
            >Save ₱3,500</span
          >
        </div>
        <div class="flex flex-col justify-center p-8 sm:p-12 lg:p-16">
          <p class="section-label">Complete starter rig</p>
          <h2 class="mt-3 font-display text-4xl font-semibold">
            Everything after the guitar.
          </h2>
          <p class="mt-4 leading-7 text-zinc-500">
            A matched practice amp, padded bag, cable, tuner, strap, picks, and
            a professional setup—ready from day one.
          </p>
          <div class="mt-7 grid grid-cols-2 gap-3 text-sm">
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              15W practice amp
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Padded gig bag
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Clip-on tuner
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Cable + strap
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Assorted picks
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Free setup
            </div>
          </div>
          <div class="mt-8 flex items-end gap-3">
            <span class="font-display text-3xl font-semibold">₱19,990</span>
            <span class="pb-1 text-sm text-zinc-500 line-through">₱23,490</span>
          </div>
          <button class="primary-btn mt-7 self-start" data-action="bundle">
            View the bundle
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-right"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </section>
    <section
      id="track"
      class="border-y border-zinc-200 bg-zinc-100 py-24 dark:border-white/10 dark:bg-white/[.02]"
    >
      <div
        class="shell grid gap-12 lg:grid-cols-[.72fr_1.28fr] lg:items-center"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div>
          <p class="section-label">Delivery updates</p>
          <h2 class="section-title">Know where it is.</h2>
          <p class="mt-4 leading-7 text-zinc-500">
            Enter your order number to see its current status and estimated
            delivery.
          </p>
          <div class="input-shell mt-7 max-w-md p-1.5 pl-5">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-search"
              aria-hidden="true"
            >
              <path d="m21 21-4.34-4.34"></path>
              <circle cx="11" cy="11" r="8"></circle>
            </svg>
            <input
              placeholder="Enter your order number"
              aria-label="Order number"
              class="min-w-0 flex-1 bg-transparent py-2 text-sm outline-none"
              value=""
              data-field="order"
            />
            <button
              class="rounded-full bg-zinc-950 px-5 py-2.5 text-xs font-bold text-white dark:bg-white dark:text-zinc-950"
              data-action="track"
            >
              Track
            </button>
          </div>
        </div>
        <div class="surface-card p-6 sm:p-8">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-zinc-500">Order</p>
              <p class="mt-1 font-semibold">Example delivery journey</p>
            </div>
            <span
              class="rounded-full bg-blue-100 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-blue-700 dark:bg-blue-400/10 dark:text-blue-300"
              >In transit</span
            >
          </div>
          <div class="mt-10 grid grid-cols-4">
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid dark:text-ink"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-package-check"
                  aria-hidden="true"
                >
                  <path d="M12 22V12"></path>
                  <path d="m16 17 2 2 4-4"></path>
                  <path
                    d="M21 11.127V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.729l7 4a2 2 0 0 0 2 .001l1.32-.753"
                  ></path>
                  <path d="M3.29 7 12 12l8.71-5"></path>
                  <path d="m7.5 4.27 8.997 5.148"></path>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-950 dark:bg-acid"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Processing
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid dark:text-ink"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-truck"
                  aria-hidden="true"
                >
                  <path
                    d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"
                  ></path>
                  <path d="M15 18H9"></path>
                  <path
                    d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"
                  ></path>
                  <circle cx="17" cy="18" r="2"></circle>
                  <circle cx="7" cy="18" r="2"></circle>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-950 dark:bg-acid"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Shipped
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-200 bg-white text-zinc-400 dark:border-white/10 dark:bg-panel"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-right"
                  aria-hidden="true"
                >
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-200 dark:bg-white/10"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Out for delivery
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-200 bg-white text-zinc-400 dark:border-white/10 dark:bg-panel"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-check"
                  aria-hidden="true"
                >
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
              </div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Delivered
              </p>
            </div>
          </div>
          <div
            class="mt-7 flex justify-between border-t border-zinc-200 pt-5 text-xs dark:border-white/10"
          >
            <span class="text-zinc-500">Estimated arrival</span>
            <span class="font-semibold">Thursday, Sep 10</span>
          </div>
        </div>
      </div>
    </section>
    <div class="shell grid gap-4 py-14 sm:grid-cols-3">
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-shield-check"
          aria-hidden="true"
        >
          <path
            d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
          ></path>
          <path d="m9 12 2 2 4-4"></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Authentic gear</p>
          <p class="mt-1 text-xs text-zinc-500">
            Official products with warranty
          </p>
        </div>
      </div>
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-volume2 lucide-volume-2"
          aria-hidden="true"
        >
          <path
            d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"
          ></path>
          <path d="M16 9a5 5 0 0 1 0 6"></path>
          <path d="M19.364 18.364a9 9 0 0 0 0-12.728"></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Hear before buying</p>
          <p class="mt-1 text-xs text-zinc-500">Tone previews on key models</p>
        </div>
      </div>
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-headphones"
          aria-hidden="true"
        >
          <path
            d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"
          ></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Player-first support</p>
          <p class="mt-1 text-xs text-zinc-500">Help choosing and setting up</p>
        </div>
      </div>
    </div>
  </main>
  <footer
    class="border-t border-zinc-200 bg-white pt-16 dark:border-white/10 dark:bg-ink"
  >
    <div
      class="shell grid gap-12 pb-14 sm:grid-cols-2 lg:grid-cols-[1.4fr_repeat(3,1fr)]"
    >
      <div>
        <button
          class="audia-mark flex items-center text-left text-lg"
          aria-label="Go to AUDIA home"
          data-action="home"
        >
          <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
        </button>
        <p class="mt-6 max-w-xs text-sm leading-6 text-zinc-500">
          A guitar-only marketplace helping players find, hear, compare, and
          purchase the right instrument.
        </p>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">Shop</h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Electric"
            >Electric guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Acoustic"
            >Acoustic guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Bass"
            >Bass guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Accessories"
            >Accessories</a
          >
        </div>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">
          Services
        </h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="finder"
            >Guitar finder</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Sound previews</a
          >
          <a
            href="#bundles"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Bundles</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="setup"
            >Professional setup</a
          >
        </div>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">
          Support
        </h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#track"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Order tracking</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="delivery"
            >Delivery &amp; returns</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="warranty"
            >Warranty</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="contact"
            >Contact us</a
          >
        </div>
      </div>
    </div>
    <div class="border-t border-zinc-200 dark:border-white/10">
      <div
        class="shell flex flex-col justify-between gap-3 py-6 text-[11px] text-zinc-500 sm:flex-row"
      >
        <span>© 2026 AUDIA Guitar Marketplace</span>
        <button
          class="hover:text-zinc-950 dark:hover:text-white"
          data-action="admin-login"
        >
          Admin portal
        </button>
      </div>
    </div>
  </footer>
  {% include 'chatbot/chatbot.html' %}
</div>
{% endblock %} {% block components %}
<!-- Related cards and dialogs live here with the page that uses them. -->

<!-- Product Card -->
<template id="product-card-template">
  <div
    class=""
    data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
  >
    <article class="product-card group">
      <div
        class="product-image relative aspect-[4/4.5] overflow-hidden rounded-[1.15rem] bg-zinc-100 dark:bg-zinc-900"
      >
        <img
          loading="lazy"
          decoding="async"
          src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
          alt="ELECTRIC_001"
          class="h-full w-full object-cover transition duration-700 group-hover:scale-[1.04]"
          data-field="image"
        />
        <span
          class="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1.5 text-[9px] font-bold uppercase tracking-[.12em] text-zinc-950 backdrop-blur"
          data-field="badge"
          >Amber Flame</span
        >
        <button
          class="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full bg-white/90 text-zinc-950 shadow-sm"
          aria-label="Save guitar"
          data-action="like"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-heart"
            aria-hidden="true"
          >
            <path
              d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"
            ></path>
          </svg>
        </button>
        <div class="absolute bottom-3 right-3">
          <button
            class="h-10 w-10 inline-flex items-center justify-center rounded-full bg-white text-zinc-950 shadow-lg transition hover:scale-105"
            aria-label="Play guitar tone"
            data-action="sound"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="currentColor"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-play"
              aria-hidden="true"
            >
              <path
                d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"
              ></path>
            </svg>
          </button>
        </div>
      </div>
      <div class="product-details px-1 pb-2 pt-5">
        <div
          class="flex items-center justify-between text-[10px] uppercase tracking-[.14em] text-zinc-500"
        >
          <span data-field="category">AUDIA Demo · Electric</span>
          <span class="flex items-center gap-1 normal-case tracking-normal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-star fill-amber-400 text-amber-400"
              aria-hidden="true"
            >
              <path
                d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"
              ></path>
            </svg>
            <span data-field="rating">0 (0)</span>
          </span>
        </div>
        <h3 class="mt-2 font-display text-lg font-semibold" data-field="name">
          ELECTRIC_001
        </h3>
        <p
          class="mt-2 min-h-[40px] text-xs leading-5 text-zinc-500"
          data-field="description"
        >
          Amber Flame single-cut electric with an amber figured finish and two
          covered pickups.
        </p>
        <div class="mt-5 flex items-center justify-between">
          <div>
            <p class="text-lg font-semibold" data-field="price">₱12,990</p>
            <p class="mt-0.5 text-[10px] text-zinc-500" data-field="stock">
              8 available
            </p>
          </div>
          <button
            class="grid h-11 w-11 place-items-center rounded-full bg-zinc-950 text-white transition hover:scale-105 dark:bg-acid dark:text-ink"
            aria-label="Add ELECTRIC_001 to cart"
            data-action="add"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-plus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="M12 5v14"></path>
            </svg>
          </button>
        </div>
      </div>
    </article>
  </div>
</template>

<!-- Mobile Nav -->
<template id="mobile-nav-template">
  <nav
    class="shell overflow-hidden border-t border-zinc-200 dark:border-white/10 lg:hidden"
    data-motion='{"initial":{"height":0,"opacity":0},"animate":{"height":"auto","opacity":1},"viewport":false}'
  >
    <div class="flex flex-col gap-1 py-4 text-sm">
      <a
        href="#shop"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Shop</a
      >
      <a
        href="#categories"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Guitars</a
      >
      <a
        href="#bundles"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Bundles</a
      >
      <a
        href="#track"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Track order</a
      >
      <button
        class="flex items-center gap-2 rounded-xl px-3 py-3 text-left"
        data-action="finder"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-compass"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <path
            d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
          ></path>
        </svg>
        Guitar finder
      </button>
      <button
        class="flex items-center gap-2 rounded-xl px-3 py-3 text-left"
        data-action="account"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-circle-user-round"
          aria-hidden="true"
        >
          <path d="M17.925 20.056a6 6 0 0 0-11.851.001"></path>
          <circle cx="12" cy="11" r="4"></circle>
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
        Sign in
      </button>
    </div>
  </nav>
</template>

<!-- Bundle Detail -->
<template id="bundle-detail-template">
  <div class="bundle-detail">
    <img class="bundle-image" data-field="image" alt="" />
    <p class="form-hint mt-5" data-field="description"></p>
    <div class="order-total mt-5">
      <span>Complete bundle</span><strong data-field="price"></strong>
    </div>
    <button class="primary-btn w-full" data-field="bundle-add">
      Add bundle to cart
    </button>
  </div>
</template>

<!-- Support Info -->
<template id="support-info-template">
  <div>
    <p class="form-hint" data-field="support-copy"></p>
    <p class="form-hint mt-5">
      Keep your order confirmation for reference. The store can help confirm the
      terms for your instrument.
    </p>
    <a
      class="secondary-btn mt-5"
      data-field="support-email"
      href="mailto:support@audia.ph"
      >Contact the store</a
    >
  </div>
</template>

<!-- Cart -->
<template id="cart-template">
  <div class="fixed inset-0 z-50">
    <button
      class="absolute inset-0 bg-black/55 backdrop-blur-sm"
      aria-label="Close cart"
      data-motion='{"initial":{"opacity":0},"animate":{"opacity":1},"viewport":false}'
      data-action="close-cart"
    ></button>
    <aside
      class="cart-panel absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-[#101014]"
      data-motion='{"initial":{"x":"100%"},"animate":{"x":0},"transition":{"type":"spring","stiffness":300,"damping":32},"viewport":false}'
    >
      <div
        class="flex items-center justify-between border-b border-zinc-200 px-6 py-5 dark:border-white/10"
      >
        <div class="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shopping-bag"
            aria-hidden="true"
          >
            <path d="M16 10a4 4 0 0 1-8 0"></path>
            <path d="M3.103 6.034h17.794"></path>
            <path
              d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
            ></path>
          </svg>
          <h2 class="font-display text-xl font-semibold">Your cart</h2>
          <span class="text-xs text-zinc-500" data-field="cart-count"
            >1 items</span
          >
        </div>
        <button class="icon-btn" data-action="close-cart">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-x"
            aria-hidden="true"
          >
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
          </svg>
        </button>
      </div>
      <div class="flex-1 overflow-y-auto p-6" data-field="cart-body"></div>
      <div
        class="border-t border-zinc-200 p-6 dark:border-white/10"
        data-field="cart-footer"
      >
        <div class="flex justify-between">
          <span class="text-sm text-zinc-500">Subtotal</span>
          <span class="font-display text-xl font-semibold" data-field="subtotal"
            >₱12,990</span
          >
        </div>
        <button class="primary-btn mt-5 w-full" data-action="checkout">
          Proceed to checkout
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shield-check"
            aria-hidden="true"
          >
            <path
              d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
            ></path>
            <path d="m9 12 2 2 4-4"></path>
          </svg>
        </button>
      </div>
    </aside>
  </div>
</template>

<!-- Cart Badge -->
<template id="cart-badge-template">
  <span
    class="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink"
  ></span>
</template>

<!-- Cart Empty -->
<template id="cart-empty-template">
  <div class="grid h-full place-items-center text-center">
    <div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="36"
        height="36"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="lucide lucide-shopping-bag mx-auto text-zinc-300 dark:text-zinc-700"
        aria-hidden="true"
      >
        <path d="M16 10a4 4 0 0 1-8 0"></path>
        <path d="M3.103 6.034h17.794"></path>
        <path
          d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
        ></path>
      </svg>
      <p class="mt-4 text-sm text-zinc-500">Your cart is empty.</p>
    </div>
  </div>
</template>

<!-- Cart Item -->
<template id="cart-item-template">
  <div class="flex gap-4">
    <img
      src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
      alt=""
      class="h-24 w-20 rounded-xl object-cover"
      data-field="image"
    />
    <div class="flex min-w-0 flex-1 flex-col">
      <p
        class="text-[10px] uppercase tracking-widest text-zinc-500"
        data-field="brand"
      >
        AUDIA Demo
      </p>
      <p class="mt-1 truncate text-sm font-semibold" data-field="name">
        ELECTRIC_001
      </p>
      <div class="mt-auto flex items-center justify-between">
        <span class="text-sm font-semibold" data-field="price">₱12,990</span>
        <div
          class="flex items-center gap-3 rounded-full border border-zinc-200 px-2 py-1 dark:border-white/10"
        >
          <button data-action="decrease">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-minus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
            </svg>
          </button>
          <span class="text-xs" data-field="quantity">1</span>
          <button data-action="increase">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-plus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="M12 5v14"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- Cart Items -->
<template id="cart-items-template">
  <div class="space-y-5"></div>
</template>

<!-- Checkout -->
<template id="checkout-template">
  <form method="post" class="stack-form" data-form="checkout">
    <p class="form-hint">
      Your instruments are reserved when you place your order. Pay with cash on
      delivery.
    </p>
    <label
      >Delivery address<textarea
        name="address"
        required
        minlength="10"
        maxlength="500"
        autocomplete="street-address"
        placeholder="House number, street, barangay, city, province, postal code"
      ></textarea></label
    ><label
      >Phone number<input
        name="phone"
        type="tel"
        required
        minlength="7"
        maxlength="30"
        autocomplete="tel"
    /></label>
    <div class="order-total">
      <span>Order total</span><strong data-field="checkout-total"></strong>
    </div>
    <p class="form-hint">
      Payment: cash on delivery. No online payment is collected.
    </p>
    <p class="form-error" role="alert" data-field="form-error" hidden></p>
    <button type="submit" class="primary-btn">Place order</button>
  </form>
</template>

<!-- Finder -->
<template id="finder-template">
  <div class="fixed inset-0 z-[60] grid place-items-center p-4">
    <button
      class="absolute inset-0 bg-black/65 backdrop-blur-md"
      aria-label="Close finder"
      data-motion='{"initial":{"opacity":0},"animate":{"opacity":1},"viewport":false}'
      data-action="close-finder"
    ></button>
    <div
      class="finder-modal relative w-full max-w-2xl overflow-hidden rounded-[2rem] bg-white shadow-2xl dark:bg-panel"
      data-motion='{"initial":{"opacity":0,"y":28,"scale":0.98},"animate":{"opacity":1,"y":0,"scale":1},"viewport":false}'
    >
      <div
        class="flex items-center justify-between border-b border-zinc-200 p-6 dark:border-white/10"
      >
        <div class="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-compass"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path
              d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
            ></path>
          </svg>
          <div>
            <p class="font-display font-semibold">AUDIA Guitar Finder</p>
            <p class="text-[10px] text-zinc-500">Four quick questions</p>
          </div>
        </div>
        <button class="icon-btn" data-action="close-finder">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-x"
            aria-hidden="true"
          >
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
          </svg>
        </button>
      </div>
      <div class="p-7 sm:p-10" data-field="finder-body">
        <div class="mb-8 flex gap-2" data-field="progress">
          <span class="h-1 flex-1 rounded-full bg-zinc-950 dark:bg-acid"></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
        </div>
        <p class="section-label" data-field="question-number">
          Question 1 of 4
        </p>
        <h2
          class="mt-3 font-display text-3xl font-semibold"
          data-field="question-title"
        >
          What is your budget?
        </h2>
        <div class="mt-10" data-field="budget">
          <div
            class="mb-7 text-center font-display text-4xl font-semibold"
            data-field="budget-value"
          >
            ₱20,000
          </div>
          <input
            type="range"
            min="8000"
            max="60000"
            step="1000"
            class="range-acid w-full"
            value="20000"
            data-field="budget-input"
          />
          <div class="mt-3 flex justify-between text-xs text-zinc-500">
            <span>₱8,000</span>
            <span>₱60,000</span>
          </div>
        </div>
        <div
          class="mt-9 grid gap-3 sm:grid-cols-2"
          data-field="options"
          hidden=""
        ></div>
        <button class="primary-btn mt-10 w-full" data-action="finder-next">
          Continue
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-arrow-right"
            aria-hidden="true"
          >
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<!-- Finder Results -->
<template id="finder-results-template">
  <div class="p-7 sm:p-10" data-field="finder-results">
    <p class="section-label">Recommended for you</p>
    <h2 class="mt-3 font-display text-3xl font-semibold">
      Your closest matches.
    </h2>
    <div class="mt-7 space-y-3" data-field="matches"></div>
    <button class="secondary-btn mt-6 w-full" data-action="finder-restart">
      Start again
    </button>
  </div>
</template>

<!-- Finder Match -->
<template id="finder-match-template">
  <div
    class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-3 dark:border-white/10"
  >
    <div class="relative">
      <img
        src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
        alt=""
        class="h-20 w-16 rounded-xl object-cover"
        data-field="image"
      />
      <span
        class="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink"
        data-field="rank"
        >1</span
      >
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold" data-field="name">
        ELECTRIC_001
      </p>
      <p class="mt-1 text-xs text-zinc-500" data-field="category">
        Electric · Beginner
      </p>
      <p class="mt-2 text-sm font-semibold" data-field="price">₱12,990</p>
    </div>
    <button
      class="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"
      data-action="add-match"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="lucide lucide-plus"
        aria-hidden="true"
      >
        <path d="M5 12h14"></path>
        <path d="M12 5v14"></path>
      </svg>
    </button>
  </div>
</template>

<!-- Finder Option -->
<template id="finder-option-template">
  <button
    class="rounded-2xl border p-5 text-left text-sm transition border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid"
    data-action="finder-option"
  ></button>
</template>

<!-- Check -->
<template id="check-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="15"
    height="15"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-check float-right"
    aria-hidden="true"
  >
    <path d="M20 6 9 17l-5-5"></path>
  </svg>
</template>

{% endblock %}

```

## templates/chatbot/chatbot.html

```html
<!-- Existing AUDI interface, shared by the public landing page and the shop. -->
<div data-chatbot>
  <button
    class="fixed bottom-5 right-5 z-40 grid h-14 w-14 place-items-center rounded-full bg-zinc-950 text-white shadow-2xl transition hover:scale-105 dark:bg-acid dark:text-ink"
    aria-label="Open customer support"
    data-action="chat"
    aria-expanded="false"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="21"
      height="21"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="lucide lucide-message-circle"
      aria-hidden="true"
    >
      <path
        d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"
      ></path>
    </svg>
  </button>
  <!-- Chat -->
  <template id="chat-template">
    <div
      class="chat-panel fixed bottom-24 right-4 z-40 flex h-[510px] w-[calc(100%-2rem)] max-w-sm flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-white/10 dark:bg-[#101014]"
      data-motion='{"initial":{"opacity":0,"y":20,"scale":0.97},"animate":{"opacity":1,"y":0,"scale":1},"viewport":false}'
    >
      <div
        class="flex items-center gap-3 border-b border-zinc-200 p-4 dark:border-white/10"
      >
        <div
          class="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-headphones"
            aria-hidden="true"
          >
            <path
              d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"
            ></path>
          </svg>
        </div>
        <div>
          <p class="font-display text-sm font-semibold">AUDI customer guide</p>
          <p class="text-[10px] text-zinc-500">Available now</p>
        </div>
      </div>
      <div
        class="flex-1 space-y-3 overflow-y-auto p-4"
        data-field="messages"
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
        aria-label="Conversation"
      ></div>
      <form
        method="post"
        class="flex gap-2 border-t border-zinc-200 p-3 dark:border-white/10"
        data-form="chat"
      >
        <input
          class="min-w-0 flex-1 rounded-full bg-zinc-100 px-4 text-xs outline-none dark:bg-white/[.06]"
          placeholder="Ask about a guitar"
          value=""
          data-field="chat-input"
          aria-label="Your message"
          maxlength="2000"
        />
        <button
          type="submit"
          aria-label="Send message"
          class="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-arrow-right"
            aria-hidden="true"
          >
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        </button>
      </form>
    </div>
  </template>

  <!-- Chat Suggestions -->
  <template id="chat-suggestions-template">
    <div class="flex flex-wrap gap-2">
      <button
        class="rounded-full border border-zinc-200 px-3 py-2 text-[10px] text-zinc-500 hover:border-zinc-500 dark:border-white/10"
        data-action="chat-suggestion"
      >
        Best guitar under ₱20k
      </button>
      <button
        class="rounded-full border border-zinc-200 px-3 py-2 text-[10px] text-zinc-500 hover:border-zinc-500 dark:border-white/10"
        data-action="chat-suggestion"
      >
        I am a beginner
      </button>
      <button
        class="rounded-full border border-zinc-200 px-3 py-2 text-[10px] text-zinc-500 hover:border-zinc-500 dark:border-white/10"
        data-action="chat-suggestion"
      >
        Acoustic or electric?
      </button>
    </div>
  </template>

  <!-- Message -->
  <template id="message-template">
    <div
      class="max-w-[86%] rounded-2xl px-4 py-3 text-xs leading-5 bg-zinc-100 dark:bg-white/[.07]"
      data-field="message"
    >
      Hi, I’m AUDI. Tell me your budget or the kind of music you want to play,
      and I’ll help narrow the options.
    </div>
  </template>
</div>

```

## templates/landing/landing.html

```html
{% extends "shared/base.html" %} {% block content %}
<div class="landing-page">
  <header class="landing-header">
    <div class="shell landing-nav">
      <a class="audia-mark" href="#welcome" aria-label="AUDIA home"
        ><span class="mark-a">A</span>UDI<span class="mark-a">A</span></a
      >
      <nav aria-label="About AUDIA">
        <a href="#about-audia">About</a>
        <a href="#guitar-families">Guitar families</a>
        <a href="#how-it-works">How it works</a>
      </nav>
      <div class="landing-nav-actions">
        <button
          class="landing-theme"
          data-action="theme"
          aria-label="Switch to light mode"
        ></button>
        <button class="secondary-btn" data-action="sign-in" data-auth-entry>
          Sign in
        </button>
        <button
          class="secondary-btn"
          data-action="browse"
          data-member-entry
          hidden
        >
          Browse guitars
        </button>
      </div>
    </div>
  </header>
  {% include 'shared/practice_links.html' %}
  <main>
    <section id="welcome" class="shell landing-hero">
      <div class="landing-hero-copy">
        <p class="section-label">Meet AUDIA</p>
        <h1>
          Your sound.<br /><span class="hero-gradient"
            >Your starting point.</span
          >
        </h1>
        <p>
          A place to discover guitars and find what fits your music. AUDIA
          brings instrument details, guided recommendations, and a simple
          shopping experience together in one account.
        </p>
        <div class="landing-actions">
          <button class="primary-btn" data-action="register" data-auth-entry>
            Create an account <span aria-hidden="true">↗</span>
          </button>
          <button
            class="primary-btn"
            data-action="browse"
            data-member-entry
            hidden
          >
            Explore the catalog <span aria-hidden="true">↗</span>
          </button>
          <a class="landing-text-link" href="#about-audia"
            >Take a quick look <span aria-hidden="true">↓</span></a
          >
        </div>
        <p class="landing-access-note">
          Sign in to browse all instruments, save favorites, and shop.
        </p>
        <div class="landing-hero-details">
          <span>Four guitar families</span
          ><span>One place to find your sound</span>
        </div>
      </div>
      <figure class="landing-hero-photo">
        <img
          src="{{ url_for('static', filename='images/guitar_front.jpg') }}"
          alt="Acoustic guitar in a studio with instruments and amplifiers"
          fetchpriority="high"
        />
        <figcaption>
          <span>A little inspiration</span
          ><strong>Every player starts somewhere.</strong>
        </figcaption>
      </figure>
    </section>
    <section id="about-audia" class="landing-about">
      <div class="shell">
        <div class="landing-section-heading">
          <div>
            <p class="section-label">The system at a glance</p>
            <h2 class="section-title">
              Less guesswork.<br />More making music.
            </h2>
          </div>
          <p>
            Whether you are picking up your first guitar or exploring a
            different style, AUDIA helps you compare your options and keep your
            choices in one place.
          </p>
        </div>
        <div class="landing-features">
          <article>
            <span class="landing-step">01 / DISCOVER</span>
            <h3>Know what you are choosing.</h3>
            <p>
              See each instrument's photo, description, price, and availability.
              Browse by guitar family or search for a specific catalog code.
            </p>
          </article>
          <article>
            <span class="landing-step">02 / FIND YOUR FIT</span>
            <h3>A little guidance goes a long way.</h3>
            <p>
              Guitar Finder uses your budget, experience, and preferred guitar
              type to suggest instruments. Save the ones you want to revisit.
            </p>
          </article>
          <article>
            <span class="landing-step">03 / KEEP IT TOGETHER</span>
            <h3>From your shortlist to your doorstep.</h3>
            <p>
              Add instruments to your cart, check out with your delivery
              details, and follow your order status from your account.
            </p>
          </article>
        </div>
      </div>
    </section>
    <section id="guitar-families" class="shell landing-collections">
      <div class="landing-section-heading">
        <div>
          <p class="section-label">A quick introduction</p>
          <h2 class="section-title">Choose your voice.</h2>
        </div>
        <p>
          Get to know the four guitar families. Sign in when you are ready to
          explore individual instruments.
        </p>
      </div>
      <div class="landing-collection-grid">
        {% for category, caption, description in [ ('Electric', 'Plug into
        possibility.', 'Explore amplified sounds, effects, and styles from clean
        pop to rock.'), ('Acoustic', 'Let the song lead.', 'A familiar starting
        point for unplugged strumming and fingerpicking.'), ('Classical', 'Make
        room for the details.', 'Discover traditional shapes suited to classical
        and fingerstyle study.'), ('Bass', 'Give the music its pulse.', 'Build
        the low-end foundation and connect melody with rhythm.') ] %}
        <button
          class="landing-collection"
          data-action="browse"
          data-category="{{ category }}"
          aria-label="Explore {{ category|lower }} guitars"
        >
          <span class="landing-collection-photo">
            <img
              src="{{ url_for('static', filename='images/' ~ category|lower ~ '_studio.jpg') }}"
              alt="{{ category }} guitar in a studio"
              loading="lazy"
              decoding="async"
            />
            <span class="landing-collection-label"
              ><strong>{{ category }}</strong
              ><span aria-hidden="true">↗</span></span
            >
          </span>
          <span class="landing-collection-copy"
            ><strong>{{ caption }}</strong><span>{{ description }}</span></span
          >
        </button>
        {% endfor %}
      </div>
    </section>
    <section id="how-it-works" class="shell landing-how">
      <div>
        <p class="section-label">Your next step</p>
        <h2 class="section-title">A simple path<br />to your next guitar.</h2>
        <p class="landing-how-intro">
          Your account opens the full AUDIA experience.
        </p>
      </div>
      <ol class="landing-steps">
        <li>
          <span>01</span>
          <div>
            <h3>Create your account.</h3>
            <p>
              Sign up or sign in to unlock the catalog and your personal
              workspace.
            </p>
          </div>
        </li>
        <li>
          <span>02</span>
          <div>
            <h3>Explore and compare.</h3>
            <p>
              Browse guitar families, try Guitar Finder, and save your
              favorites.
            </p>
          </div>
        </li>
        <li>
          <span>03</span>
          <div>
            <h3>Shop when you are ready.</h3>
            <p>
              Add your selections to the cart, check out, and track your order.
            </p>
          </div>
        </li>
      </ol>
    </section>
    <section class="shell landing-join">
      <div>
        <p class="section-label">Find your sound</p>
        <h2 class="section-title">Ready to take a closer look?</h2>
        <p>The full collection is waiting inside.</p>
      </div>
      <button class="primary-btn" data-action="browse">
        Explore the catalog <span aria-hidden="true">↗</span>
      </button>
    </section>
  </main>
  <footer class="shell landing-footer">
    <a class="audia-mark" href="#welcome">AUDIA</a>
    <p>Discover. Compare. Find your sound.</p>
    <span>School project · Demo catalog</span>
  </footer>
  {% include 'chatbot/chatbot.html' %}
</div>
{% endblock %}

```

## templates/lessons/chord_detail.html

```html
{% extends "shared/practice_base.html" %}
{% from "lessons/_chord_diagram.html" import chord_diagram %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.chords') }}">← Chord library</a>
<div class="practice-heading"><p class="section-label">02 · Basic Chords</p><h1 class="section-title">{{ chord.name }}</h1><p>Make each string ring clearly before trying a full strum.</p></div>
<div class="chord-detail-layout">
  <section class="surface-card practice-card chord-detail-diagram" aria-label="Chord shape"><h2>{{ chord.symbol }}</h2>{{ chord_diagram(chord, slug) }}<p class="chord-legend">O = open · X = muted<br>1 index · 2 middle · 3 ring · 4 little</p></section>
  <section class="surface-card practice-card"><h2>Finger placement</h2><ul class="lesson-steps">{% for placement in chord.placement %}<li>{{ placement }}</li>{% endfor %}</ul><h3>Strings to play</h3><p>{{ chord.played }}</p><h3>Strings to leave out</h3><p>{{ chord.muted }}</p><h3>Make it sound clear</h3><p>{{ chord.tip }}</p><p>Place your fingers just behind the frets. Pick each played string separately, adjust any buzzing notes, and then strum slowly.</p></section>
</div>
<div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Try another chord</a><a class="primary-btn" href="{{ url_for('lessons.strumming') }}">Add a strumming pattern →</a></div>
{% endblock %}

```

## templates/lessons/chords.html

```html
{% extends "shared/practice_base.html" %}
{% from "lessons/_chord_diagram.html" import chord_diagram %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">02 · Basic Chords</p><h1 class="section-title">Your first eight chords</h1><p>Choose a chord to see finger placements and playing tips. Try E minor first if you are just starting.</p></div>
<p class="chord-legend">O = open string · X = muted string · numbered circle = finger. 1 index, 2 middle, 3 ring, 4 little. Read from low E on the left to high E on the right.</p>
<div class="chord-grid">
  {% for slug, chord in chords.items() %}
  <a class="surface-card practice-card chord-card" href="{{ url_for('lessons.chord_detail', slug=slug) }}"><h2>{{ chord.name }} <span>{{ chord.symbol }}</span></h2>{{ chord_diagram(chord, slug) }}<span class="practice-link">Learn this chord →</span></a>
  {% endfor %}
</div>
{% endblock %}

```

## templates/lessons/getting_started.html

```html
{% extends "shared/practice_base.html" %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">01 · Getting Started</p><h1 class="section-title">Get to know your guitar</h1><p>Get comfortable before you start playing. These instructions describe right-handed playing; mirror the hands for left-handed playing.</p></div>
<nav class="lesson-topics" aria-label="Getting started topics"><a href="#parts">Guitar parts</a><a href="#holding">Holding your guitar</a><a href="#pick">Holding a pick</a><a href="#strings">String names</a><a href="#tuning">Standard tuning</a></nav>
<div class="lesson-basics-grid">
  <section id="parts" class="surface-card practice-card"><h2>Parts of a guitar</h2><dl class="lesson-definitions"><dt>Headstock &amp; tuning pegs</dt><dd>The headstock holds the pegs. Turn them to change string tension and pitch.</dd><dt>Nut, neck &amp; frets</dt><dd>The nut guides strings into the neck. Press just behind a metal fret to shorten a string and change its note.</dd><dt>Body &amp; sound</dt><dd>An acoustic guitar uses a sound hole and hollow body. An electric guitar uses pickups to send sound to an amplifier.</dd><dt>Bridge &amp; saddle</dt><dd>These support the strings at the body end and help transfer their vibrations.</dd></dl></section>
  <section id="holding" class="surface-card practice-card"><h2>How to hold a guitar</h2><ol class="lesson-steps"><li>Sit upright with both feet supported and your shoulders relaxed.</li><li>Rest the guitar body on your right thigh. Classical players may prefer the left thigh with a foot support.</li><li>Keep the neck angled slightly upward. Rest your right forearm lightly over the body.</li><li>Place your left thumb behind the neck and curve your fingers. Avoid squeezing or bending your wrist sharply.</li></ol><p>A strap can support the guitar while standing. Adjust it so both hands can move comfortably.</p></section>
  <section id="pick" class="surface-card practice-card"><h2>How to hold a guitar pick</h2><ol class="lesson-steps"><li>Curl your index finger gently.</li><li>Lay the pick on the side of the index finger, with the point facing the strings.</li><li>Place your thumb over it, leaving a small part of the point exposed.</li><li>Hold it securely, relax your wrist, and let the pick glide over the strings.</li></ol><p>A light or medium pick is a comfortable starting point. Use small motions instead of gripping tightly.</p></section>
  <section id="strings" class="surface-card practice-card"><h2>Guitar string names</h2><p>String 6 is the thickest and lowest. String 1 is the thinnest and highest.</p><ol class="lesson-string-list" reversed><li>6 · E — low E</li><li>5 · A</li><li>4 · D</li><li>3 · G</li><li>2 · B</li><li>1 · E — high E</li></ol><p>Remember: <strong>E A D G B E</strong>, from thick to thin.</p></section>
  <section id="tuning" class="surface-card practice-card lesson-wide"><h2>Standard guitar tuning</h2><p>The open-string pitches are E2 (82.41 Hz), A2 (110.00 Hz), D3 (146.83 Hz), G3 (196.00 Hz), B3 (246.94 Hz), and E4 (329.63 Hz). The octave number distinguishes low E from high E.</p><ol class="lesson-steps"><li>Open the tuner and press Start Tuner. Allow microphone access.</li><li>Mute the other strings and pluck one open string. Match its note and octave to the reference.</li><li>If the reading is flat, carefully increase tension. If sharp, reduce tension. Make small adjustments; avoid overtightening.</li><li>Repeat for all six strings and check them once more.</li></ol><a class="primary-btn" href="{{ url_for('tuner.index') }}">Open Guitar Tuner</a></section>
</div>
<div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Next: basic chords →</a></div>
{% endblock %}

```

## templates/lessons/index.html

```html
{% extends "shared/practice_base.html" %}
{% block practice_content %}
<div class="practice-heading">
  <p class="section-label">AUDIA practice studio</p>
  <h1 class="section-title">Learn Guitar</h1>
  <p>Start small, build good habits, and make your first chords ring.</p>
</div>
<div class="lesson-hero surface-card">
  <div class="practice-card">
    <p class="section-label">Your first practice</p>
    <h2>Pick up your guitar.<br>Find your rhythm.</h2>
    <p>A few focused minutes each day can help you get comfortable. Learn the strings, tune up, try a chord, then add a steady strum.</p>
    <div class="practice-actions"><a class="primary-btn" href="{{ url_for('lessons.getting_started') }}">Start learning</a><a class="secondary-btn" href="{{ url_for('tuner.index') }}">Tune your guitar</a></div>
  </div>
  <img src="{{ url_for('static', filename='images/acoustic_studio.jpg') }}" alt="Acoustic guitar ready for practice" width="640" height="480">
</div>
<div class="lesson-grid">
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.getting_started') }}"><span class="section-label">01 · Getting Started</span><h2>Get to know your guitar</h2><p>Parts, posture, pick grip, string names, and standard tuning.</p><span class="practice-link">Explore the basics →</span></a>
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.chords') }}"><span class="section-label">02 · Basic Chords</span><h2>Your first eight chords</h2><p>Clear diagrams and finger placements for C, G, D, A, E, Am, Em, and Dm.</p><span class="practice-link">Open the chord library →</span></a>
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.strumming') }}"><span class="section-label">03 · Strumming</span><h2>Bring chords to life</h2><p>Downstrokes, upstrokes, counting beats, and three beginner patterns.</p><span class="practice-link">Find your rhythm →</span></a>
</div>
{% endblock %}

```

## templates/lessons/strumming.html

```html
{% extends "shared/practice_base.html" %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">03 · Strumming</p><h1 class="section-title">Find your rhythm</h1><p>Choose a comfortable chord, such as E minor. Count out loud and keep your hand moving evenly.</p></div>
<section class="surface-card practice-card"><h2>Learn the strokes</h2><p><strong>D ↓ = Downstroke:</strong> move from thick strings toward thin strings. <strong>U ↑ = Upstroke:</strong> move back toward the thick strings, brushing lightly.</p><p>In 4/4 time, count <strong>1 &amp; 2 &amp; 3 &amp; 4 &amp;</strong>. Each number is a beat (a quarter note). The &amp; halfway between beats makes eighth notes. A dash means pass over the strings without striking them.</p></section>
<div class="strumming-lessons">
{% for pattern in patterns %}
<section class="surface-card practice-card"><h2>{{ pattern.name }}</h2><div class="strumming-pattern" role="group" aria-label="{{ pattern.name }} with beat counts">
{% for stroke in pattern.strokes %}<div class="strumming-beat"><span class="strumming-stroke{% if stroke == '–' %} strumming-rest{% endif %}">{{ stroke }}<span aria-hidden="true">{{ '↓' if stroke == 'D' else '↑' if stroke == 'U' else '·' }}</span></span><span class="strumming-count">{{ (loop.index0 // 2) + 1 if loop.index0 % 2 == 0 else '&' }}</span></div>{% endfor %}
</div><p>{{ pattern.description }}</p></section>
{% endfor %}
</div>
<section class="practice-card"><h2>Keep it comfortable</h2><ul class="lesson-steps"><li>Hold your pick with a relaxed grip and keep your wrist loose.</li><li>Start slowly, around 60 beats per minute on a metronome. Play one downstroke per click first.</li><li>Keep the same motion through silent gaps. Listen for even spacing between strokes.</li><li>Practice on one chord before changing chords. Increase the tempo only when the pattern feels steady.</li></ul><div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Choose a practice chord</a><a class="practice-link" href="{{ url_for('tuner.index') }}">Tune up before practice →</a></div></section>
{% endblock %}

```

## templates/shared/base.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#09090b" />
    <meta
      name="description"
      content="AUDIA - find the guitar that fits your music."
    />
    <title>{{ title }} | AUDIA</title>
    <script src="{{ url_for('static', filename='js/shared/theme.js') }}"></script>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/shared/shared.css') }}"
    />
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/' ~ stylesheet ~ '.css') }}"
    />
  </head>
  <body
    data-page="{{ page_name }}"
    data-auth-mode="{{ auth_mode|default('login') }}"
    data-reset-token="{{ reset_token|default('') }}"
  >
    <div
      id="root"
      inert
      aria-busy="true"
      class="min-h-screen bg-stone-50 text-zinc-950 transition-colors duration-300 dark:bg-ink dark:text-white"
    >
      {% block content %}{% endblock %}
    </div>
    {% block components %}{% endblock %} {% include 'shared/components.html' %}
    <script
      type="module"
      src="{{ url_for('static', filename='js/shared/app.js') }}"
    ></script>
  </body>
</html>

```

## templates/shared/components.html

```html
<!-- Reusable icons and dialogs shared by the shop, account and admin pages. -->

<template id="icon-arrow-right-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-arrow-right"
    aria-hidden="true"
  >
    <path d="M5 12h14"></path>
    <path d="m12 5 7 7-7 7"></path>
  </svg>
</template>

<template id="icon-eye-off-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-eye-off"
    aria-hidden="true"
  >
    <path
      d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"
    ></path>
    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"></path>
    <path
      d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"
    ></path>
    <path d="m2 2 20 20"></path>
  </svg>
</template>

<template id="icon-eye-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-eye"
    aria-hidden="true"
  >
    <path
      d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"
    ></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
</template>

<template id="icon-menu-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="19"
    height="19"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-menu"
    aria-hidden="true"
  >
    <path d="M4 5h16"></path>
    <path d="M4 12h16"></path>
    <path d="M4 19h16"></path>
  </svg>
</template>

<template id="icon-message-circle-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="21"
    height="21"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-message-circle"
    aria-hidden="true"
  >
    <path
      d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"
    ></path>
  </svg>
</template>

<template id="icon-moon-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-moon"
    aria-hidden="true"
  >
    <path
      d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"
    ></path>
  </svg>
</template>

<template id="icon-pause-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-pause"
    aria-hidden="true"
  >
    <rect x="14" y="3" width="5" height="18" rx="1"></rect>
    <rect x="5" y="3" width="5" height="18" rx="1"></rect>
  </svg>
</template>

<template id="icon-play-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="15"
    height="15"
    viewBox="0 0 24 24"
    fill="currentColor"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-play"
    aria-hidden="true"
  >
    <path
      d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"
    ></path>
  </svg>
</template>

<template id="icon-sun-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="17"
    height="17"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-sun"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="4"></circle>
    <path d="M12 2v2"></path>
    <path d="M12 20v2"></path>
    <path d="m4.93 4.93 1.41 1.41"></path>
    <path d="m17.66 17.66 1.41 1.41"></path>
    <path d="M2 12h2"></path>
    <path d="M20 12h2"></path>
    <path d="m6.34 17.66-1.41 1.41"></path>
    <path d="m19.07 4.93-1.41 1.41"></path>
  </svg>
</template>

<template id="icon-x-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="19"
    height="19"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-x"
    aria-hidden="true"
  >
    <path d="M18 6 6 18"></path>
    <path d="m6 6 12 12"></path>
  </svg>
</template>

<template id="order-detail-template">
  <div class="order-detail">
    <div class="order-status" data-field="status"></div>
    <dl class="detail-list">
      <dt>Placed</dt>
      <dd data-field="date"></dd>
      <dt>Customer</dt>
      <dd data-field="customer"></dd>
      <dt>Delivery address</dt>
      <dd data-field="address"></dd>
      <dt>Phone</dt>
      <dd data-field="phone"></dd>
      <dt>Payment</dt>
      <dd data-field="payment"></dd>
    </dl>
    <h3 class="font-semibold">Instruments &amp; gear</h3>
    <ul class="order-items" data-field="items"></ul>
    <div class="order-total">
      <span>Total</span><strong data-field="total"></strong>
    </div>
    <p class="form-hint">
      For changes or delivery assistance, contact the store with your order
      number.
    </p>
  </div>
</template>

<template id="dialog-template">
  <dialog class="app-dialog" aria-labelledby="dialog-title">
    <div class="dialog-heading">
      <div>
        <p class="section-label">AUDIA</p>
        <h2
          id="dialog-title"
          class="font-display text-2xl font-semibold"
          data-field="dialog-title"
        ></h2>
      </div>
      <button
        type="button"
        class="icon-btn"
        aria-label="Close dialog"
        data-action="dialog-close"
      >
        ✕
      </button>
    </div>
    <div data-field="dialog-body"></div>
  </dialog>
</template>

```

## templates/shared/practice_base.html

```html
{% extends "shared/base.html" %}
{% block content %}
<div class="practice-page">
  <header class="practice-header shell">
    <a class="audia-mark" href="{{ url_for('index') }}" aria-label="AUDIA home"><span class="mark-a">A</span>UDI<span class="mark-a">A</span></a>
    <nav class="practice-nav" aria-label="Main navigation">
      <a href="{{ url_for('shop') }}">Store</a>
      <a href="{{ url_for('shop') }}#shop">Products</a>
      <a href="{{ url_for('tuner.index') }}" {% if practice_area == 'tuner' %}aria-current="page"{% endif %}>Guitar Tuner</a>
      <a href="{{ url_for('lessons.index') }}" {% if practice_area == 'lessons' %}aria-current="page"{% endif %}>Guitar Lessons</a>
      <a href="{{ url_for('account_page') }}">Account</a>
    </nav>
    <button class="icon-btn" data-action="theme" aria-label="Change theme"></button>
  </header>
  <main class="shell practice-main">
    {% block practice_content %}{% endblock %}
  </main>
  {% include 'chatbot/chatbot.html' %}
</div>
{% endblock %}

```

## templates/shared/practice_links.html

```html
<nav class="shell flex flex-wrap items-center gap-3 py-3 text-sm border-b border-zinc-200 dark:border-white/10" aria-label="Guitar practice">
  <a class="flex items-center gap-2" href="{{ url_for('tuner.index') }}">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 10v4m4-8v12m4-15v18m4-15v12m4-8v4"/></svg>
    Guitar Tuner
  </a>
  <a class="flex items-center gap-2" href="{{ url_for('lessons.index') }}">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M12 5C9 3 5 3 2 4v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Zm0 0v15"/></svg>
    Guitar Lessons
  </a>
</nav>

```

## templates/tuner/tuner.html

```html
{% extends "shared/practice_base.html" %}
{% block practice_content %}
<div class="practice-heading">
  <p class="section-label">AUDIA practice studio</p>
  <h1 class="section-title">Guitar Tuner</h1>
  <p>Six strings. One clear sound. Pluck a single open string and let it ring.</p>
</div>
<div class="tuner-layout">
  <section class="surface-card tuner-container" aria-label="Live guitar tuner">
    <p id="tuner-microphone" class="tuner-microphone" role="status">Microphone inactive</p>
    <div class="tuner-readout" aria-label="Detected pitch">
      <p class="tuner-note"><span id="tuner-note">—</span><span id="tuner-octave" class="tuner-octave"></span></p>
      <p id="tuner-frequency" class="tuner-frequency">— Hz</p>
      <p id="tuner-cents" class="tuner-cents">— cents</p>
    </div>
    <p id="tuner-status" class="tuner-status" role="status">Play a string</p>
    <div id="tuner-meter" class="tuner-meter" role="meter" aria-label="Tuning deviation in cents" aria-valuemin="-50" aria-valuemax="50" aria-valuenow="0" aria-valuetext="No reliable pitch">
      <div class="tuner-meter-track"><span class="tuner-meter-center" aria-hidden="true"></span><span id="tuner-indicator" class="tuner-indicator" hidden></span></div>
      <div class="tuner-meter-labels" aria-hidden="true"><span>Flat −50</span><span>In tune</span><span>+50 Sharp</span></div>
    </div>
    <div class="practice-actions tuner-controls">
      <button id="tuner-start" type="button" class="primary-btn">Start Tuner</button>
      <button id="tuner-stop" type="button" class="secondary-btn" disabled>Stop Tuner</button>
    </div>
    <p id="tuner-error" class="form-error" role="alert" hidden></p>
    <p class="tuner-privacy">Audio is processed locally in your browser and is not recorded.</p>
  </section>
  <aside class="tuner-guide">
    <section class="surface-card practice-card">
      <p class="section-label">Standard tuning · A4 = 440 Hz</p>
      <h2>Meet your six strings</h2>
      <p>From the thickest string to the thinnest. The matching string lights up automatically.</p>
      <ol class="tuner-strings" reversed>
        {% for note, frequency in [('E2', '82.41'), ('A2', '110.00'), ('D3', '146.83'), ('G3', '196.00'), ('B3', '246.94'), ('E4', '329.63')] %}
        <li data-tuning-note="{{ note }}"><span>String {{ 7 - loop.index }}</span><strong>{{ note }}</strong><span>{{ frequency }} Hz</span></li>
        {% endfor %}
      </ol>
    </section>
    <section class="practice-card tuner-tips">
      <h2>A little preparation</h2>
      <p>Use a quiet room and keep your microphone near the guitar. Mute the other strings and pluck gently. Adjust the tuning peg a little at a time, then pluck again.</p>
      <p>Within ±5 cents is in tune. The note follows the nearest musical pitch; check the string reference to make sure you reach the intended open string.</p>
      <a class="practice-link" href="{{ url_for('lessons.getting_started') }}#tuning">Learn standard tuning →</a>
    </section>
  </aside>
</div>
{% endblock %}

```

## tests/practice.cjs

```javascript
// Run against python tests/serve.py (disposable database), never production.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';

(async () => {
  const browser = await chromium.launch({ headless: true, args: [
    '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
  ] });
  const errors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const email = `practice-${Date.now()}@example.com`;
    let session = await (await context.request.get(base + '/api/auth/session')).json();
    const register = await context.request.post(base + '/api/auth/register', {
      headers: { 'X-CSRF-Token': session.csrf_token },
      data: { name: 'Practice Player', email, password: 'practice-password-123' },
    });
    assert.equal(register.status(), 201);
    session = await (await context.request.get(base + '/api/auth/session')).json();
    assert.equal((await context.request.post(base + '/api/auth/login', {
      headers: { 'X-CSRF-Token': session.csrf_token }, data: { email, password: 'practice-password-123' },
    })).status(), 200);

    // Use real Web Audio nodes and streams for deterministic pitch/lifecycle tests.
    // The app still executes its actual getUserMedia -> analyser -> YIN path.
    await context.addInitScript(() => {
      const NativeAudioContext = window.AudioContext;
      const nativeGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      window.__audio = { mode: 'sine', calls: 0, stopped: 0, contexts: [], frequency: 110, stream: null };
      window.AudioContext = class extends NativeAudioContext {
        constructor(...args) { super(...args); window.__audio.contexts.push(this); }
      };
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        const state = window.__audio;
        state.calls++;
        if (state.mode === 'pending') await new Promise(resolve => { state.resolve = resolve; });
        if (['denied', 'missing', 'busy'].includes(state.mode)) {
          throw new DOMException('Test microphone error', state.mode === 'denied'
            ? 'NotAllowedError' : state.mode === 'missing' ? 'NotFoundError' : 'NotReadableError');
        }
        let stream;
        if (state.mode === 'native') stream = await nativeGetUserMedia(constraints);
        else {
          const generator = new NativeAudioContext();
          await generator.resume();
          const oscillator = generator.createOscillator();
          oscillator.frequency.value = state.frequency;
          const gain = generator.createGain(); gain.gain.value = .2;
          const destination = generator.createMediaStreamDestination();
          oscillator.connect(gain); gain.connect(destination); oscillator.start();
          stream = destination.stream;
          state.setPitch = frequency => oscillator.frequency.setValueAtTime(frequency, generator.currentTime);
          state.setVolume = volume => gain.gain.setValueAtTime(volume, generator.currentTime);
          state.disconnect = () => { stream.getTracks()[0].dispatchEvent(new Event('ended')); };
          state.cleanup = () => { oscillator.stop(); void generator.close(); };
        }
        for (const track of stream.getTracks()) {
          const stop = track.stop.bind(track);
          track.stop = () => { state.stopped++; stop(); state.cleanup?.(); };
        }
        state.stream = stream;
        return stream;
      };
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const newRequests = [];
    page.on('request', request => {
      if (request.method() !== 'GET') newRequests.push(request.method() + ' ' + new URL(request.url()).pathname);
    });
    const ready = () => page.locator('#root:not([inert])').waitFor();
    const start = () => page.getByRole('button', { name: 'Start Tuner', exact: true }).click();
    const stop = () => page.getByRole('button', { name: 'Stop Tuner', exact: true }).click();
    await page.goto(base + '/tuner'); await ready();
    assert.equal(await page.evaluate(() => window.__audio.calls), 0, 'No permission prompt on page load');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    const targets = [[82.406889, 'E', '2'], [110, 'A', '2'], [146.832384, 'D', '3'],
      [195.997718, 'G', '3'], [246.941651, 'B', '3'], [329.627557, 'E', '4']];
    for (const [frequency, note, octave] of targets) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), frequency);
      await page.waitForFunction(({ note, octave }) => document.querySelector('#tuner-note').textContent === note
        && document.querySelector('#tuner-octave').textContent === octave
        && document.querySelector('#tuner-status').textContent === 'In Tune', { note, octave });
      assert.equal(await page.locator(`[data-tuning-note="${note}${octave}"][data-active]`).count(), 1);
      assert.ok(Math.abs(parseFloat(await page.locator('#tuner-frequency').innerText()) - frequency) < .5);
    }
    for (const [cents, status] of [[-25, 'Too Flat'], [-10, 'Slightly Flat'], [10, 'Slightly Sharp'], [25, 'Too Sharp']]) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), 110 * 2 ** (cents / 1200));
      await page.getByText(status, { exact: true }).waitFor();
      const position = await page.locator('#tuner-indicator').evaluate(node => parseFloat(node.style.left));
      assert.ok(cents < 0 ? position < 50 : position > 50);
    }
    await page.evaluate(() => window.__audio.setVolume(0));
    await page.getByText('Play a string', { exact: true }).waitFor();
    assert.equal(await page.locator('#tuner-indicator').isHidden(), true);
    await page.evaluate(() => { window.__audio.setPitch(110); window.__audio.setVolume(.2); });
    await page.getByText('In Tune', { exact: true }).waitFor();
    await stop();
    await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks().every(track => track.readyState === 'ended')), true);

    for (const [mode, message] of [['denied', 'Permission denied'], ['missing', 'No microphone was detected'], ['busy', 'The microphone could not be started']]) {
      await page.evaluate(mode => { window.__audio.mode = mode; }, mode);
      await start(); await page.getByText(message, { exact: mode === 'denied' }).waitFor();
      assert.equal(await page.getByRole('button', { name: 'Start Tuner', exact: true }).isEnabled(), true);
      await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    }
    await page.evaluate(() => { window.__audio.mode = 'pending'; });
    await start(); await page.getByText('Requesting microphone', { exact: true }).waitFor();
    await page.waitForFunction(() => Boolean(window.__audio.resolve));
    await stop(); await page.evaluate(() => { window.__audio.mode = 'sine'; window.__audio.resolve(); });
    await page.waitForFunction(() => window.__audio.stopped === 2);
    assert.equal(await page.locator('#tuner-microphone').innerText(), 'Microphone inactive');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.__audio.disconnect());
    await page.getByText(/The microphone was disconnected/).waitFor();

    // Also exercise actual browser microphone permission and capture with a fake device.
    await page.evaluate(() => { window.__audio.mode = 'native'; window.__audio.cleanup = null; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await stop();
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks()[0].readyState), 'ended');

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { configurable: true, value: true });
      document.dispatchEvent(new Event('visibilitychange'));
      delete document.hidden;
    });
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.goto(base + '/lessons'); await ready();
    assert.ok(await page.getByRole('heading', { name: 'Learn Guitar', exact: true }).count());
    await page.getByRole('link', { name: 'Start learning', exact: true }).click(); await ready();
    await page.getByRole('link', { name: 'Next: basic chords →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.chord-diagram').count(), 8);
    await page.locator('.chord-card').first().click(); await ready();
    assert.equal(await page.locator('.chord-diagram .chord-string').count(), 6);
    await page.getByRole('link', { name: 'Add a strumming pattern →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.strumming-pattern').count(), 3);
    for (const pattern of await page.locator('.strumming-pattern').all()) {
      assert.deepEqual(await pattern.locator('.strumming-count').allTextContents(), ['1', '&', '2', '&', '3', '&', '4', '&']);
    }

    const routes = ['/tuner', '/lessons', '/lessons/getting-started', '/lessons/chords', '/lessons/strumming',
      ...['c-major', 'g-major', 'd-major', 'a-major', 'e-major', 'a-minor', 'e-minor', 'd-minor'].map(slug => '/lessons/chords/' + slug)];
    for (const route of routes) {
      await page.goto(base + route); await ready();
      for (const theme of ['dark', 'light']) {
        if (await page.locator('html').evaluate(node => node.classList.contains('dark')) !== (theme === 'dark')) {
          await page.locator('[data-action="theme"]').click();
        }
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          // Wait for Chromium's SVG layout to settle after resizing; keep the size assertion below.
          await page.waitForFunction(() => [...document.querySelectorAll('.chord-diagram')]
            .every(node => node.getBoundingClientRect().width >= 180));
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${route}: ${theme} at ${width}px`);
          const clipped = await page.locator('.chord-diagram, .tuner-meter, .strumming-pattern, .practice-nav').evaluateAll(nodes =>
            nodes.some(node => { const box = node.getBoundingClientRect(); return box.left < 0 || box.right > innerWidth; }));
          assert.equal(clipped, false, `${route}: clipped component at ${width}px`);
          const tinyDiagrams = await page.locator('.chord-diagram').evaluateAll(nodes =>
            nodes.some(node => node.getBoundingClientRect().width < 180));
          assert.equal(tinyDiagrams, false, `${route}: chord diagram too small to read at ${width}px`);
          if (process.env.SCREENSHOT_DIR && width === 320 && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
            fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
            await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}-mobile.png`, fullPage: true });
          }
        }
        if (process.env.SCREENSHOT_DIR && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
          fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
          await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}.png`, fullPage: true });
        }
      }
    }
    assert.deepEqual(newRequests, [], 'Practice pages must never upload audio or mutate server state');
    assert.deepEqual(errors, [], 'No browser JavaScript errors');
    console.log('PASS: Audio capture, six strings, flat/sharp meter, silence recovery, denial/missing/busy, stop, pending cancellation, disconnect and restart');
    console.log('PASS: Lessons, eight SVG shapes, beat alignment, links, 130 layout/theme cases and no JavaScript errors or audio uploads');
    const storage = await context.storageState();
    await context.close();

    // Unsupported browser must produce an actionable message without an uncaught error.
    const unsupported = await browser.newContext({ storageState: storage });
    await unsupported.addInitScript(() => { window.AudioContext = undefined; window.webkitAudioContext = undefined; });
    const unsupportedPage = await unsupported.newPage();
    await unsupportedPage.goto(base + '/tuner'); await unsupportedPage.locator('#root:not([inert])').waitFor();
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Your browser does not support/).waitFor();
    await unsupportedPage.evaluate(() => Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true }));
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Microphone access requires HTTPS or localhost/).waitFor();
    await unsupported.close();
    console.log('PASS: Unsupported audio API, insecure address and page lifecycle cleanup');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

```

## tests/serve.py

```python
"""Run the browser fixture on localhost with disposable data, not the real database."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from support import create_app
from modules.database import db, initialize
from modules.database.models import User
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='audia-browser-') as directory:
        app = create_app({'TESTING': True, 'SECRET_KEY': 'browser-fixture-only',
                          'DATABASE_URL': f'sqlite:///{Path(directory) / "browser.db"}', 'MAIL_BACKEND': 'memory'})
        initialize(app)
        with app.app_context():
            db().add(User(name='Test Admin', email='admin@example.com', role='admin',
                          password_hash=generate_password_hash('admin-password-123')))
            db().commit()
        try:
            app.run(host='127.0.0.1', port=int(os.getenv('TEST_PORT', '5056')), use_reloader=False)
        finally:
            app.extensions['engine'].dispose()

```

## tests/structure-browser.cjs

```javascript
// Compare existing screens before/after a structure-only migration.
// Run with tests/serve.py and STRUCTURE_PHASE=before, then =after.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';
const phase = process.env.STRUCTURE_PHASE || 'after';
assert.ok(['before', 'after'].includes(phase));
const directory = process.env.STRUCTURE_SNAPSHOTS || 'test-results/architecture/screens';

function decodeScreenshot(data) {
  let offset = 8, width, height, channels;
  const chunks = [];
  while (offset < data.length) {
    const length = data.readUInt32BE(offset);
    const type = data.toString('ascii', offset + 4, offset + 8);
    const chunk = data.subarray(offset + 8, offset + 8 + length);
    if (type === 'IHDR') {
      width = chunk.readUInt32BE(0); height = chunk.readUInt32BE(4);
      assert.equal(chunk[8], 8);
      assert.ok([2, 6].includes(chunk[9]));
      channels = chunk[9] === 2 ? 3 : 4;
    }
    if (type === 'IDAT') chunks.push(chunk);
    offset += length + 12;
  }
  const raw = zlib.inflateSync(Buffer.concat(chunks));
  const stride = width * channels, pixels = Buffer.alloc(stride * height);
  for (let row = 0; row < height; row++) {
    const filter = raw[row * (stride + 1)];
    for (let column = 0; column < stride; column++) {
      const index = row * stride + column;
      const left = column >= channels ? pixels[index - channels] : 0;
      const above = row ? pixels[index - stride] : 0;
      const corner = row && column >= channels ? pixels[index - stride - channels] : 0;
      let predictor = 0;
      if (filter === 1) predictor = left;
      if (filter === 2) predictor = above;
      if (filter === 3) predictor = Math.floor((left + above) / 2);
      if (filter === 4) {
        const estimate = left + above - corner;
        const distances = [Math.abs(estimate - left), Math.abs(estimate - above), Math.abs(estimate - corner)];
        predictor = [left, above, corner][distances.indexOf(Math.min(...distances))];
      }
      pixels[index] = (raw[row * (stride + 1) + column + 1] + predictor) & 255;
    }
  }
  return { width, height, channels, pixels };
}

function sameAppearance(before, after) {
  if (before.equals(after)) return true;
  const a = decodeScreenshot(before), b = decodeScreenshot(after);
  if (a.width !== b.width || a.height !== b.height || a.channels !== b.channels) return false;
  let changed = 0;
  for (let index = 0; index < a.pixels.length; index += a.channels) {
    let different = false;
    for (let channel = 0; channel < a.channels; channel++) {
      const delta = Math.abs(a.pixels[index + channel] - b.pixels[index + channel]);
      if (delta > 2) return false;
      different ||= delta > 0;
    }
    if (different) changed++;
  }
  // Permit only tiny compositor rounding: at most 2/255 in 0.1% of pixels.
  return changed / (a.width * a.height) <= .001;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const contexts = {};
    for (const role of ['guest', 'customer', 'admin']) {
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
      if (role !== 'guest') {
        const email = role === 'admin' ? 'admin@example.com' : 'structure@example.com';
        const password = role === 'admin' ? 'admin-password-123' : 'structure-password-123';
        let csrf = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
        if (role === 'customer') {
          const register = await context.request.post(base + '/api/auth/register', {
            headers: { 'X-CSRF-Token': csrf }, data: { name: 'Structure Player', email, password },
          });
          assert.ok([201, 409].includes(register.status()));
          csrf = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
        }
        const login = await context.request.post(base + '/api/auth/login', {
          headers: { 'X-CSRF-Token': csrf }, data: { email, password, role: role === 'admin' ? 'admin' : 'customer' },
        });
        assert.equal(login.status(), 200);
      }
      contexts[role] = context;
    }
    const cases = [
      ['guest', '/'], ['guest', '/login'], ['guest', '/register'], ['guest', '/reset-password'],
      ['customer', '/'], ['customer', '/shop'], ['customer', '/account'], ['admin', '/admin'],
      ['customer', '/tuner'], ['customer', '/lessons'], ['customer', '/lessons/getting-started'],
      ['customer', '/lessons/chords'], ['customer', '/lessons/chords/c-major'], ['customer', '/lessons/strumming'],
    ];
    let captured = 0;
    for (const [role, route] of cases) {
      const page = await contexts[role].newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {
        if (response.status() >= 400 && new URL(response.url()).pathname.startsWith('/static/')) {
          errors.push(`Missing asset: ${response.url()}`);
        }
      });
      await page.goto(base + route);
      await page.locator('#root:not([inert])').waitFor();
      if (route === '/shop') await page.waitForFunction(() => document.querySelectorAll('.product-card').length === 42);
      if (route === '/account') await page.getByText('Your first order starts with your next favorite instrument.', { exact: true }).waitFor();
      if (route === '/admin') await page.waitForFunction(() => document.querySelector('[data-field=total_orders]')?.textContent === '0');
      await page.locator('img').evaluateAll(images => Promise.all(images.map(async image => {
        image.loading = 'eager'; await image.decode();
      })));
      for (const theme of ['dark', 'light']) {
        if (await page.locator('html').evaluate(node => node.classList.contains('dark')) !== (theme === 'dark')) {
          await page.locator('#root [data-action="theme"]').first().click();
        }
        await page.evaluate(() => document.activeElement.blur());
        await page.mouse.move(0, 0);
        for (const width of [375, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${route} overflow`);
          const name = `${role}-${route.slice(1).replaceAll('/', '-') || 'landing'}-${theme}-${width}.png`;
          const target = path.join(directory, phase, name);
          fs.mkdirSync(path.dirname(target), { recursive: true });
          await page.screenshot({ path: target, fullPage: true, animations: 'disabled' });
          if (phase === 'after') {
            const original = path.join(directory, 'before', name);
            assert.ok(fs.existsSync(original), `Missing baseline: ${name}`);
            assert.ok(sameAppearance(fs.readFileSync(original), fs.readFileSync(target)), `Visual appearance changed: ${name}`);
          }
          captured++;
        }
      }
      assert.deepEqual(errors, [], `Browser errors: ${role} ${route}`);
      await page.close();
    }
    console.log(`PASS: ${captured} ${phase} screenshots, all assets loaded, no browser errors${phase === 'after' ? ', visually unchanged from before (strict pixel tolerance)' : ''}`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

```

## tests/test_ai.py

```python
"""Exercise the moved chatbot -> AI -> RAG pipeline without a paid API call."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from sqlalchemy import text
from support import create_app
from modules.ai import services as ai
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

```

## tests/test_app.py

```python
"""Integration checks use a disposable SQLite database, never the configured PostgreSQL server."""
import re
import tempfile
import unittest
from pathlib import Path
from sqlalchemy import URL, select
from werkzeug.security import generate_password_hash
from support import create_app
from modules.database import db, initialize
from modules.database.models import User, Product, LoginSession


class AudiaTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test-key','DATABASE_URL':f'sqlite:///{Path(self.directory.name)/"test.db"}', 'MAIL_BACKEND':'memory'})
        initialize(self.app)
        self.client=self.app.test_client()
        self.csrf=self.client.get('/api/auth/session').json['csrf_token']

    def tearDown(self):
        self.app.extensions['engine'].dispose()
        self.directory.cleanup()

    def send(self,path,data=None,method='POST',client=None,csrf=None):
        response=(client or self.client).open('/api'+path,method=method,json=data,
                    headers={'X-CSRF-Token':csrf or self.csrf})
        if client is None and response.is_json and response.json.get('csrf_token'):
            self.csrf=response.json['csrf_token']
        return response

    def register(self,email='player@example.com',name='Test Player'):
        result=self.send('/auth/register',dict(name=name,email=email,password='correct-horse-123'))
        self.assertEqual(result.status_code,201,result.json)
        login=self.send('/auth/login',dict(email=email,password='correct-horse-123'))
        self.assertEqual(login.status_code,200,login.json)
        return login.json['user']

    def admin(self):
        with self.app.app_context():
            user=db().scalar(select(User).where(User.email=='admin@example.com'))
            if not user:
                db().add(User(name='Store Admin',email='admin@example.com',password_hash=generate_password_hash('admin-password-123'),role='admin'))
                db().commit()
        response=self.send('/auth/login',dict(email='admin@example.com',password='admin-password-123',role='admin'))
        self.assertEqual(response.status_code,200,response.json)

    def order(self,quantity=1,key='unique-request-key-12345'):
        return self.send('/orders',dict(items=[dict(product_id=1,quantity=quantity)],address='123 Guitar Street, Quezon City',phone='09171234567',request_key=key))

    def test_assets_and_template_registry(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'class="landing-page"',response.data)
        self.assertNotIn(b'product-card-template',response.data)
        for route in ('/login','/register','/reset-password'):
            self.assertEqual(self.client.get(route).status_code,200)
        self.register()
        for route,name in (('/shop','checkout'),('/account','saved-item')):
            page=self.client.get(route)
            self.assertEqual(page.status_code,200)
            self.assertIn(f'id="{name}-template"'.encode(),page.data)
        self.admin()
        admin_page=self.client.get('/admin')
        for name in ('product-form','settings','notifications'):
            self.assertIn(f'id="{name}-template"'.encode(),admin_page.data)
        self.assertNotRegex(response.get_data(as_text=True),r'<style\b|\sstyle=')
        for asset in Path(self.app.static_folder).rglob('*'):
            if asset.is_file():
                with self.client.get('/static/'+asset.relative_to(self.app.static_folder).as_posix()) as result:
                    self.assertEqual(result.status_code,200,str(asset))

    def test_unconfigured_landing_has_no_catalog_or_fake_authentication(self):
        preview=create_app({'TESTING':True,'SECRET_KEY':'preview','DATABASE_URL':''}).test_client()
        self.assertEqual(preview.get('/').status_code,200)
        self.assertEqual(preview.get('/api/products').status_code,401)
        self.assertEqual(preview.get('/api/health').status_code,503)
        token=preview.get('/api/auth/session').json['csrf_token']
        response=self.send('/auth/login',dict(email='admin@audia.ph',password='admin123'),client=preview,csrf=token)
        self.assertEqual(response.status_code,503)
        self.assertIsNone(preview.get('/api/auth/session').json['user'])

    def test_registration_password_hash_role_and_duplicate(self):
        response=self.send('/auth/register',dict(name='New Player',email='PLAYER@EXAMPLE.COM',password='correct-horse-123',role='admin'))
        self.assertEqual(response.status_code,201)
        self.assertNotIn('user',response.json)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        self.assertEqual(self.client.get('/api/products').status_code,401)
        self.assertEqual(self.client.get('/shop').status_code,302)
        with self.app.app_context():
            user=db().scalar(select(User).where(User.email=='player@example.com'))
            self.assertEqual(user.role,'customer')
            self.assertEqual(db().query(LoginSession).count(),0)
            self.assertNotEqual(user.password_hash,'correct-horse-123')
            self.assertTrue(user.password_hash.startswith('scrypt:'))
        self.assertEqual(self.send('/auth/register',dict(name='Other',email='player@example.com',password='correct-horse-123')).status_code,409)

    def test_login_rejects_demo_wrong_password_and_role_escalation(self):
        self.register()
        self.send('/auth/logout')
        for email,password,role in [('player@example.com','wrong','customer'),('admin@audia.ph','admin123','admin'),('player@example.com','correct-horse-123','admin')]:
            self.assertEqual(self.send('/auth/login',dict(email=email,password=password,role=role)).status_code,401)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        good=self.send('/auth/login',dict(email='PLAYER@example.com',password='correct-horse-123',remember=True))
        self.assertEqual(good.status_code,200)
        cookie=good.headers.get('Set-Cookie','')
        self.assertIn('HttpOnly',cookie);self.assertIn('SameSite=Lax',cookie);self.assertIn('Expires=',cookie)

    def test_csrf_admin_and_order_access(self):
        self.assertEqual(self.client.post('/api/auth/login',json={}).status_code,403)
        for path in ['/api/admin/sales','/api/admin/products','/api/admin/customers','/api/admin/summary','/api/admin/settings','/api/admin/sales/export']:
            self.assertEqual(self.client.get(path).status_code,401,path)
        self.register()
        self.assertEqual(self.client.get('/api/admin/sales').status_code,403)
        self.assertEqual(self.send('/admin/products',{},method='POST').status_code,403)

    def test_logout_invalidates_replayed_cookie(self):
        self.register()
        old_cookie=self.client.get_cookie('session').value
        self.send('/auth/logout')
        self.client.set_cookie('session',old_cookie)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])

    def test_reset_single_use_and_session_revocation(self):
        self.register()
        old_cookie=self.client.get_cookie('session').value
        response=self.send('/auth/forgot-password',dict(email='player@example.com'))
        self.assertEqual(response.status_code,200)
        message=self.app.extensions['outbox'][-1].get_content()
        token=re.search(r'/reset-password\?token=([^\s]+)',message)[1]
        self.assertNotIn(token,str(response.json))
        self.assertEqual(self.send('/auth/reset-password',dict(token=token,password='new-password-123')).status_code,200)
        self.assertEqual(self.send('/auth/reset-password',dict(token=token,password='other-password-123')).status_code,400)
        other=self.app.test_client();other.set_cookie('session',old_cookie)
        self.assertIsNone(other.get('/api/auth/session').json['user'])
        self.assertEqual(self.send('/auth/login',dict(email='player@example.com',password='correct-horse-123')).status_code,401)
        self.assertEqual(self.send('/auth/login',dict(email='player@example.com',password='new-password-123')).status_code,200)

    def test_password_change_profile_and_rate_limit(self):
        self.register()
        self.assertEqual(self.send('/auth/password',dict(current_password='wrong',password='new-password-123')).status_code,400)
        self.assertEqual(self.send('/auth/password',dict(current_password='correct-horse-123',password='new-password-123')).status_code,200)
        updated=self.send('/auth/profile',dict(name='Updated Player',phone='09171234567',address='Guitar Street'),method='PATCH')
        self.assertEqual(updated.json['user']['name'],'Updated Player')
        for _ in range(9):
            response=self.send('/auth/login',dict(email='none@example.com',password='incorrect'))
        self.assertEqual(response.status_code,429)

    def test_catalog_finder_and_wishlist(self):
        self.register()
        self.assertEqual(self.client.get('/api/products?category=acoustic&q=ACOUSTIC_001').json['count'],1)
        self.assertEqual(self.client.get('/api/products/999').status_code,404)
        profile=dict(budget=20000,category='Electric',level='Beginner',genre='Rock')
        result=self.send('/finder',profile)
        self.assertEqual(result.json['recommendations'][0]['name'],'ELECTRIC_010')
        self.assertEqual(self.send('/finder',dict(profile,budget='bad')).status_code,400)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,200)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,200)
        data=self.client.get('/api/account/saved').json
        self.assertEqual(len(data['products']),1);self.assertEqual(data['profile'],profile)
        self.send('/account/saved/1',method='DELETE')
        self.assertEqual(self.client.get('/api/account/saved').json['products'],[])

    def test_checkout_server_prices_stock_idempotency_and_ownership(self):
        self.register()
        first=self.order(2);self.assertEqual(first.status_code,201,first.json)
        self.assertEqual(first.json['order']['amount'],25980)
        self.assertEqual(self.order(2).json['order']['id'],first.json['order']['id'])
        self.assertEqual(self.client.get('/api/products/1').json['stock'],6)
        self.assertEqual(self.order(99,'other-request-key-12345').status_code,400)
        self.assertEqual(self.client.get('/api/products/1').json['stock'],6)
        self.assertEqual(len(self.client.get('/api/orders').json['orders']),1)
        self.register('another@example.com')
        self.assertEqual(self.client.get('/api/orders/'+first.json['order']['id']).status_code,404)

    def test_invalid_checkout_rolls_back_all_items(self):
        self.register()
        response=self.send('/orders',dict(request_key='rollback-request-key-123',address='123 Guitar Street',phone='09171234567',
                           items=[dict(product_id=1,quantity=1),dict(product_id=2,quantity=99)]))
        self.assertEqual(response.status_code,400)
        self.assertEqual(self.client.get('/api/products/1').json['stock'],8)
        self.assertEqual(self.client.get('/api/orders').json['orders'],[])

    def test_admin_inventory_orders_reporting_export_settings(self):
        self.register(name='=FORMULA')
        order=self.order().json['order']
        self.admin()
        base=self.client.get('/api/products/1').json
        data=dict(base,name='Test instrument',stock=3,price=12345.67)
        created=self.send('/admin/products',data)
        self.assertEqual(created.status_code,201,created.json)
        product_id=created.json['product']['id']
        self.assertEqual(self.send(f'/admin/products/{product_id}',dict(data,stock=5),method='PUT').json['product']['stock'],5)
        self.assertEqual(self.send(f'/admin/products/{product_id}',method='DELETE').status_code,200)
        self.assertEqual(self.client.get(f'/api/products/{product_id}').status_code,404)
        for status in ['Processing','Shipped','Delivered']:
            self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status=status),method='PATCH').status_code,200)
        summary=self.client.get('/api/admin/summary').json
        self.assertEqual(summary['gross_revenue'],12990)
        self.assertEqual(summary['categories']['Electric'],12990)
        self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status='Pending'),method='PATCH').status_code,400)
        self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status='Refunded'),method='PATCH').status_code,200)
        self.send('/admin/sales/'+order['id'],dict(status='Refunded'),method='PATCH')
        self.assertEqual(self.client.get('/api/products/1').json['stock'],8)
        exported=self.client.get('/api/admin/sales/export').get_data(as_text=True)
        self.assertIn("'=FORMULA",exported)
        settings=self.send('/admin/settings',dict(store_name='AUDIA Studio',support_email='studio@example.com'),method='PUT')
        self.assertEqual(settings.json['settings']['store_name'],'AUDIA Studio')
        self.assertEqual(len(self.client.get('/api/admin/customers').json['customers']),1)

    def test_malformed_requests_and_validation(self):
        self.assertEqual(self.send('/auth/register',[]).status_code,400)
        self.assertEqual(self.send('/auth/register',dict(name='Player',email='bad',password='short')).status_code,400)
        self.admin()
        data=self.client.get('/api/products/1').json
        for changes in [dict(price='NaN'),dict(stock=-1),dict(image='javascript:alert(1)'),dict(category='Unknown')]:
            self.assertEqual(self.send('/admin/products',dict(data,**changes)).status_code,400)

    def test_uploaded_catalog_codes_categories_and_files(self):
        self.register()
        products=self.client.get('/api/products').json['products']
        guitars=[p for p in products if p['category'] in ('Electric','Acoustic','Bass','Classical')]
        self.assertEqual(len(guitars),40)
        self.assertEqual(len({p['image'] for p in guitars}),40)
        for category in ('Electric','Acoustic','Bass','Classical'):
            group=[p for p in guitars if p['category']==category]
            self.assertEqual([p['name'] for p in group],[f'{category.upper()}_{i:03d}' for i in range(1,11)])
            for product in group:
                self.assertTrue(product['image'].startswith(f'/static/images/{category.lower()}/'))
                self.assertIsInstance(product['id'],int)
                self.assertGreater(product['stock'],0)
                self.assertGreater(product['price'],0)
                self.assertTrue(product['description'])
                self.assertTrue(product['specs'])
                self.assertEqual(product['reviews'],0)
        self.assertIn('images/guitar_performance.jpg',self.app.test_client().get('/login').get_data(as_text=True))

    def test_initialization_preserves_inventory_and_does_not_duplicate_catalog(self):
        self.register()
        with self.app.app_context():
            product=db().get(Product,1)
            product.stock=2
            product.price=5432
            db().commit()
        initialize(self.app)
        response=self.client.get('/api/products').json
        self.assertEqual(response['count'],42)
        first=next(p for p in response['products'] if p['id']==1)
        self.assertEqual((first['stock'],first['price']),(2,5432))

    def test_local_and_https_inventory_images(self):
        self.admin()
        product=self.client.get('/api/products/1').json
        for path in ('/static/images/electric/Amber_Flame.png','https://example.com/guitar.png'):
            result=self.send('/admin/products/1',dict(product,image=path),method='PUT')
            self.assertEqual(result.status_code,200,result.json)
            self.assertEqual(result.json['product']['image'],path)
        for path in ('/static/images/missing.png','/static/images/../../.env',
                     '/static/images/../icons/play.svg','//example.com/guitar.png',
                     'data:image/svg+xml,<svg/>','/static/images/%2e%2e/.env'):
            self.assertEqual(self.send('/admin/products/1',dict(product,image=path),method='PUT').status_code,400,path)

    def test_sqlalchemy_url_object_configuration(self):
        app=create_app({'TESTING':True,'SECRET_KEY':'url-test',
                        'DATABASE_URL':URL.create('sqlite',database=':memory:')})
        try:
            initialize(app)
            self.assertEqual(app.test_client().get('/api/products').status_code,401)
            with app.app_context():
                self.assertEqual(db().query(Product).count(),42)
        finally:
            app.extensions['engine'].dispose()

    def test_guests_cannot_read_catalog_find_products_or_checkout(self):
        for path in ('/api/products','/api/products?category=Electric','/api/products/1',
                     '/api/account/saved','/api/orders'):
            response=self.client.get(path)
            self.assertEqual(response.status_code,401,path)
            self.assertNotIn('products',response.json)
        self.assertEqual(self.send('/finder',dict(budget=20000,category='Electric',level='Beginner')).status_code,401)
        self.assertEqual(self.order().status_code,401)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,401)
        self.register()
        self.assertEqual(self.client.get('/api/products').json['count'],42)
        self.send('/auth/logout')
        self.assertEqual(self.client.get('/api/products').status_code,401)
        self.assertEqual(self.client.get('/api/products/1').status_code,401)

    def test_expired_session_cannot_read_products(self):
        from datetime import timedelta
        from modules.database.models import now
        self.register()
        with self.app.app_context():
            for login in db().scalars(select(LoginSession)):
                login.expires_at=now()-timedelta(seconds=1)
            db().commit()
        self.assertEqual(self.client.get('/api/products').status_code,401)


    def test_page_routes_require_login_and_admin_role(self):
        for route in ('/shop','/account','/admin'):
            response=self.client.get(route)
            self.assertEqual(response.status_code,302)
            self.assertTrue(response.headers['Location'].startswith('/login'))
        self.register()
        self.assertEqual(self.client.get('/shop').status_code,200)
        self.assertEqual(self.client.get('/account').status_code,200)
        self.assertEqual(self.client.get('/admin').headers['Location'],'/shop')
        self.admin()
        self.assertEqual(self.client.get('/admin').status_code,200)
        self.send('/auth/logout')
        self.assertEqual(self.client.get('/shop').headers['Location'],'/login')

if __name__=='__main__':
    unittest.main()

```

## tests/test_practice.py

```python
"""New feature routes use the existing auth/security hooks and disposable data."""
import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from support import create_app
from modules.database import db, initialize
from modules.database.models import User
from werkzeug.security import generate_password_hash


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="audia-practice-")
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "practice-tests-only",
            "DATABASE_URL": f'sqlite:///{Path(self.directory.name) / "test.db"}',
        })
        initialize(self.app)
        with self.app.app_context():
            db().add(User(name="Practice Player", email="practice@example.com",
                          password_hash=generate_password_hash("practice-password-123")))
            db().commit()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.extensions["engine"].dispose()
        self.directory.cleanup()

    def sign_in(self):
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        result = self.client.post("/api/auth/login", json={
            "email": "practice@example.com", "password": "practice-password-123",
        }, headers={"X-CSRF-Token": csrf})
        self.assertEqual(result.status_code, 200)

    def test_guest_redirects_and_security(self):
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords",
                     "/lessons/chords/c-major", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response.location, "/login")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.post("/api/chat", json={"message": "hello"}).status_code, 403)
        self.assertEqual(self.client.get("/api/products").status_code, 401)

    def test_pages_assets_and_navigation(self):
        self.sign_in()
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            html = response.get_data(as_text=True)
            for link in re.findall(r'(?:href|src)="([^"]+)"', html):
                if link.startswith("/"):
                    with self.client.get(link.split("#")[0]) as linked:
                        self.assertEqual(linked.status_code, 200, link)
        for path in ("/", "/shop", "/account"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertIn('href="/tuner"', html)
            self.assertIn('href="/lessons"', html)
        for filename in ("css/shared/practice.css", "css/tuner/tuner.css", "css/lessons/lessons.css", "js/tuner/tuner.js", "js/tuner/pitch.js"):
            with self.client.get("/static/" + filename) as asset:
                self.assertEqual(asset.status_code, 200)

    def test_all_chord_shapes_and_missing_chord(self):
        self.sign_in()
        shapes = {
            "c-major": (1, 2, 3), "g-major": (0, 3, 3), "d-major": (2, 1, 3),
            "a-major": (1, 2, 3), "e-major": (0, 3, 3), "a-minor": (1, 2, 3),
            "e-minor": (0, 4, 2), "d-minor": (2, 1, 3),
        }
        for slug, (muted, opened, fretted) in shapes.items():
            html = self.client.get("/lessons/chords/" + slug).get_data(as_text=True)
            diagram = ElementTree.fromstring(re.search(r'<svg class="chord-diagram".*?</svg>', html, re.S)[0])
            strings = diagram.findall(".//line[@class='chord-string']")
            self.assertEqual(len(strings), 6, slug)
            self.assertEqual([int(line.attrib["x1"]) for line in strings], [35, 65, 95, 125, 155, 185])
            markers = [node.text for node in diagram.findall(".//text[@class='chord-open-muted']")]
            self.assertEqual(markers.count("X"), muted, slug)
            self.assertEqual(markers.count("O"), opened, slug)
            self.assertEqual(len(diagram.findall(".//circle")), fretted, slug)
            self.assertIn("Finger placement", html)
        self.assertEqual(self.client.get("/lessons/chords/missing-chord").status_code, 404)

    def test_revoked_session_and_read_only_routes(self):
        self.sign_in()
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        cookie = self.client.get_cookie("session").value
        self.assertEqual(self.client.post("/tuner").status_code, 405)
        self.client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
        self.client.set_cookie("session", cookie)
        self.assertEqual(self.client.get("/tuner").status_code, 302)
        self.assertEqual(self.client.get("/lessons").status_code, 302)


if __name__ == "__main__":
    unittest.main()

```

## tests/test_structure.py

```python
"""Migration contracts recorded before the structure-only refactor.

These check route identity, unchanged logic, and lossless file moves, rather
than testing an alternative implementation of AUDIA's features.
"""
import ast
import hashlib
import json
import re
import unittest
from pathlib import Path

from app import app

ROOT = Path(__file__).resolve().parent.parent
BASELINE = json.loads((ROOT / "docs/architecture/before.json").read_text(encoding="utf-8"))
MIGRATION = json.loads((ROOT / "docs/architecture/migration.json").read_text(encoding="utf-8"))

# Canonicalize only resource paths that are allowed to change in this refactor.
PATHS = {
    "landing/landing.html": "landing.html", "auth/auth.html": "auth.html",
    "catalog/storefront.html": "storefront.html", "account/account.html": "account.html",
    "admin/admin.html": "admin.html", "chatbot/chatbot.html": "chatbot.html",
    "shared/base.html": "base.html", "shared/components.html": "shared.html",
    "shared/practice_base.html": "practice/base.html",
    "shared/practice_links.html": "practice/feature_links.html",
    "landing/landing": "landing", "auth/auth": "auth", "catalog/storefront": "storefront",
    "account/account": "account", "admin/admin": "admin", "tuner/tuner": "tuner",
    "lessons/lessons": "lessons",
}
PATHS.update({new.removeprefix("assets/"): old.removeprefix("assets/")
              for old, new in MIGRATION.items() if old.startswith("assets/")})


class OriginalLogic(ast.NodeTransformer):
    def visit_Import(self, node):
        return None

    def visit_ImportFrom(self, node):
        return None

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.value = PATHS.get(node.value, node.value)
        return node


def original_frontend_bytes(old, raw):
    """Undo explicit import/include changes so all other bytes must match."""
    source = raw.decode("utf-8")
    if old.endswith(".html"):
        for new, original in PATHS.items():
            if new.endswith(".html") or new.startswith(("js/", "css/")):
                source = source.replace(new, original)
    if old.endswith(".css"):
        source = source.replace('../shared/practice.css', './practice.css')
        for original, new in MIGRATION.items():
            if original.startswith("templates/"):
                source = source.replace(new, original)
    if old == "assets/js/app.js":
        for new, original in {
            "../chatbot/chatbot.js": "./chatbot/chatbot.js",
            "../catalog/storefront.js": "./storefront.js",
            "../auth/auth.js": "./auth.js", "../admin/admin.js": "./admin.js",
            "../account/account.js": "./account.js", "../tuner/tuner.js": "./tuner.js",
        }.items():
            source = source.replace(new, original)
    elif old in ("assets/js/auth.js", "assets/js/storefront.js", "assets/js/account.js", "assets/js/admin.js"):
        source = source.replace('../shared/shared.js', './shared.js')
    elif old == "assets/js/tuner.js":
        source = source.replace('./pitch.js', './tuner-pitch.js')
    elif old == "assets/js/chatbot/chatbot-ui.js":
        source = source.replace('../shared/shared.js', '../shared.js')
    elif old == "tests/tuner-pitch.cjs":
        source = source.replace('assets/js/tuner/pitch.js', 'assets/js/tuner-pitch.js')
    elif old == "tests/practice.cjs":
        # Only this test-readiness wait was added; every original assertion remains.
        source = source.replace(
            "          // Wait for Chromium's SVG layout to settle after resizing; keep the size assertion below.\n"
            "          await page.waitForFunction(() => [...document.querySelectorAll('.chord-diagram')]\n"
            "            .every(node => node.getBoundingClientRect().width >= 180));\n", "")
    return source.encode("utf-8")


class StructureTests(unittest.TestCase):
    def test_exact_route_and_blueprint_contract(self):
        routes = sorted([
            {"endpoint": rule.endpoint, "methods": sorted(rule.methods), "rule": rule.rule}
            for rule in app.url_map.iter_rules()
        ], key=lambda rule: (rule["endpoint"], rule["rule"], rule["methods"]))
        self.assertEqual(routes, BASELINE["routes"])
        self.assertEqual(list(app.blueprints), BASELINE["blueprints"])
        self.assertEqual(len({id(blueprint) for blueprint in app.blueprints.values()}), 7)

    def test_original_files_and_logic_preserved(self):
        for old, before in BASELINE["files"].items():
            with self.subTest(file=old):
                target = ROOT / MIGRATION.get(old, old)
                self.assertTrue(target.is_file(), f"Missing original file: {target}")
                if old in MIGRATION:
                    self.assertFalse((ROOT / old).is_file(), f"Duplicate old source: {old}")
                raw = target.read_bytes()
                if "logic_sha256" in before:
                    tree = OriginalLogic().visit(ast.parse(raw.decode("utf-8-sig")))
                    digest = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
                    self.assertEqual(digest, before["logic_sha256"], "Non-import/path Python logic changed")
                elif (old.startswith(("assets/", "templates/")) and target.suffix in (".html", ".css", ".js")) or old in ("tests/tuner-pitch.cjs", "tests/practice.cjs"):
                    digest = hashlib.sha256(original_frontend_bytes(old, raw)).hexdigest()
                    self.assertEqual(digest, before["sha256"], "Non-path frontend content changed")
                elif not old.endswith(".md") and old != "tests/tuner-pitch.cjs":
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), before["sha256"])
                elif old.startswith("assets/images/") or old == "docs/guitar-practice-source.md":
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), before["sha256"])

    def test_template_and_browser_import_paths(self):
        for name in app.jinja_env.list_templates():
            app.jinja_env.get_template(name)
        for folder, extension, pattern in [
            ("assets/js", "*.js", r'(?:from\s*|import\s*\()\s*[\'\"](\.[^\'\"]+)[\'\"]'),
            ("assets/css", "*.css", r'@import\s+url\([\'\"]([^\'\"]+)[\'\"]\)'),
        ]:
            for path in (ROOT / folder).rglob(extension):
                for reference in re.findall(pattern, path.read_text(encoding="utf-8")):
                    if reference.startswith(("https://", "http://", "//", "data:")):
                        continue
                    self.assertTrue((path.parent / reference).resolve().is_file(), f"{path}: {reference}")


if __name__ == "__main__":
    unittest.main()

```

## tests/tuner-pitch.cjs

```javascript
// Run with node tests/tuner-pitch.cjs. No microphone or npm dependency required.
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const code = fs.readFileSync('assets/js/tuner/pitch.js', 'utf8');
  const { detectPitch, describePitch, PitchStabilizer } = await import(
    'data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
  const targets = [[82.406889, 'E', 2], [110, 'A', 2], [146.832384, 'D', 3],
    [195.997718, 'G', 3], [246.941651, 'B', 3], [329.627557, 'E', 4]];
  for (const rate of [44100, 48000, 96000]) {
    for (const [target, note, octave] of targets) {
      for (const cents of [-25, -10, 0, 10, 25]) {
        const frequency = target * 2 ** (cents / 1200);
        // A plucked-string-like signal with harmonics and a decaying envelope.
        const samples = Float32Array.from({ length: 4096 }, (_, index) => {
          const phase = 2 * Math.PI * frequency * index / rate;
          return Math.exp(-index / rate * 3) * (.2 * Math.sin(phase) + .12 * Math.sin(phase * 2) + .06 * Math.sin(phase * 3));
        });
        const detected = detectPitch(samples, rate);
        assert.ok(detected, `${note}${octave}, ${cents} cents, ${rate} Hz`);
        const pitch = describePitch(detected.frequency);
        assert.equal(pitch.note, note); assert.equal(pitch.octave, octave);
        assert.ok(Math.abs(pitch.cents - cents) < 2, `Pitch error: ${pitch.cents - cents} cents`);
        assert.equal(pitch.status, cents === 0 ? 'In Tune' : cents < -15 ? 'Too Flat'
          : cents < 0 ? 'Slightly Flat' : cents > 15 ? 'Too Sharp' : 'Slightly Sharp');
      }
    }
  }
  assert.equal(detectPitch(new Float32Array(4096), 48000), null);
  assert.equal(detectPitch(new Float32Array(4096).fill(.2), 48000), null, 'DC input');
  assert.equal(detectPitch(Float32Array.from({ length: 4096 }, (_, i) => .001 * Math.sin(i)), 48000), null);
  let seed = 123;
  const noise = Float32Array.from({ length: 4096 }, () => {
    seed = (1664525 * seed + 1013904223) >>> 0;
    return (seed / 2 ** 32 - .5) * .3;
  });
  assert.equal(detectPitch(noise, 48000), null, 'Broadband noise');
  const smoother = new PitchStabilizer();
  assert.equal(smoother.push(110), null); assert.equal(smoother.push(110.1), null);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  assert.equal(smoother.push(196), null, 'One outlier cannot change the note');
  assert.equal(smoother.push(110), null); smoother.push(110);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  smoother.reset(); assert.equal(smoother.push(82.4), null);
  console.log('PASS: 90 harmonic pitch cases across six strings, three sample rates, flat/sharp/in-tune; silence, weak input, noise and stabilization');
})().catch(error => { console.error(error); process.exitCode = 1; });

```
