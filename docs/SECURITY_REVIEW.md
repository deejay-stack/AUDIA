# Role authentication and UI consistency review

October 29, 2026 (Asia/Manila). This pass fixes authentication/authorization and
shared presentation. It preserves existing accounts, credentials, environment
settings, order/payment processing, AI, tuner algorithms and lesson content.

## Root cause and corrected login flows

The previous login handler checked the stored account role only when the request
body selected `admin`. Customer login therefore accepted a valid administrator
password. The client could also switch portal roles without changing pages.

The server now fixes the expected role for each endpoint, checks the stored
`User.role`, verifies the password and rejects conflicting role fields using the
same generic `Incorrect email or password.` response. A URL, request field,
header or browser-storage value never grants a privilege.

| Portal | Page | Login endpoint | Accepted account role |
| --- | --- | --- | --- |
| Customer | `/login` | POST `/api/auth/login` | `customer` only |
| Administrator | `/admin/login` | POST `/api/auth/admin/login` | `admin` only |

`/login?role=admin` redirects to `/admin/login` for old bookmarks. Portal controls
are ordinary links to separate pages. A signed-in user visiting a login page is
redirected according to the database-verified identity: admin to `/admin`, customer
to `/shop`. This does not authenticate a logged-out user. Password recovery remains
shared and directs a successful reset back to the correct portal without signing
the user in automatically.

## Single administrator and data preservation

Exactly one administrator existed when this pass began. That account was retained;
the migration did not create, deactivate or change accounts, emails, roles or password
hashes. All records in all 14 existing tables matched the private pre-edit snapshot
immediately after migration. Later checks observed live registration/session/rate-limit
activity while the app was in use; the new customer and runtime records were retained.
The original accounts/password hashes and other business records still match the
checkpoint. Existing `.env` and runtime-secret hashes match.

The `uq_users_single_admin` partial unique index permits at most one row with
`role = 'admin'`. Together with the preserved administrator and no public role
mutation/deletion endpoint, it enforces the application's one-administrator policy.
All currently supported accounts are active; no new active/deactivated column was
introduced. The constraint also blocks concurrent inserts and direct database/ORM
promotion of a customer to a second administrator.

`create-admin` now rejects a second administrator before inserting and handles a
database uniqueness race safely. On a genuinely empty installation, the existing
explicit owner-run CLI command can provision the first admin. Startup, migration,
and public registration never create an administrator automatically.

`upgrade-db` adds the index after a private backup. It refuses legacy databases
with multiple administrators, preserving every account and requiring the owner to
identify the authorized one before any deactivation. It never selects or demotes
an administrator automatically. Re-running the upgrade is a no-op.

```powershell
.venv\Scripts\python.exe -m flask --app app upgrade-db
```

The configured `audia_db` has already been upgraded. No columns or business records
were altered. Private checkpoints are under `instance/backups/`:

- `before-role-security-*.zip`: pre-edit source, templates, styles and guides.
- `database-before-role-security-*.json.gz`: pre-edit records and private file hashes.
- `database-before-upgrade-*.json.gz`: migration's own recovery snapshot.

These files are ignored by Git and are not served as static resources. Database
snapshots contain private account records and must remain private.

## Authorization and session behavior

- `require_user()` supports authenticated, customer and admin access. Protected
  API access is checked before CSRF: guests receive 401 and authenticated wrong
  roles receive 403. Authorized mutations still require CSRF. `/api/admin/` has
  an additional prefix-level admin check.
- `require_page()` sends guests to the appropriate login portal and returns a
  consistent HTML 403 for an authenticated wrong role. Admin dashboard/customer
  shop and orders pages are strictly separated.
- Checkout, personal order lists, saved instruments and Finder state require a
  customer. Admins retain authorized order-detail inspection needed for management.
  Product reads remain available to authorized admin inventory flows. Shared
  profile/password and existing tuner/lesson modules remain available to both
  valid roles; customer-only account sections/navigation are hidden for admins.
- Customer registration always creates `customer`. Forged role/privilege fields
  are rejected rather than ignored. Profile and password forms cannot assign roles.
- Login rotates the session identifier and CSRF token. A signed session records
  the role actually verified from the database. Each request reloads the user and
  compares that binding; a later database role change cannot upgrade an old login.
- Legacy cookies without the role binding require fresh sign-in after this update.
  No password reset is required. Logout revokes the current stored session and
  clears its cookie state; replaying its old cookie does not restore access.
- Existing fixed session expiry, hashed database identifiers, HttpOnly/SameSite
  cookies, deployment-controlled Secure flag, rate limits and explicit remember-me
  behavior remain. Read-only session checks do not refresh stale cookies.
- Expiration compares actual UTC instants. An aware PostgreSQL timestamp with a
  non-UTC offset is converted, rather than having its offset overwritten; naive
  SQLite timestamps continue to be treated as UTC. This avoids extending access
  accidentally when the database connection returns a local timezone.
- Existing back/forward-cache reload and cross-tab login/logout revalidation remain.
  HTML/API responses use no-store, no-cache and expired cache headers. Browser
  storage is used for non-authentication preferences/events, never credentials or
  an authorization decision.

## UI consistency

`theme.css` now supplies shared primary/secondary/background/border and
success/warning/error/info colors for both themes, plus spacing, font, size and
radius tokens. The existing violet/mint identity is retained. Shared buttons,
inputs, forms, errors, statuses and headings use those tokens. Portal links have
keyboard focus, adequate hit areas and narrow-screen spacing. Table alignment,
readable wrapping, mobile input text and the access-denied page are consistent.

Payment selection, tracking/status meaning, order totals and all transaction
algorithms are unchanged. The payment option CSS specificity was corrected so
shared form-label rules do not override the card's flex layout. Customer and admin
status badges now use the same semantic palette without changing status data.

The automated contrast check verifies at least 4.5:1 for the tested normal-text
foreground/background token pairs in both themes. It does not claim a complete
rendered accessibility audit. Live desktop/tablet/mobile browser visual testing
was not performed in this pass; server-rendered markup, responsive rules and
static imports were inspected/checked.

## Verification

Run the retained security regressions with the project interpreter:

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

The 23 checks in `tests/test_security.py` use disposable SQLite, independent cookie
containers and random test-only credentials. They never log into or modify the
configured administrator account, and do not call live email or AI services.

| Scenario | Verified result |
| --- | --- |
| Admin credentials in customer flow | 401, generic rejection, no session |
| Customer credentials in admin flow | 401, same generic rejection |
| Correct admin/customer flows | 200, correct stored role and landing page |
| Manipulated role/query/header/body | No escalation or workflow switch |
| Every admin API, including writes | Guest 401; customer 403 |
| Direct wrong-role browser URL | HTML 403 before protected rendering |
| Public admin registration/profile promotion | 403, account rows unchanged |
| Second admin ORM insert or role promotion | Database uniqueness rejection |
| Second admin CLI creation | Rejected, existing hash preserved |
| Duplicate-admin legacy migration | Aborts, no deactivation or data edits |
| No-admin startup/migration | No automatic account creation |
| Logout and old cookie replay | Access denied; valid credentials required again |
| Session fixation/legacy or forged role binding | Old identity cannot be restored |
| Database role changed after login | Existing session invalidated |
| Aware/non-UTC and naive UTC expiration | Actual expiry instant respected |
| CSRF, cache, cookie and remember-me flags | Expected protections preserved |
| Customer registration/profile/password/recovery | Working through authorized flows |
| Customer order creation/admin detail inspection | Existing workflow and ownership preserved |
| Semantic text colors | Tested pairs meet 4.5:1 in both themes |

Python compilation, all JavaScript syntax/local imports, CSS imports and Jinja
compilation passed. All 50 pre-existing route entries remain; two login entries
bring the total to 52, with eight existing blueprints. The configured PostgreSQL
health endpoint returned 200. All 14 tables' records and existing password hashes
matched the private checkpoint immediately after the unique-index migration;
subsequent live activity was preserved without restoring an outdated snapshot.

Unrelated AI/chatbot, tuner, lesson and order/payment service files match their
pre-edit bytes. Customer catalog/search/order handler bodies match their prior
syntax after excluding the intentional access-decorator changes.

## Modified files

| File(s) | Change |
| --- | --- |
| `app.py` | Separate admin page, reusable page guards, correct redirects, CLI one-admin guard and uniqueness handling. |
| `audia/routes/auth/auth.py` | Separate login handlers, strict stored-role checks, public role-field rejection, session binding, access/CSRF order, 403 rendering, cache headers and role-aware reset return. |
| `audia/routes/auth/__init__.py` | Export `require_page`. |
| `audia/database/models.py` | Declare partial unique administrator index; no column/record changes. |
| `audia/database/migrations.py` | Backed-up, repeatable index creation and duplicate-admin refusal. |
| `audia/routes/{catalog/catalog,orders/orders,search_filter/search_filter}.py` | Customer-only access decorators on personal shopping state; handler bodies unchanged. |
| `templates/auth/{auth,auth_roles}.html` | Distinct portal titles and real navigation links. |
| `templates/auth/access_denied.html` | New reusable permission-denied interface. |
| `templates/account/{account,account_header}.html` | Shared admin profile with customer-only cards hidden and correct return link. |
| `templates/admin/admin_aside.html` | Public website preview label. |
| `templates/shared/{practice_base,practice_links}.html` | Role-correct navigation without removing shared practice features. |
| `assets/js/auth/auth.js` | Fixed portal role, separate login requests and role-aware reset navigation. |
| `assets/js/shared/app.js` | Role-correct navigation/session-expiry destination. |
| `assets/js/account/account.js` | Avoid customer data requests for admin profiles; status presentation hook. |
| `assets/js/admin/admin.js` | Website preview uses public landing page. |
| `assets/js/shared/shared.js` | Status presentation hook only. |
| `assets/css/shared/{theme,shared,commerce}.css` | Semantic tokens, spacing/type/control consistency, statuses and payment-label layout specificity. |
| `assets/css/auth/{auth,auth_roles}.css` | Portal/403 presentation and narrow-screen navigation. |
| `assets/css/admin/admin_order_status.css` | Semantic status colors. |
| `tests/test_security.py` | New self-contained security and compatibility regressions requested for this pass. |
| `README.md`, `PROJECT_STRUCTURE.md`, `DEBUGGING_GUIDE.md`, `docs/CSS_EDITING_GUIDE.md`, `docs/FRONTEND_COMPONENT_MAP.md`, `docs/UPGRADE_NOTES.md`, this report | Current login, constraint, navigation, theme and verification documentation. |

Restart an already-running Flask server to load this version. Existing users must
sign in once through their correct portal; all existing credentials stay valid.
