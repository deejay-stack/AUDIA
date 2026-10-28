# Editing the AUDIA interface

## Find the matching files

HTML controls the structure and written content. CSS controls colors, backgrounds,
spacing, and text size. Catalog and search/filter each use one HTML file and one CSS file. Their labeled
`SECTION` comments help you find each part. Other features keep matching component
files in two folders:

| What you want to edit | HTML | CSS |
| --- | --- | --- |
| Main tuner screen | [tuner.html](../templates/tuner/tuner.html) | [tuner.css](../assets/css/tuner/tuner.css) |
| Tuner meter and moving line | [tuner_meter.html](../templates/tuner/tuner_meter.html) | [tuner_meter.css](../assets/css/tuner/tuner_meter.css) |
| Six-string reference | [tuner_strings.html](../templates/tuner/tuner_strings.html) | [tuner_strings.css](../assets/css/tuner/tuner_strings.css) |
| Product card | [catalog.html](../templates/catalog/catalog.html) | [catalog.css](../assets/css/catalog/catalog.css) |
| Search, sorting, type chips, and Finder | [search_filter.html](../templates/search_filter/search_filter.html) | [search_filter.css](../assets/css/search_filter/search_filter.css) |
| Chat window | [chatbot_panel.html](../templates/chatbot/chatbot_panel.html) | [chatbot_panel.css](../assets/css/chatbot/chatbot_panel.css) |

For the catalog and search/filter section list and other components, use the [complete file map](FRONTEND_COMPONENT_MAP.md).
The comment at the top of each HTML file names its CSS and JavaScript files.
An `{% include 'tuner/tuner_meter.html' %}` line means that part of the page is
written in the named file. Open that file to edit that part.

## Make a component style change

1. Find the element in its HTML file.
2. Copy its class name and search for it in the matching CSS file.
3. Edit the property in that rule, save the file, and refresh the browser.

For example, the product name has `class="catalog-product-card__name"`.
Its text size is set by `font-size` in `.catalog-product-card__name` in
`catalog.css`. You can change that value directly. The repeated
underscores are just part of the class name; they have no special CSS behavior.

```css
/* Example edit in catalog.css */
.catalog-product-card__name {
  /* Keep the other existing properties. */
  font-size: 24px;
}
```

Use `color` for text, `background-color` for a solid background, and `font-size`
for text size. Change the existing declaration instead of adding another copy
of the rule at the bottom of the file. Keep layout, hover, and state rules in
that component's file. No CSS build command is needed.

## Light theme, dark theme, and changing states

A rule such as `.dark .chatbot-panel` applies when the dark theme is selected.
Edit that rule for the dark background. Edit `.chatbot-panel` for the default
background. The CSS files label these theme rules.

Tuner status changes as you play. In `tuner.css`, `.tuner-status` is the idle
appearance. The nearby rules with `data-tuning="in-tune"`, `"flat"`, or `"sharp"`
set its appearance during tuning. The meter's state colors are in
`tuner_meter.css`. A `:hover` rule applies while the pointer is over an element.

An `@media (max-width: 767px)` block applies only to screens that are 767 pixels
wide or smaller. Check that block when changing a mobile layout. Responsive
sizes and existing visual effects are retained to keep the design the same.

## Shared styles

| File | What belongs here |
| --- | --- |
| [theme.css](../assets/css/shared/theme.css) | Site-wide light and dark colors. `--muted` is secondary text, `--accent` is the highlight color, and `--surface` is the card color. |
| [shared.css](../assets/css/shared/shared.css) | Reusable buttons, cards, inputs, and page width. |
| [reset.css](../assets/css/shared/reset.css) | Browser defaults for basic HTML elements. |
| [practice.css](../assets/css/shared/practice.css) | Headings, cards, and links shared by tuner and lessons. |
| [practice_base.css](../assets/css/shared/practice_base.css) | Shared tuner/lessons header and page layout. |

`color: var(--muted)` uses the secondary text color from `theme.css`. To change
only one component, replace that component's `color` value with a color such
as `#70687c`. Edit `theme.css` when you want to change the shared color everywhere.

Catalog and search/filter have all their rules together in their own stylesheet.
Other features import their component styles at the top; those imports must
stay before CSS rules. Page backgrounds belong to the page's own CSS file;
the shared stylesheet no longer forces them through `#root > div`.

## When editing HTML text does not change the screen

Some HTML is a template that JavaScript fills with real data:

- Product names, descriptions, prices, and stock come from the database. Edit
  them through **Administration > Products**. Text inside
  `catalog.html` is the initial template content.
- Tuner notes, frequency, and status messages are updated by
  [tuner.js](../assets/js/tuner/tuner.js). Ordinary headings and preparation
  instructions are written in `tuner.html`.
- Lesson names, chord fingers, and strumming patterns come from
  [lessons_data.py](../modules/lessons/lessons_data.py).

Keep IDs and `data-action` / `data-field` attributes when editing HTML; the
existing JavaScript uses them to find controls and fill content.

If an edit still does not appear, save the file and use **Ctrl+F5**. In the browser,
right-click the element, choose **Inspect**, and look at **Styles**. A crossed-out
declaration means another rule supplies that property. Its filename is shown
beside the rule. Also check the selected theme, screen width, and component state.

## Check a change

Run the Python checks from the project folder:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
```

The browser check `node tests/css-editing.cjs` verifies that editing the component
rules above changes the actual screen in both themes at mobile and desktop
widths. It uses Playwright and the disposable server from `tests/serve.py`; its
sample CSS edits stay in memory and do not modify your files or real database.
