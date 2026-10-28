# AUDIA frontend component map

For a first HTML/CSS edit, follow [CSS_EDITING_GUIDE.md](CSS_EDITING_GUIDE.md).
Shared colors are in `assets/css/shared/theme.css`; browser defaults are in
`assets/css/shared/reset.css`. Component adjustments live in their matching
CSS files, including theme and responsive rules.

Current frontend map after the October 15 HTML/CSS refactor. Existing folders, filenames, Flask routes and backend logic are preserved. Catalog and search/filter each contain a single HTML/CSS pair with section comments. Other module entry stylesheets import their matching component sheets; `shared.css` loads shared primitives. No frontend build is required.

| Module | UI Component | HTML File | CSS File | JS File | Rendered In |
|---|---|---|---|---|---|
| account | Account | [account.html](../templates/account/account.html) | [account.css](../assets/css/account/account.css) | assets/js/account/account.js | /account |
| account | Account header | [account_header.html](../templates/account/account_header.html) | [account_header.css](../assets/css/account/account_header.css) | assets/js/account/account.js | /account |
| account | Account order card | [account_order_card.html](../templates/account/account_order_card.html) | [account_order_card.css](../assets/css/account/account_order_card.css) | assets/js/account/account.js | /account |
| account | Account orders | [account_orders.html](../templates/account/account_orders.html) | [account_orders.css](../assets/css/account/account_orders.css) | assets/js/account/account.js | /account |
| account | Account password | [account_password.html](../templates/account/account_password.html) | [account_password.css](../assets/css/account/account_password.css) | assets/js/account/account.js | /account |
| account | Account profile | [account_profile.html](../templates/account/account_profile.html) | [account_profile.css](../assets/css/account/account_profile.css) | assets/js/account/account.js | /account |
| account | Account saved | [account_saved.html](../templates/account/account_saved.html) | [account_saved.css](../assets/css/account/account_saved.css) | assets/js/account/account.js | /account |
| account | Account saved item | [account_saved_item.html](../templates/account/account_saved_item.html) | [account_saved_item.css](../assets/css/account/account_saved_item.css) | assets/js/account/account.js | /account |
| admin | Admin | [admin.html](../templates/admin/admin.html) | [admin.css](../assets/css/admin/admin.css) | assets/js/admin/admin.js | /admin |
| admin | Admin sidebar navigation | [admin_aside.html](../templates/admin/admin_aside.html) | [admin_aside.css](../assets/css/admin/admin_aside.css) | assets/js/admin/admin.js | /admin |
| admin | Admin customer | [admin_customer.html](../templates/admin/admin_customer.html) | [admin_customer.css](../assets/css/admin/admin_customer.css) | assets/js/admin/admin.js | /admin |
| admin | Admin customers | [admin_customers.html](../templates/admin/admin_customers.html) | [admin_customers.css](../assets/css/admin/admin_customers.css) | assets/js/admin/admin.js | /admin |
| admin | Admin header | [admin_header.html](../templates/admin/admin_header.html) | [admin_header.css](../assets/css/admin/admin_header.css) | assets/js/admin/admin.js | /admin |
| admin | Admin notifications | [admin_notifications.html](../templates/admin/admin_notifications.html) | [admin_notifications.css](../assets/css/admin/admin_notifications.css) | assets/js/admin/admin.js | /admin |
| admin | Admin order status | [admin_order_status.html](../templates/admin/admin_order_status.html) | [admin_order_status.css](../assets/css/admin/admin_order_status.css) | assets/js/admin/admin.js | /admin |
| admin | Overview dashboard | [admin_overview.html](../templates/admin/admin_overview.html) | [admin_overview.css](../assets/css/admin/admin_overview.css) | assets/js/admin/admin.js | /admin |
| admin | Admin product | [admin_product.html](../templates/admin/admin_product.html) | [admin_product.css](../assets/css/admin/admin_product.css) | assets/js/admin/admin.js | /admin |
| admin | Product editor dialog | [admin_product_form.html](../templates/admin/admin_product_form.html) | [admin_product_form.css](../assets/css/admin/admin_product_form.css) | assets/js/admin/admin.js | /admin |
| admin | Admin products | [admin_products.html](../templates/admin/admin_products.html) | [admin_products.css](../assets/css/admin/admin_products.css) | assets/js/admin/admin.js | /admin |
| admin | Admin recent sale | [admin_recent_sale.html](../templates/admin/admin_recent_sale.html) | [admin_recent_sale.css](../assets/css/admin/admin_recent_sale.css) | assets/js/admin/admin.js | /admin |
| admin | Admin sale row | [admin_sale_row.html](../templates/admin/admin_sale_row.html) | [admin_sale_row.css](../assets/css/admin/admin_sale_row.css) | assets/js/admin/admin.js | /admin |
| admin | Admin sales | [admin_sales.html](../templates/admin/admin_sales.html) | [admin_sales.css](../assets/css/admin/admin_sales.css) | assets/js/admin/admin.js | /admin |
| admin | Admin settings | [admin_settings.html](../templates/admin/admin_settings.html) | [admin_settings.css](../assets/css/admin/admin_settings.css) | assets/js/admin/admin.js | /admin |
| admin | Admin sidebar backdrop | [admin_sidebar_backdrop.html](../templates/admin/admin_sidebar_backdrop.html) | [admin_sidebar_backdrop.css](../assets/css/admin/admin_sidebar_backdrop.css) | assets/js/admin/admin.js | /admin |
| auth | Auth | [auth.html](../templates/auth/auth.html) | [auth.css](../assets/css/auth/auth.css) | assets/js/auth/auth.js | /login, /register, /reset-password |
| auth | Auth artwork | [auth_artwork.html](../templates/auth/auth_artwork.html) | [auth_artwork.css](../assets/css/auth/auth_artwork.css) | assets/js/auth/auth.js | /login, /register, /reset-password |
| auth | Auth form | [auth_form.html](../templates/auth/auth_form.html) | [auth_form.css](../assets/css/auth/auth_form.css) | assets/js/auth/auth.js | /login, /register, /reset-password |
| auth | Auth header | [auth_header.html](../templates/auth/auth_header.html) | [auth_header.css](../assets/css/auth/auth_header.css) | assets/js/auth/auth.js | /login, /register, /reset-password |
| auth | Customer/admin role switcher | [auth_roles.html](../templates/auth/auth_roles.html) | [auth_roles.css](../assets/css/auth/auth_roles.css) | assets/js/auth/auth.js | /login, /register, /reset-password |
| catalog | Full catalog, product templates, cart, and checkout | [catalog.html](../templates/catalog/catalog.html) | [catalog.css](../assets/css/catalog/catalog.css) | assets/js/catalog/catalog.js | /shop |
| chatbot | Floating support button and component composition | [chatbot.html](../templates/chatbot/chatbot.html) | [chatbot.css](../assets/css/chatbot/chatbot.css) | assets/js/chatbot/chatbot.js; assets/js/chatbot/chatbot_ui.js; assets/js/chatbot/chatbot_api.js | Landing, catalog, tuner and lessons |
| chatbot | Assistant/customer message | [chatbot_message.html](../templates/chatbot/chatbot_message.html) | [chatbot_message.css](../assets/css/chatbot/chatbot_message.css) | assets/js/chatbot/chatbot.js; assets/js/chatbot/chatbot_ui.js; assets/js/chatbot/chatbot_api.js | Landing, catalog, tuner and lessons |
| chatbot | Chat panel | [chatbot_panel.html](../templates/chatbot/chatbot_panel.html) | [chatbot_panel.css](../assets/css/chatbot/chatbot_panel.css) | assets/js/chatbot/chatbot.js; assets/js/chatbot/chatbot_ui.js; assets/js/chatbot/chatbot_api.js | Landing, catalog, tuner and lessons |
| chatbot | Chat suggestions | [chatbot_suggestions.html](../templates/chatbot/chatbot_suggestions.html) | [chatbot_suggestions.css](../assets/css/chatbot/chatbot_suggestions.css) | assets/js/chatbot/chatbot.js; assets/js/chatbot/chatbot_ui.js; assets/js/chatbot/chatbot_api.js | Landing, catalog, tuner and lessons |
| landing | Landing | [landing.html](../templates/landing/landing.html) | [landing.css](../assets/css/landing/landing.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing categories | [landing_categories.html](../templates/landing/landing_categories.html) | [landing_categories.css](../assets/css/landing/landing_categories.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing footer | [landing_footer.html](../templates/landing/landing_footer.html) | [landing_footer.css](../assets/css/landing/landing_footer.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing header | [landing_header.html](../templates/landing/landing_header.html) | [landing_header.css](../assets/css/landing/landing_header.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing hero | [landing_hero.html](../templates/landing/landing_hero.html) | [landing_hero.css](../assets/css/landing/landing_hero.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing join | [landing_join.html](../templates/landing/landing_join.html) | [landing_join.css](../assets/css/landing/landing_join.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing overview | [landing_overview.html](../templates/landing/landing_overview.html) | [landing_overview.css](../assets/css/landing/landing_overview.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| landing | Landing steps | [landing_steps.html](../templates/landing/landing_steps.html) | [landing_steps.css](../assets/css/landing/landing_steps.css) | assets/js/shared/app.js (navigation/theme); assets/js/shared/shared.js (reveals) | / |
| lessons | Lessons | [lessons.html](../templates/lessons/lessons.html) | [lessons.css](../assets/css/lessons/lessons.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Lessons chord detail | [lessons_chord_detail.html](../templates/lessons/lessons_chord_detail.html) | [lessons_chord_detail.css](../assets/css/lessons/lessons_chord_detail.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Chord diagram macro | [lessons_chord_diagram.html](../templates/lessons/lessons_chord_diagram.html) | [lessons_chord_diagram.css](../assets/css/lessons/lessons_chord_diagram.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Lessons chords | [lessons_chords.html](../templates/lessons/lessons_chords.html) | [lessons_chords.css](../assets/css/lessons/lessons_chords.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Lessons getting started | [lessons_getting_started.html](../templates/lessons/lessons_getting_started.html) | [lessons_getting_started.css](../assets/css/lessons/lessons_getting_started.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Lessons strumming | [lessons_strumming.html](../templates/lessons/lessons_strumming.html) | [lessons_strumming.css](../assets/css/lessons/lessons_strumming.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| lessons | Strumming pattern diagram | [lessons_strumming_pattern.html](../templates/lessons/lessons_strumming_pattern.html) | [lessons_strumming_pattern.css](../assets/css/lessons/lessons_strumming_pattern.css) | No lesson controller: Jinja renders the content; assets/js/shared/app.js handles navigation/theme | /lessons and lesson subpages |
| search_filter | Search, sorting, type filters, and Guitar Finder | [search_filter.html](../templates/search_filter/search_filter.html) | [search_filter.css](../assets/css/search_filter/search_filter.css) | assets/js/search_filter/search_filter.js | /shop |
| shared | Global HTML shell | [base.html](../templates/shared/base.html) | [base.css](../assets/css/shared/base.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Shared template composition | [components.html](../templates/shared/components.html) | [components.css](../assets/css/shared/components.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Dialog shell | [dialog.html](../templates/shared/dialog.html) | [dialog.css](../assets/css/shared/dialog.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Reusable native SVG icon templates | [icons.html](../templates/shared/icons.html) | [icons.css](../assets/css/shared/icons.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Order detail dialog | [order_detail.html](../templates/shared/order_detail.html) | [order_detail.css](../assets/css/shared/order_detail.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Practice page shell | [practice_base.html](../templates/shared/practice_base.html) | [practice_base.css](../assets/css/shared/practice_base.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| shared | Practice navigation strip | [practice_links.html](../templates/shared/practice_links.html) | [practice_links.css](../assets/css/shared/practice_links.css) | assets/js/shared/app.js; assets/js/shared/shared.js; assets/js/shared/theme.js | Shared layout; dialogs in catalog/account/admin; practice layout in tuner/lessons |
| tuner | Tuner | [tuner.html](../templates/tuner/tuner.html) | [tuner.css](../assets/css/tuner/tuner.css) | assets/js/tuner/tuner.js (pitch: assets/js/tuner/tuner_pitch.js) | /tuner |
| tuner | Tuner meter | [tuner_meter.html](../templates/tuner/tuner_meter.html) | [tuner_meter.css](../assets/css/tuner/tuner_meter.css) | assets/js/tuner/tuner.js (pitch: assets/js/tuner/tuner_pitch.js) | /tuner |
| tuner | Tuner strings | [tuner_strings.html](../templates/tuner/tuner_strings.html) | [tuner_strings.css](../assets/css/tuner/tuner_strings.css) | assets/js/tuner/tuner.js (pitch: assets/js/tuner/tuner_pitch.js) | /tuner |

## Shared components and dynamic rendering

- `templates/shared/base.html` loads `assets/css/shared/shared.css`, the page stylesheet, chatbot CSS, and catalog search/filter CSS where applicable. `shared.css` owns the reset, fonts, themes, `.shell`, `.surface-card`, form/button primitives, order status tokens and common accessibility rules. It imports shared component sheets.

- `assets/css/shared/practice.css` is the common tuner/lesson typography sheet. Tuner and lessons import it, then `practice_base.css`, before their feature-specific sheets. Chord macro presentation belongs in `lessons_chord_diagram.css`; strumming diagram presentation belongs in `lessons_strumming_pattern.css`.

- Native `<template>` fragments are cloned by the existing controllers with `clone()` in `shared/shared.js`. The template IDs, `data-field`, `data-action`, element attributes and API wiring remain intact. Finder options/progress, admin sidebar links, saved hearts, selected auth roles and customer chat bubbles use named CSS state classes.

- Notices and empty results are small DOM constructors in `assets/js/shared/shared.js` (`notice()` and `empty()`), rather than HTML templates. Their exact CSS files are `assets/css/shared/notice.css` and `assets/css/shared/empty_state.css`. Order item text is generated by `orderDetails()`; its containing markup and presentation are in `shared/order_detail.html` and `shared/order_detail.css`.

- The admin revenue chart is native SVG generated by `assets/js/admin/admin.js` (`renderSummary()`); its SVG geometry and accessibility attributes remain data-driven. Chart layout/color rules are owned by `admin_overview.css`. Shared icon templates have native SVG geometry in `shared/icons.html` and inherit `currentColor`; `icons.css` is the matching edit point. Some composition-only CSS sheets document shared primitive ownership and intentionally add no redundant declarations. They are still imported by their module entry.

- Existing reveal/dismiss timing and initial keyframes remain in the Web Animations flow in `shared/shared.js`. Settled poses belong to `assets/css/shared/animations.css` through `data-motion-state` attributes. No inline style attributes are written. The tuner marker position is the one continuously numeric presentation value: `positionIndicator()` in `tuner.js` uses the native animation API, with timing read from `tuner_meter.css`; pitch detection is unchanged.

## How to Find and Debug a UI Component

1. Identify the visible component and look it up in the table. For example, the chat panel maps to `templates/chatbot/chatbot_panel.html` and `assets/css/chatbot/chatbot_panel.css`.
2. Inspect the element in browser DevTools. Component classes describe its role; `data-action`, `data-field` and template IDs identify interaction hooks. Read the file header for its matching CSS and controller.
3. For an appearance problem, open the matching CSS. Check base rules, hover/focus states, `.dark` context and media queries. Use DevTools Computed to see the winning declaration, including shared primitives. Catalog and search/filter each use one stylesheet; for other features, verify the module entry stylesheet imports the component file.
4. For missing dynamically rendered content, locate the matching `<template id="...-template">`, then search its controller for `clone("...")`, the relevant data hook or render function. Check Console and Network before changing any selectors.
5. For failed requests, trace the existing controller to its `/api/...` endpoint and module. Preserve template IDs, field names, CSRF/session handling and API contracts. The existing [backend debugging guide](../DEBUGGING_GUIDE.md) covers this trace.
6. Run the relevant browser test, then the Python suite. `tests/test_frontend.py` checks the original DOM attributes, backend hashes, matching sheets, imports and utility removal. Visual captures use disposable data and mocked chat responses.

See [FRONTEND_REFACTOR_REPORT.md](FRONTEND_REFACTOR_REPORT.md) for the complete inspected/changed file inventory and validation results. Earlier architecture/component reports are historical snapshots; this document is the current frontend map.

## Catalog and search/filter sections

Search for `SECTION:` in the HTML or CSS file to jump between parts.

- `templates/catalog/catalog.html`: announcement, header, hero, categories, products, bundles, tracking, guarantees, footer, product card, navigation, support, cart, and checkout.
- `assets/css/catalog/catalog.css`: all catalog styles, grouped under the same section names.
- `templates/search_filter/search_filter.html`: toolbar (search/sort), type chips, Finder banner, and Finder dialog/templates.
- `assets/css/search_filter/search_filter.css`: all search/filter and Finder styles.

`catalog.html` includes the same `search_filter.html` file in four places.
The nearby `{% with search_filter_section='toolbar' %}` (or `types`, `banner`,
`finder`) chooses its labeled section. This keeps the controls in their existing
positions while all search/filter markup stays in one file. Shared layout and
chatbot templates remain in their own feature folders.
