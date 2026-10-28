# AUDIA frontend refactor implementation report

October 20 follow-up: repeated component rules and generated styling variables
have been simplified. Shared colors and browser defaults now live in
`assets/css/shared/theme.css` and `assets/css/shared/reset.css`. Page backgrounds
and component adjustments belong to their own files. See
[CSS_EDITING_GUIDE.md](CSS_EDITING_GUIDE.md) for the current editing workflow.
Catalog and search/filter have since been consolidated into one HTML/CSS pair
per feature; their former fragments map to those files in
`frontend-consolidation.json`.
The counts and inventories below describe the October 15 conversion.

Completed October 15, 2026. The existing Flask project now uses conventional component CSS and matching HTML/CSS files inside the existing feature folders. No original folder or file was moved or renamed. All 26 Python application/module files and `requirements.txt` match their inspected hashes. All 45 routes and 7 blueprints retain their original contracts.

## 1. Files inspected

The original runtime inventory contains 78 files: 27 HTML templates, 11 CSS stylesheets, 13 JavaScript modules, 26 Python application/module files and `requirements.txt`. Inspection covered Jinja inheritance/includes, native template cloning, dynamic classes, SVG generation, theme/state selectors, animation poses, microphone UI wiring, static imports, routes and API handlers. Supporting files reviewed include README, DEBUGGING_GUIDE, PROJECT_STRUCTURE, existing component/architecture manifests, test fixtures and the Python/browser suites.

<details><summary>Complete original runtime file inventory</summary>

- [app.py](../app.py)
- [assets/css/account/account.css](../assets/css/account/account.css)
- [assets/css/admin/admin.css](../assets/css/admin/admin.css)
- [assets/css/auth/auth.css](../assets/css/auth/auth.css)
- [assets/css/catalog/catalog.css](../assets/css/catalog/catalog.css)
- [assets/css/chatbot/chatbot.css](../assets/css/chatbot/chatbot.css)
- [assets/css/landing/landing.css](../assets/css/landing/landing.css)
- [assets/css/lessons/lessons.css](../assets/css/lessons/lessons.css)
- [assets/css/search_filter/search_filter.css](../assets/css/search_filter/search_filter.css)
- [assets/css/shared/practice.css](../assets/css/shared/practice.css)
- [assets/css/shared/shared.css](../assets/css/shared/shared.css)
- [assets/css/tuner/tuner.css](../assets/css/tuner/tuner.css)
- [assets/js/account/account.js](../assets/js/account/account.js)
- [assets/js/admin/admin.js](../assets/js/admin/admin.js)
- [assets/js/auth/auth.js](../assets/js/auth/auth.js)
- [assets/js/catalog/catalog.js](../assets/js/catalog/catalog.js)
- [assets/js/chatbot/chatbot.js](../assets/js/chatbot/chatbot.js)
- [assets/js/chatbot/chatbot_api.js](../assets/js/chatbot/chatbot_api.js)
- [assets/js/chatbot/chatbot_ui.js](../assets/js/chatbot/chatbot_ui.js)
- [assets/js/search_filter/search_filter.js](../assets/js/search_filter/search_filter.js)
- [assets/js/shared/app.js](../assets/js/shared/app.js)
- [assets/js/shared/shared.js](../assets/js/shared/shared.js)
- [assets/js/shared/theme.js](../assets/js/shared/theme.js)
- [assets/js/tuner/tuner.js](../assets/js/tuner/tuner.js)
- [assets/js/tuner/tuner_pitch.js](../assets/js/tuner/tuner_pitch.js)
- [modules/__init__.py](../modules/__init__.py)
- [modules/admin/__init__.py](../modules/admin/__init__.py)
- [modules/admin/admin.py](../modules/admin/admin.py)
- [modules/auth/__init__.py](../modules/auth/__init__.py)
- [modules/auth/auth.py](../modules/auth/auth.py)
- [modules/auth/auth_mail.py](../modules/auth/auth_mail.py)
- [modules/catalog/__init__.py](../modules/catalog/__init__.py)
- [modules/catalog/catalog.py](../modules/catalog/catalog.py)
- [modules/chatbot/__init__.py](../modules/chatbot/__init__.py)
- [modules/chatbot/ai/__init__.py](../modules/chatbot/ai/__init__.py)
- [modules/chatbot/ai/ai.py](../modules/chatbot/ai/ai.py)
- [modules/chatbot/ai/ai_rag_sync.py](../modules/chatbot/ai/ai_rag_sync.py)
- [modules/chatbot/chatbot.py](../modules/chatbot/chatbot.py)
- [modules/database/__init__.py](../modules/database/__init__.py)
- [modules/database/connection.py](../modules/database/connection.py)
- [modules/database/models.py](../modules/database/models.py)
- [modules/lessons/__init__.py](../modules/lessons/__init__.py)
- [modules/lessons/lessons.py](../modules/lessons/lessons.py)
- [modules/lessons/lessons_data.py](../modules/lessons/lessons_data.py)
- [modules/orders/__init__.py](../modules/orders/__init__.py)
- [modules/orders/orders.py](../modules/orders/orders.py)
- [modules/search_filter/__init__.py](../modules/search_filter/__init__.py)
- [modules/search_filter/search_filter.py](../modules/search_filter/search_filter.py)
- [modules/tuner/__init__.py](../modules/tuner/__init__.py)
- [modules/tuner/tuner.py](../modules/tuner/tuner.py)
- [requirements.txt](../requirements.txt)
- [templates/account/account.html](../templates/account/account.html)
- [templates/admin/admin.html](../templates/admin/admin.html)
- [templates/auth/auth.html](../templates/auth/auth.html)
- [templates/catalog/catalog.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_bundle.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_checkout.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_navigation.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_product_card.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_support.html](../templates/catalog/catalog.html)
- [templates/chatbot/chatbot.html](../templates/chatbot/chatbot.html)
- [templates/landing/landing.html](../templates/landing/landing.html)
- [templates/lessons/lessons.html](../templates/lessons/lessons.html)
- [templates/lessons/lessons_chord_detail.html](../templates/lessons/lessons_chord_detail.html)
- [templates/lessons/lessons_chord_diagram.html](../templates/lessons/lessons_chord_diagram.html)
- [templates/lessons/lessons_chords.html](../templates/lessons/lessons_chords.html)
- [templates/lessons/lessons_getting_started.html](../templates/lessons/lessons_getting_started.html)
- [templates/lessons/lessons_strumming.html](../templates/lessons/lessons_strumming.html)
- [templates/search_filter/search_filter.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder_banner.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_types.html](../templates/search_filter/search_filter.html)
- [templates/shared/base.html](../templates/shared/base.html)
- [templates/shared/components.html](../templates/shared/components.html)
- [templates/shared/practice_base.html](../templates/shared/practice_base.html)
- [templates/shared/practice_links.html](../templates/shared/practice_links.html)
- [templates/tuner/tuner.html](../templates/tuner/tuner.html)

</details>

## 2. HTML files updated or created

Updated 27 existing templates; created 61 component partials. There are now 88 matching HTML/CSS pairs. Parent pages compose named includes; native template IDs, original form/data attributes and SVG geometry remain intact. The aggregate DOM contract preserves all 1,563 original elements except their intentionally replaced class collections. File headers identify each component, CSS and controller.

<details><summary>Updated HTML files</summary>

- [templates/account/account.html](../templates/account/account.html)
- [templates/admin/admin.html](../templates/admin/admin.html)
- [templates/auth/auth.html](../templates/auth/auth.html)
- [templates/catalog/catalog.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_bundle.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_checkout.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_navigation.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_product_card.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_support.html](../templates/catalog/catalog.html)
- [templates/chatbot/chatbot.html](../templates/chatbot/chatbot.html)
- [templates/landing/landing.html](../templates/landing/landing.html)
- [templates/lessons/lessons.html](../templates/lessons/lessons.html)
- [templates/lessons/lessons_chord_detail.html](../templates/lessons/lessons_chord_detail.html)
- [templates/lessons/lessons_chord_diagram.html](../templates/lessons/lessons_chord_diagram.html)
- [templates/lessons/lessons_chords.html](../templates/lessons/lessons_chords.html)
- [templates/lessons/lessons_getting_started.html](../templates/lessons/lessons_getting_started.html)
- [templates/lessons/lessons_strumming.html](../templates/lessons/lessons_strumming.html)
- [templates/search_filter/search_filter.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder_banner.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_types.html](../templates/search_filter/search_filter.html)
- [templates/shared/base.html](../templates/shared/base.html)
- [templates/shared/components.html](../templates/shared/components.html)
- [templates/shared/practice_base.html](../templates/shared/practice_base.html)
- [templates/shared/practice_links.html](../templates/shared/practice_links.html)
- [templates/tuner/tuner.html](../templates/tuner/tuner.html)

</details>

<details><summary>Created HTML files</summary>

- [templates/account/account_header.html](../templates/account/account_header.html)
- [templates/account/account_order_card.html](../templates/account/account_order_card.html)
- [templates/account/account_orders.html](../templates/account/account_orders.html)
- [templates/account/account_password.html](../templates/account/account_password.html)
- [templates/account/account_profile.html](../templates/account/account_profile.html)
- [templates/account/account_saved.html](../templates/account/account_saved.html)
- [templates/account/account_saved_item.html](../templates/account/account_saved_item.html)
- [templates/admin/admin_aside.html](../templates/admin/admin_aside.html)
- [templates/admin/admin_customer.html](../templates/admin/admin_customer.html)
- [templates/admin/admin_customers.html](../templates/admin/admin_customers.html)
- [templates/admin/admin_header.html](../templates/admin/admin_header.html)
- [templates/admin/admin_notifications.html](../templates/admin/admin_notifications.html)
- [templates/admin/admin_order_status.html](../templates/admin/admin_order_status.html)
- [templates/admin/admin_overview.html](../templates/admin/admin_overview.html)
- [templates/admin/admin_product.html](../templates/admin/admin_product.html)
- [templates/admin/admin_product_form.html](../templates/admin/admin_product_form.html)
- [templates/admin/admin_products.html](../templates/admin/admin_products.html)
- [templates/admin/admin_recent_sale.html](../templates/admin/admin_recent_sale.html)
- [templates/admin/admin_sale_row.html](../templates/admin/admin_sale_row.html)
- [templates/admin/admin_sales.html](../templates/admin/admin_sales.html)
- [templates/admin/admin_settings.html](../templates/admin/admin_settings.html)
- [templates/admin/admin_sidebar_backdrop.html](../templates/admin/admin_sidebar_backdrop.html)
- [templates/auth/auth_artwork.html](../templates/auth/auth_artwork.html)
- [templates/auth/auth_form.html](../templates/auth/auth_form.html)
- [templates/auth/auth_header.html](../templates/auth/auth_header.html)
- [templates/auth/auth_roles.html](../templates/auth/auth_roles.html)
- [templates/catalog/catalog_announcement.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_bundles.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart_badge.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart_empty.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart_item.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_cart_items.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_categories.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_footer.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_guarantees.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_header.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_hero.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_products.html](../templates/catalog/catalog.html)
- [templates/catalog/catalog_tracking.html](../templates/catalog/catalog.html)
- [templates/chatbot/chatbot_message.html](../templates/chatbot/chatbot_message.html)
- [templates/chatbot/chatbot_panel.html](../templates/chatbot/chatbot_panel.html)
- [templates/chatbot/chatbot_suggestions.html](../templates/chatbot/chatbot_suggestions.html)
- [templates/landing/landing_categories.html](../templates/landing/landing_categories.html)
- [templates/landing/landing_footer.html](../templates/landing/landing_footer.html)
- [templates/landing/landing_header.html](../templates/landing/landing_header.html)
- [templates/landing/landing_hero.html](../templates/landing/landing_hero.html)
- [templates/landing/landing_join.html](../templates/landing/landing_join.html)
- [templates/landing/landing_overview.html](../templates/landing/landing_overview.html)
- [templates/landing/landing_steps.html](../templates/landing/landing_steps.html)
- [templates/lessons/lessons_strumming_pattern.html](../templates/lessons/lessons_strumming_pattern.html)
- [templates/search_filter/search_filter_check.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder_match.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder_option.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_finder_results.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_search.html](../templates/search_filter/search_filter.html)
- [templates/search_filter/search_filter_sort.html](../templates/search_filter/search_filter.html)
- [templates/shared/dialog.html](../templates/shared/dialog.html)
- [templates/shared/icons.html](../templates/shared/icons.html)
- [templates/shared/order_detail.html](../templates/shared/order_detail.html)
- [templates/tuner/tuner_meter.html](../templates/tuner/tuner_meter.html)
- [templates/tuner/tuner_strings.html](../templates/tuner/tuner_strings.html)

</details>

## 3. CSS files updated or created

Updated 11 original stylesheets; created 82 component/shared sheets. All 93 CSS files are connected through existing page links and module imports. Component declarations are consolidated into cohesive blocks; responsive, hover, focus and dark rules preserve the inspected definitions and cascade. Global reset, fonts, themes, reusable form/button primitives and common status tokens remain shared. Comment-only composition/native-icon sheets document their shared owners and remain imported edit points.

<details><summary>Updated CSS files</summary>

- [assets/css/account/account.css](../assets/css/account/account.css)
- [assets/css/admin/admin.css](../assets/css/admin/admin.css)
- [assets/css/auth/auth.css](../assets/css/auth/auth.css)
- [assets/css/catalog/catalog.css](../assets/css/catalog/catalog.css)
- [assets/css/chatbot/chatbot.css](../assets/css/chatbot/chatbot.css)
- [assets/css/landing/landing.css](../assets/css/landing/landing.css)
- [assets/css/lessons/lessons.css](../assets/css/lessons/lessons.css)
- [assets/css/search_filter/search_filter.css](../assets/css/search_filter/search_filter.css)
- [assets/css/shared/practice.css](../assets/css/shared/practice.css)
- [assets/css/shared/shared.css](../assets/css/shared/shared.css)
- [assets/css/tuner/tuner.css](../assets/css/tuner/tuner.css)

</details>

<details><summary>Created CSS files</summary>

- [assets/css/account/account_header.css](../assets/css/account/account_header.css)
- [assets/css/account/account_order_card.css](../assets/css/account/account_order_card.css)
- [assets/css/account/account_orders.css](../assets/css/account/account_orders.css)
- [assets/css/account/account_password.css](../assets/css/account/account_password.css)
- [assets/css/account/account_profile.css](../assets/css/account/account_profile.css)
- [assets/css/account/account_saved.css](../assets/css/account/account_saved.css)
- [assets/css/account/account_saved_item.css](../assets/css/account/account_saved_item.css)
- [assets/css/admin/admin_aside.css](../assets/css/admin/admin_aside.css)
- [assets/css/admin/admin_customer.css](../assets/css/admin/admin_customer.css)
- [assets/css/admin/admin_customers.css](../assets/css/admin/admin_customers.css)
- [assets/css/admin/admin_header.css](../assets/css/admin/admin_header.css)
- [assets/css/admin/admin_notifications.css](../assets/css/admin/admin_notifications.css)
- [assets/css/admin/admin_order_status.css](../assets/css/admin/admin_order_status.css)
- [assets/css/admin/admin_overview.css](../assets/css/admin/admin_overview.css)
- [assets/css/admin/admin_product.css](../assets/css/admin/admin_product.css)
- [assets/css/admin/admin_product_form.css](../assets/css/admin/admin_product_form.css)
- [assets/css/admin/admin_products.css](../assets/css/admin/admin_products.css)
- [assets/css/admin/admin_recent_sale.css](../assets/css/admin/admin_recent_sale.css)
- [assets/css/admin/admin_sale_row.css](../assets/css/admin/admin_sale_row.css)
- [assets/css/admin/admin_sales.css](../assets/css/admin/admin_sales.css)
- [assets/css/admin/admin_settings.css](../assets/css/admin/admin_settings.css)
- [assets/css/admin/admin_sidebar_backdrop.css](../assets/css/admin/admin_sidebar_backdrop.css)
- [assets/css/auth/auth_artwork.css](../assets/css/auth/auth_artwork.css)
- [assets/css/auth/auth_form.css](../assets/css/auth/auth_form.css)
- [assets/css/auth/auth_header.css](../assets/css/auth/auth_header.css)
- [assets/css/auth/auth_roles.css](../assets/css/auth/auth_roles.css)
- [assets/css/catalog/catalog_announcement.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_bundle.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_bundles.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_cart.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_cart_badge.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_cart_empty.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_cart_item.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_cart_items.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_categories.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_checkout.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_footer.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_guarantees.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_header.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_hero.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_navigation.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_product_card.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_products.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_support.css](../assets/css/catalog/catalog.css)
- [assets/css/catalog/catalog_tracking.css](../assets/css/catalog/catalog.css)
- [assets/css/chatbot/chatbot_message.css](../assets/css/chatbot/chatbot_message.css)
- [assets/css/chatbot/chatbot_panel.css](../assets/css/chatbot/chatbot_panel.css)
- [assets/css/chatbot/chatbot_suggestions.css](../assets/css/chatbot/chatbot_suggestions.css)
- [assets/css/landing/landing_categories.css](../assets/css/landing/landing_categories.css)
- [assets/css/landing/landing_footer.css](../assets/css/landing/landing_footer.css)
- [assets/css/landing/landing_header.css](../assets/css/landing/landing_header.css)
- [assets/css/landing/landing_hero.css](../assets/css/landing/landing_hero.css)
- [assets/css/landing/landing_join.css](../assets/css/landing/landing_join.css)
- [assets/css/landing/landing_overview.css](../assets/css/landing/landing_overview.css)
- [assets/css/landing/landing_steps.css](../assets/css/landing/landing_steps.css)
- [assets/css/lessons/lessons_chord_detail.css](../assets/css/lessons/lessons_chord_detail.css)
- [assets/css/lessons/lessons_chord_diagram.css](../assets/css/lessons/lessons_chord_diagram.css)
- [assets/css/lessons/lessons_chords.css](../assets/css/lessons/lessons_chords.css)
- [assets/css/lessons/lessons_getting_started.css](../assets/css/lessons/lessons_getting_started.css)
- [assets/css/lessons/lessons_strumming.css](../assets/css/lessons/lessons_strumming.css)
- [assets/css/lessons/lessons_strumming_pattern.css](../assets/css/lessons/lessons_strumming_pattern.css)
- [assets/css/search_filter/search_filter_check.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_finder.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_finder_banner.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_finder_match.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_finder_option.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_finder_results.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_search.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_sort.css](../assets/css/search_filter/search_filter.css)
- [assets/css/search_filter/search_filter_types.css](../assets/css/search_filter/search_filter.css)
- [assets/css/shared/animations.css](../assets/css/shared/animations.css)
- [assets/css/shared/base.css](../assets/css/shared/base.css)
- [assets/css/shared/components.css](../assets/css/shared/components.css)
- [assets/css/shared/dialog.css](../assets/css/shared/dialog.css)
- [assets/css/shared/empty_state.css](../assets/css/shared/empty_state.css)
- [assets/css/shared/icons.css](../assets/css/shared/icons.css)
- [assets/css/shared/notice.css](../assets/css/shared/notice.css)
- [assets/css/shared/order_detail.css](../assets/css/shared/order_detail.css)
- [assets/css/shared/practice_base.css](../assets/css/shared/practice_base.css)
- [assets/css/shared/practice_links.css](../assets/css/shared/practice_links.css)
- [assets/css/tuner/tuner_meter.css](../assets/css/tuner/tuner_meter.css)
- [assets/css/tuner/tuner_strings.css](../assets/css/tuner/tuner_strings.css)

</details>

## 4. Tailwind dependencies removed

- Removed the compiled utility selector bundle from `assets/css/shared/shared.css` and replaced active template/JavaScript utility collections with named component and state classes.
- Removed Tailwind-specific `--tw-*` names; exact design values now use ordinary declarations and CSS custom properties. No utility selectors, variant classes, Tailwind directives or unnecessary inline styles remain in the active frontend.
- Inspection found no Tailwind CDN script, package manifest dependency, configuration file or build pipeline to uninstall. No frontend framework, package or build step was introduced. The existing Google Fonts import remains intact.
- Historical source attribution: the supplied stylesheet identified its generated reset/declarations as “tailwindcss v3.4.19 | MIT License | https://tailwindcss.com”. This is historical attribution, not a runtime dependency. Older documentation snapshots may also contain original utility markup; they are not loaded by the application.

## 5. Modules converted

| Module | Component boundaries |
|---|---|
| Catalog | Delivery banner, header/navigation, hero, categories, product grid/card, bundles, tracking, guarantees, footer/support, cart/badge/items/empty state and checkout |
| Search/filter | Search input, sort select, type chips, Finder banner, budget/options/progress/results/match and check icon |
| Chatbot | Floating toggle, panel/header/input, suggestions and assistant/customer messages |
| Tuner | Interface/controls, meter and standard tuning string cards |
| Lessons | Overview, getting started, chord list/detail, chord diagram macro, strumming lesson and pattern diagram |
| Landing | Header, hero, overview, categories, steps, join and footer |
| Auth | Artwork, header, role switcher and form; login/register/recovery/reset modes remain in the existing controller |
| Account | Header, profile/password forms, orders/order cards and saved instruments/items |
| Admin | Sidebar/header, overview/recent sales, products/editor/cards, sales/rows, customers/cards, settings, notifications, order status and mobile backdrop |
| Shared | Global/practice shell, practice links, icons, dialogs, order details, animation states and generated notices/empty results |

## 6. Component-to-file mapping

Use [FRONTEND_COMPONENT_MAP.md](FRONTEND_COMPONENT_MAP.md). Its 88-row table identifies actual HTML, CSS, controller and rendered pages. “How to Find and Debug a UI Component” explains the DevTools → matching file → controller → API trace. README and DEBUGGING_GUIDE link to this current map.

Dynamic rendering exceptions are documented there: shared notice/empty DOM constructors, order item text, native icon/diagram geometry, the admin revenue SVG, initial/dismiss Web Animation keyframes and continuously numeric tuner marker positioning. Shared/composition-only rules are explicitly identified.

## 7. Necessary JavaScript styling adjustments

| File | Presentation wiring change |
|---|---|
| `assets/js/auth/auth.js` | Selected/default role utility strings become `auth-roles__option--selected` and `auth-roles__option`. |
| `assets/js/search_filter/search_filter.js` | Finder option/progress utility strings become named default/selected/complete classes. |
| `assets/js/admin/admin.js` | Selected/default sidebar classes and open/closed translation classes become named component states. |
| `assets/js/catalog/catalog.js` | Saved heart color uses `is-saved`. |
| `assets/js/chatbot/chatbot_ui.js` | Customer bubble utility string becomes `chatbot-message--customer`. |
| `assets/js/shared/shared.js` | Settled reveal styles use CSS data states; initial/native timing and observer/dismiss flow are retained, with no inline style writes. |
| `assets/js/tuner/tuner.js` | Numeric marker positioning uses native animation presentation and CSS-owned timing; unchanged targets retain the current transition. Audio/pitch calculations remain untouched. |

The chatbot transport/controller, account controller, shared app/theme controllers and tuner pitch detector are byte-for-byte unchanged. No API calls, request bodies, CSRF/session handling or business workflows were rewritten.

## 8. Validation and tests

| Validation | Result |
|---|---|
| Python suite | 33 tests passed, including 4 new frontend contracts. |
| Backend and routing | 26 application/module hashes, dependency manifest, 45 routes and 7 blueprints preserved. |
| Markup/CSS inspection | 1,563 original non-class element contracts preserved; all 88 HTML/CSS pairs and 93-sheet import graph verified; Jinja templates compile. No utility/inline/component style blocks remain. |
| Page pixel comparisons | 56 original/refactored full-page captures at 375/1440 pixels, dark/light modes: passed existing strict pixel tolerance. |
| Dynamic component comparison | 84 original/refactored viewport/style cases across catalog, cart, checkout, Finder, account/orders, chat, admin tabs/dialogs and all auth modes: zero computed-style differences in the active components. |
| Focus, hover and animations | 20 original/refactored state cases: exact computed-style matches for catalog focus/hover, auth focus/hover, chat focus/suggestions, open mobile sidebar and normal-motion reveals, in both themes and widths. |
| Existing browser workflow suite | Passed registration/login/session/recovery/password, catalog/search/Finder, saved items, checkout/tracking, admin inventory/fulfillment/reporting/export/customers/settings/notifications and API failures. |
| Existing chatbot browser suite | Passed guest/member chat, Enter/Send/suggestions, safe Unicode/text rendering, empty/duplicate prevention, typing, scrolling, close/reopen, network/server/malformed responses and CSRF retry behavior. |
| Existing practice browser suite | Passed six strings, flat/sharp meter, silence recovery, microphone denial/busy/missing/unsupported/insecure cases, cancellation/restart/lifecycle cleanup, 8 SVG chord shapes and 130 layout/theme cases. |
| Pitch detector | 90 harmonic cases passed across six strings, three sample rates and tuning conditions, plus silence/noise/stabilization checks. Detector file unchanged. |
| Normal entry point | `.venv/Scripts/python.exe app.py` launched with a disposable SQLite database; GET `/login` returned 200 with the auth form. |
| Source hygiene | `git diff --check` passed. No original runtime file deleted, renamed or moved. |

Permanent guards: `tests/test_frontend.py`, `docs/frontend-contract.json` and `docs/frontend-conversion.json`. The earlier structure hash test now retains backend/unrelated byte checks while delegating intentionally changed frontend contracts to the new tests. The chord test accepts formatted SVG whitespace without changing geometry assertions; the meter test reads its actual rendered position.

Browser evidence is saved under ignored `test-results/frontend/`: original source copy, full-page `screens/`, `dynamic/`, `states/` and frozen synthetic API fixtures. The visual comparison scripts require these captured references in this workspace; the Python contracts and existing functional browser suites do not require the ignored original source copy. Fixtures use disposable databases and mocked chat replies, with no paid model requests or production data mutations. Theme comparisons settle paint/finite transitions first. Modal tests compare the active panel; its underlying page is independently covered by full-page cases.

## 9. Limitations and safe dynamic exceptions

No verified conversion blockers remain. Verification used Chromium on Windows; physical microphone hardware, Firefox/Safari and live Gemini responses were not exercised. Audio scenarios used controlled browser input and mocks. Initial/dismiss keyframes and numeric SVG/meter geometry remain in their existing presentation/data flows as documented; static component styling is in CSS.
