# Commerce and practice upgrade

Completed October 29, 2026 (Asia/Manila). The existing Flask application,
PostgreSQL configuration, branding, AI integration, URLs and working workflows
were extended in place. No runtime dependency was added.

## Features

- Checkout shows products/quantities, subtotal, free standard shipping and total
  with cents. COD is available. Card and e-wallet method cards are labelled
  previews, collect no card data, and cannot submit an order or a charge.
- COD orders save the payment method and a Pending payment record. Existing
  server prices, inventory row locks and per-customer idempotency remain intact.
  The browser preserves the request key for retries of the same checkout.
- Add-to-cart toasts, live cart badges, quantity/stock limits and cart navigation
  work through the existing cart. Restored quantities are clamped to current
  stock. Cart keyboard focus is contained, and Escape closes the drawer.
- Authenticated `/orders` provides My Orders, payment information, details,
  item/unit/line prices, a tracking timeline and an empty state.
- Customer order lists, open tracking dialogs and the admin order directory
  poll every 15 seconds while visible. Requests do not overlap; polling pauses
  while hidden and stops on navigation. No driver positions or delivery dates
  are invented.
- Admin Orders & payments retains search/filter/CSV, adds acceptance/rejection,
  fulfillment steps and explicit cash collection/refund confirmation. COD does
  not require advance payment. Collection requires Delivered status, an explicit
  confirmation and a receipt/verification note; it is audited with the actor and
  timestamp. Paid orders require an explicit completed offline refund before a
  refund is recorded. Preview/unsupported methods cannot be verified or dispatched.
- Order history stores status/payment events and UTC timestamps. Repeating an
  update does not add duplicate events or restock twice. An expected-status check
  prevents a stale admin form from overwriting a later change.
- AUDI has the exact accessible tooltip “Ask AUDI, Our AI Assistant”, opening and
  closing animation, Escape-to-close, improved readable bubbles, mobile input
  sizing, loading feedback and automatic scrolling. Existing Gemini/RAG,
  plain-text rendering, CSRF retry and request timeout remain intact.
- The real microphone tuner retains its existing YIN detector and smoothing.
  Acoustic/electric modes share E2/A2/D3/G3/B3/E4 standard targets. Electric mode
  admits quieter signals; local high/low-pass filtering and adequate sample
  windows support pitch analysis. Automatic targets and manual string buttons
  measure cents against the intended open string. Stop, navigation, hidden pages,
  permission errors and disconnection release audio resources.
- Lessons retain the original material and add 12 chord shapes (20 total), barre
  indicators, family/difficulty filters, nine courses across three levels, six
  strumming patterns, switching/fingerstyle/rhythm exercises, and three original
  eight-bar song studies. Completion is saved per user. No copyrighted song
  arrangement was copied.

## Bugs addressed

- Session reads used `session.setdefault()`, which marked Flask's cookie session
  modified even when the CSRF token existed. Permanent-cookie refresh also
  rewrote cookies on requests. Read-only session checks now avoid those stale
  concurrent writes; database session expiry remains authoritative.
- Browser history could restore frozen authenticated UI without revalidation.
  Restored pages now reload, and login/logout changes trigger revalidation in
  other tabs. Logout invalidates the stored session, clears cart/checkout state,
  and blocks repeated clicks. A session-fetch network error no longer causes a
  protected-page/login redirect loop.
- SQLite returned stored UTC timestamps without timezone information, making
  event responses inconsistent with newly created events. UTC serialization is
  now explicit for order dates, history and collection times.
- Non-object or non-text chatbot input could reach an attribute error or be
  coerced into an AI prompt. It now returns a validated 400 without calling AI;
  rollback only uses an existing request session.
- Tuner feedback formerly compared pitch only to the closest chromatic note.
  String-target feedback now makes the intended standard string explicit.

## Database changes and recovery

Three additive tables were created: `order_events`, `order_payments`, and
`lesson_progress`. No existing table/column was altered. A comparison of all
rows and columns in the 11 existing configured-database tables matched before
and after upgrading. `.env` and existing runtime secrets were not changed.

The reusable upgrade is:

```powershell
.venv\Scripts\python.exe -m flask --app app upgrade-db
```

It backs up existing table rows and column descriptions to private
`instance/backups/database-before-upgrade-*.json.gz`, then creates only missing
tables in a transaction. It is safe to repeat. Fresh databases use the existing
`init-db` command, which includes the new mappings. The configured database has
already been upgraded in this workspace.

`instance/backups/before-commerce-upgrade-20261029.zip` contains the source before
this feature pass, including the previous tests. The backup directory is ignored
by Git and is outside Flask's static assets. Database backups contain private
records; keep them private. Legacy orders keep their original dates; missing
historical status timestamps are explicitly shown as unavailable, and collection
is not inferred from Delivered status.

## Verification performed

- **36 applicable Python tests passed**: 20 existing app/security/order/admin
  checks, two AI/RAG checks with mocked provider calls, four practice checks, and
  ten targeted upgrade tests.
- Targeted coverage included COD pending/collection/refund, unsupported payment
  rejection, timestamp/idempotency behavior, ownership and admin authorization,
  invalid/stale transitions, repeated login/logout, cookie replay, read-only
  session cookies, malformed chat JSON, progress isolation, all new lesson/chord
  pages, and repeatable migrations preserving existing rows.
- Original pitch checks passed 90 harmonic cases across six strings and three
  sample rates, with silence/noise/weak-input/stabilization checks. Additional
  checks passed 48 manual-target/low-signal cases and six automatic targets.
- New chord shapes passed pitch-class checks, and all lesson pages rendered.
- Python compilation, JavaScript syntax/local imports, Jinja compilation,
  local CSS imports, original-route preservation and resource checks passed.
- Configured PostgreSQL `/api/health` returned 200 after upgrade. Test accounts,
  orders and collections used disposable SQLite, not live application records.

The earlier byte-for-byte organization and frontend snapshot contracts describe
an earlier UI and were retired with the obsolete reports. They were not used as
evidence that these intentional feature changes preserve old file bytes.

## Limitations

- Computer Use stopped before browser interaction because its policy check could
  not identify the current browser URL reliably. Desktop/mobile visual behavior,
  live focus interaction, and live polling in a real browser were not verified.
  Responsive rules and markup were inspected; this is not a substitute for a
  rendered device check.
- Physical guitar/microphone accuracy, device-specific permissions and acoustic
  conditions need a real instrument check. Algorithm tests use generated signals;
  application pitch values always come from microphone samples.
- Live Gemini responses were not called. The existing mocked integration passed;
  actual availability depends on existing credentials, models and network access.
- No payment gateway is connected. Only COD places orders; card/wallet cards are
  previews. Cash collection/refund records rely on an authorized administrator's
  explicit verification of the real offline action.

## Cleanup

After verification, removed `tests/`, `test-results/`, bytecode caches, generated
debug logs, historical architecture/component/organization reports, obsolete
frontend snapshot JSON/report files, and the two shared CSS files containing no
rules (`components.css`, `icons.css`). Their imports/references were updated.
Current source, assets, licenses, seed data, environment settings, runtime files,
editing/debugging guides and recovery backups were retained. Automated test code
is no longer shipped in the project, as requested; this report records its results.

## Main implementation files

Backend: `app.py`, database `models.py`/`migrations.py`, shared
`services/orders.py`, and the existing auth, orders, admin, chatbot and lessons
routes. Curriculum stays in `routes/lessons/lessons_data.py`.

Frontend: existing shared/app/account/catalog/admin/chatbot/tuner controllers,
new `assets/js/lessons/lessons.js`, checkout/order/admin/tuner/lesson templates,
new `templates/account/orders.html`, lesson practice/song pages, shared
`commerce.css` and focused additions to chatbot/tuner/lesson styles.

See [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) and
[DEBUGGING_GUIDE.md](../DEBUGGING_GUIDE.md) for navigation and debugging.


## Later role-security update

The subsequent [SECURITY_REVIEW.md](SECURITY_REVIEW.md) supersedes this report's
login/access descriptions and route count. It preserves commerce/AI/tuner/lesson
logic, adds strict separate login flows and the single-admin constraint, and retains
new requested security regression tests in `tests/test_security.py`. The commerce
fixture/scripts described above remain removed.
