# AUDIA — Guitar E-Commerce Platform

AUDIA uses Flask, HTML templates, plain CSS, and vanilla JavaScript. Flask serves the website and the existing `/api` endpoints together. React, Vite, and a frontend build are no longer required.

## Run locally

From the project root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install the Python dependencies and start Flask:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**. The existing `python backend/app.py` entry point also works. HTML must be served through Flask so its template includes and static asset URLs are rendered.

## Project structure

```text
app.py                  Root Flask entry point
backend/app.py          Existing API logic and Flask configuration
backend/requirements.txt
requirements.txt        Root dependency-install entry point
templates/
  index.html            Document served by Flask
  fragments.html        Native HTML template declarations
  partials/             Storefront, sign-in, admin, dialogs, rows, and SVG icons
static/
  css/styles.css        Existing design compiled into ordinary CSS
  css/motion.css        Native animation and visibility support
  js/app.js             Screen navigation and theme switching
  js/storefront.js      Catalog, cart, finder, tracking, chat, and audio
  js/auth.js            Existing login rules and fallback behavior
  js/admin.js           Admin navigation, sales filtering, and customer views
  js/dom.js             Template cloning and browser animation helpers
  js/data.js            Original fallback catalog and sales data
  js/theme.js           Saved theme applied before rendering
tests/                  Flask and browser regression checks
```

All HTML lives in `templates/`. JavaScript clones native `<template>` elements and uses DOM events and `textContent` to update them. Styles are editable CSS; no Tailwind compiler or npm install is needed. Icons are inline SVG, with their license in `static/icons-LICENSE.txt`. Animations use Web Animations and IntersectionObserver, with reduced-motion support.

## Preserved behavior

- Responsive catalog, search, categories, sorting, ratings, stock, wishlist toggles, and synthesized sound previews.
- Four-step Guitar Finder with the same API requests, ranking, answer retention, and local fallback.
- Cart additions, quantities, removal, item count, and subtotal.
- AUDI chat presets, conversation state, API replies, and fallback replies.
- Demo order tracking, customer/admin sign-in, password visibility, and role-aware navigation.
- Admin overview, products, customers, and searchable/filterable sales directory.
- Persistent light/dark theme, mobile navigation, and the existing layout, colors, fonts, images, and icons.

Existing API functions and catalog/sales data are unchanged. Store, cart, and account state retain their original in-memory lifetime; only the theme persists across reloads. Existing display-only controls (including checkout, bundle details, account creation, password recovery, admin edits, CSV export, and pagination) remain display-only. This migration does not add business behavior to those controls.

Product images and fonts retain their original external URLs. Local catalog, finder, sign-in, sales, and chat fallbacks remain available when an API request fails.

## Demo accounts

- Customer: `user@audia.ph` / `audia123`
- Administrator: `admin@audia.ph` / `admin123`

These accounts are demonstration-only. The existing customer API accepts an email containing `@` and a password of at least six characters. Replace demo authentication with database-backed users, password hashing, and secure sessions before production use.

## Verification

Run the Flask tests without a running server:

```bash
python -m unittest discover -s tests -v
```

For the optional browser regression suite, start Flask, make Playwright available to Node, and run:

```bash
node tests/browser.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright installation. `AUDIA_BASE_URL` defaults to `http://127.0.0.1:5000`. The suite checks catalog actions, cart totals, finder answers, chat, authentication, sales filters, theme persistence, API failure fallbacks, and responsive layouts from 320px to 1440px.
