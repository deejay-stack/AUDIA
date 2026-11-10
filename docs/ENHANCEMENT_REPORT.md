# AUDIA full-stack enhancement report

November 10, 2026 · Asia/Manila

GCash follow-up: Confirm payment now opens a GCash mobile-number authorization
step. The backend validates the number before collection and saves only a masked
form on the payment attempt; success and receipts show that masked value. No OTP
or PIN is requested. A stale Jinja-template/new-JavaScript mismatch that prevented
the success panel from rendering was fixed by enabling local template reload,
checking the payment template before authorization, and restarting the local app.
An additive, backed-up migration adds `payment_attempts.payer_number_masked`.
The updated checks passed: 47 backend tests, 7 commerce browser groups and 7
PostgreSQL concurrency groups. The earlier operations-browser results below are
retained from the full delivery.

## 1. Initial problems and preservation

The audit found an existing Flask/Jinja storefront, vanilla JavaScript and component
CSS, SQLAlchemy/PostgreSQL, database sessions, CSRF, separate customer/admin login,
catalog/inventory editing, order reservation, electronic payment simulation,
counter POS, collection/refund ledger and revenue reporting. Those working modules
were retained. The missing integrations were customer refund/cancellation requests,
manual bank verification, QR receipts, delivery maps, operational settings, inventory
movements, customer history/account controls and request timeouts.

The audit and implementation order are recorded in ENHANCEMENT_PLAN.md. Before
editing, a source checkpoint including the pre-existing uncommitted work was saved
privately at `instance/backups/source-before-enhancement-20261110T123658Z.zip`.
No existing music, Finder, account, chatbot or authentication module was replaced.
No files were removed on the assumption that their filenames looked unused.

## 2. Integrated features

Customers can choose GCash, Maya, BDO, BPI, Metrobank, LandBank or COD, review the
stored amount/reference, authorize a simulation, retry an interrupted payment,
view success/failure/cancellation, open a QR receipt and track their order.
Provider logos use the existing attributed assets; LandBank retains a text fallback.
Merchant and fictional TEST identifiers come from backend settings. No PIN, OTP,
banking password, active account number or external settlement is collected.

My Orders now includes paid-cancellation requests, item/quantity return requests,
optional evidence images, request history, follow-up information and persistent
activity notifications. Administrators can review requests, approve smaller
amounts when policy permits, reject, record returns/inspection, explicitly restock,
process refunds and open store-issued refund confirmations.

The administrator also has delivery-route management, customer order/transaction/
request drilldowns, account suspension/restoration, product image uploads, product
sales history, stock movements, settings audits, payment verification and expanded
policy settings. Existing POS, inventory archive/restore, CSV, date-based reports
and receipt printing remain connected to the same database.

## 3. Database changes and executed migration

The additive upgrade adds:

| Table | Stored responsibility |
| --- | --- |
| refund_requests | Customer request, selected item snapshots, requested/approved amount, refund link, restock flag |
| refund_request_events | Review, customer information and lifecycle history |
| uploads | Random image identifier, owner, purpose and evidence/request association |
| inventory_movements | Signed stock change, resulting balance, order and actor |
| deliveries | Store-controlled route points, current point, reference, method, window and update |
| account_statuses | Customer suspension state, staff reason and actor |
| notifications | Customer-owned order/payment/refund notifications and read state |
| admin_audits | Staff catalog, settings and customer-access actions |

`payment_attempts.manual_review` captures the bank mode when an authorization
starts. Existing payment and refund financial records are reused. Request keys are
unique per order; one request can link to only one refund. Foreign keys preserve
ownership and relationships. No existing primary keys or credentials changed.

The configured PostgreSQL database was upgraded after isolated migration tests.
Its private row/schema snapshot is
`instance/backups/database-before-upgrade-20261110T130704994310Z.json.gz`.
Hashes of every pre-existing table's original rows/columns matched before and
after. The repeat upgrade returned already up to date. Database health returned
HTTP 200. New financial test data was confined to isolated databases/test schemas.
Migration DDL uses the existing PostgreSQL transaction/advisory lock. There is no
destructive downgrade; retain a normal PostgreSQL backup for deployment rollback.

## 4. Payment, receipt and financial architecture

`checkout.py` owns locked inventory reservation and backend price/fee validation.
`payments.py` owns attempt expiry, replay and authorization. `ledger.py` owns a
single collection per order and separate immutable completed-refund records.
`reporting.py` derives reports from collection/refund event dates in Asia/Manila.
Money remains Decimal through business calculations and Numeric database storage.

Automatic mode collects after successful internal authorization. Manual bank mode
records Pending Verification and an Awaiting review attempt. Only the admin API
can approve/reject that exact authorization; pending verification produces no paid
receipt and contributes no collected revenue. Changing settings does not change
the mode of an existing authorization. Counter POS remains an explicit immediate
staff-confirmed sale; COD remains uncollected until authorized collection after
delivery. Payment, stock and audit mutations commit together under order locks.

Successful collections retain a unique store receipt number. `/receipts/<order>`
shows item price snapshots, quantity, fees, discount, collection/refund totals,
internal reference and date. Print / Save PDF uses the browser print dialog.
The success screen and receipt display a locally generated QR SVG. It encodes the
current origin's `/verify/receipts/<receipt>` URL, with no customer data. Verification,
receipt and refund pages require the purchaser or administrator; a logged-out
verification viewer returns to that page after login. Refund receipts use
`/refunds/<refund-reference>` and preserve the original collection.

Only captured payments count as collections. Unpaid, failed, pending-bank and
uncollected COD orders contribute zero revenue. Completed refunds reduce net
collections by their actual amount. Existing collection-date reports, discounts,
channel/method breakdowns and CSV reconciliation are retained.

## 5. Cancellation, refund and inventory rules

Unshipped unpaid orders cancel directly when policy permits; the order transition
voids outstanding authorizations and releases each reserved quantity once.
Unshipped paid orders create a request. Approval does not refund immediately.
Processing an approved cancellation reverses the remaining captured payment and
releases its reservation in the same transaction. A dispatched order cannot follow
ordinary cancellation. Shipped/delivered orders use returns/refunds instead.

Request states are Requested, Under Review, Approved, Rejected, Awaiting Return,
Item Received, Refund Processing, Partially Refunded, Refunded and Closed.
Under Review supports additional staff/customer information. Refund amount is
computed from selected original order lines after merchandise-discount allocation;
quantities cannot exceed unprocessed purchased quantities. Shipping is excluded
from item-based return requests; pre-dispatch cancellation refunds the remaining
full collected amount. COD refund destination is configurable and simulated.
The return window uses a recorded Delivered event when present; historical orders
without that timestamp do not receive an invented delivery date.

The backend requires an actual capture, bounds approvals against both request and
remaining collection, rechecks the balance at processing, and reuses a stable
request-derived refund key. Separate order locks serialize direct refunds,
cancellations and request processing. An already-completed refund cannot be issued
again. A return restores stock only after explicit staff inspection at Item Received
→ Refund Processing, and only once. Monetary refunds alone do not restock goods.

Images are decoded and re-encoded as JPEG without original metadata; SVG/HTML,
unsupported formats, files over 4 MB and images over 16 megapixels are rejected.
Stored filenames are random, evidence is owner/admin-only, and claimable evidence
ownership is checked under a row lock. Product uploads are public catalog assets.

## 6. Delivery maps

Staff configure dispatch/destination coordinates, optional waypoints, a store-issued
tracking reference, supported delivery window, current point and update. Customers
see the stored address, status timeline, timestamps, history and resulting route.
No real customer addresses or routes were added to source; coordinates in tests
are synthetic. There is no geocoding, invented carrier partnership or live GPS.

The default map uses vendored [Leaflet 1.9.4](https://leafletjs.com/reference-1.9.4.html),
with route lines and circle markers. Browser tile requests use HTTPS, visible
OpenStreetMap attribution, normal browser caching/referrers and no prefetch,
following the [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/).
The tile URL is configurable. A failed tile request leaves the stored route/markers
and visible retry feedback usable.

Optional Google Maps uses the official JavaScript API, callback loading and
[advanced markers](https://developers.google.com/maps/documentation/javascript/advanced-markers/migration)
with Google's testing map ID. Configure a browser key restricted to your website
origins and Maps JavaScript API in Google Cloud. Missing/loading/auth failures
fall back to Leaflet. A valid billed Google key was unavailable, so live Google
rendering was not claimed as tested; failure/fallback was exercised in Edge.

## 7. Administrator experience and analytics

The existing branded sidebar now includes requests, fulfillment/delivery and
inventory movements. Desktop collapse, mobile navigation, order search, profile
access and operational alerts are functional. Deep links and refresh retain the
selected admin workspace. Financial cards, method/channel chart drilldowns,
collection/refund counts, order distribution, completion/cancellation percentages,
low-stock alerts and recent customer/order activity use stored records.

Orders support search, fulfillment/payment filters, sorting, pagination, detail,
reason/history, collection and CSV export. Payments support search, method/channel/
status/date filters, sorting, pagination, manual verification, receipt access,
refunds and audit detail. Requests support search, status, date/amount sorting,
pagination and review. Inventory movements support product/search filters and
pagination. Empty and failure states expose retry controls. Customer profiles never
serialize password hashes or authentication tokens. Suspension revokes sessions
and prevents login; the existing administrator account cannot be suspended here.

## 8. Routes and project structure

Before: customer/admin route modules, existing checkout/payment/order/reporting
services and component templates/styles. After: the same architecture, extended by
`audia/services/returns.py`, `settings.py`, `notifications.py`, and protected
`audia/routes/admin/operations.py`; browser operations live in
`assets/js/shared/order_operations.js` and `assets/js/admin/operations.js`.
No new application or frontend framework was introduced.

New protected entry points include `/admin/refunds`, `/admin/delivery`,
`/admin/inventory`, `/admin/transactions`, `/admin/settings`, customer
`/api/orders/<order>/requests`, admin `/api/admin/requests/<request>`,
`/api/admin/payments/<order>/verify`, `/api/admin/orders/<order>/delivery`,
customer-owned `/api/account/notifications`, protected `/uploads/<id>`, receipt
verification and refund confirmations. Existing `/admin`, `/shop`, `/orders`,
`/account` and original API URLs remain. Unknown admin pages return a real 404.
Admin/customer roles and CSRF are enforced on the backend, including uploads.

API calls use relative same-origin URLs and a 20-second timeout. 404/500/database
errors have visible HTML/API responses. `TRUSTED_PROXY_HOPS` defaults to zero; set
it only for known proxies that overwrite forwarding headers. HTTPS deployments
should retain COOKIE_SECURE=true. Sessions are never trusted from browser storage.

## 9. Executed tests and actual results

| Check | Result |
| --- | --- |
| Backend isolated SQLite suite, foreign keys on | 46 tests passed |
| Existing Edge commerce suite | 7 scenario groups passed |
| New Edge operations suite | 8 scenario groups passed |
| Actual PostgreSQL concurrency in disposable schema | 7 scenario groups passed; schema removed |
| JavaScript modules | 20 syntax checks passed |
| Jinja templates | All compiled |
| Configured database preservation | All original row/column hashes matched |
| Configured migration repeat / health | Already up to date / HTTP 200 |

Backend tests cover the prior registration/auth/catalog/financial regressions plus
pending-bank review, rejected retries, mode snapshots, paid cancellation/replay,
review/inspection/partial refunds, invalid/excess amounts and quantities, stale
remaining balances, return windows, private QR/receipt/evidence access, image
validation, shipping/method settings, notifications, information replies,
account suspension and migration preservation/repeatability.

Browser tests exercised customer checkout, failed/successful payment and retry,
receipt/PDF/CSV, POS lost-response recovery, ledger drilldown, refund request and
staff lifecycle, inspected restock, partial refund confirmation, bank verification,
stored route rendering with forced Google/tile failures, cancellation requests,
notifications/read state, settings save/refresh and mobile layouts. Runtime error
collectors reported no JavaScript exceptions. Screenshots were visually inspected.
Artifacts are in ignored `test-results/commerce/` and `test-results/operations/`.

PostgreSQL tests use six simultaneous callers for overselling, duplicate checkout,
duplicate confirmation, competing/duplicate refunds, paid-cancellation request and
reversal/release, manual bank approval and inspected return restock. Each verified
one effect or rejection at the correct bound.

Local access was tested on 127.0.0.1; a separate localhost origin and a forwarding
HTTP proxy at port 5099 were tested for same-origin APIs, cookies and refresh.
An actual external/public tunnel and physical phone camera were not available.
QR generation and authorized verification were tested, but physical phone scanning
remains a manual device check.

## 10. Remaining limits

- This remains the requested school simulation: no real funds, provider/courier
  settlement, carrier telemetry or real financial credentials.
- A valid restricted Google browser key/billing configuration and a real public
  tunnel must be verified in the deployment environment; Leaflet needs no key.
- Receipts/PDF use browser printing. There is no dedicated server PDF service.
- Existing single-admin policy remains; a configurable multi-staff permissions
  matrix was not introduced. Catalog discounts remain the existing POS discount
  workflow and direct product-price editing; no promotion/coupon engine was added.
- Account delivery details retain the existing single saved address rather than
  a multi-address book. Navigation consolidates payment and refund histories in
  My Orders and its details rather than creating duplicate history pages.
- Reporting/request/movement filtering uses in-memory records after database reads
  at school-project scale. A large production dataset needs SQL aggregation/paging.
- Unpaid orders hold stock until cancellation; there is no background expiry job.
- Evidence is stored locally; orphan upload cleanup, cloud storage, malware scanning
  infrastructure and email/push delivery are not configured. In-app notifications
  are persisted. Retain `instance/uploads/` with database backups.
- Historical stock, delivery times and request histories are not fabricated.
  Existing unrelated microphone/AI/mail features were preserved; physical-device
  and live external-service regression coverage is outside these commerce tests.

## 11. Run and test commands

```powershell
# From the existing AUDIA_V2 directory; PostgreSQL must be running.
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m flask --app app upgrade-db
.venv\Scripts\python.exe app.py

# Fresh empty database only, never reset an existing database:
.venv\Scripts\python.exe -m flask --app app init-db
.venv\Scripts\python.exe -m flask --app app create-admin

# Reproduce the checks:
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.venv\Scripts\python.exe tests/postgres_concurrency.py
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe tests/browser_commerce.py
.venv\Scripts\python.exe tests/browser_operations.py
```

Open the URL printed at startup (default http://localhost:5000; this workspace's
existing PORT setting uses http://localhost:5001). Customer login is `/login`; administrator login is
`/admin/login`. Existing accounts are preserved; no default login was created.
Restart an already-running Flask process after source changes. Browser suites use
installed Microsoft Edge and isolated test ports 5097–5099.
