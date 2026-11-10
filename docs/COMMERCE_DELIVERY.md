# Integrated POS, payments and sales reporting

This is the initial commerce delivery record. The subsequent
[full-stack enhancement report](ENHANCEMENT_REPORT.md) is the current reference
for bank review, customer request workflows, QR verification, maps, configuration,
new dependencies and updated test results. Historical limitations below describe
the initial implementation and are superseded where the newer report says so.

Delivery date: November 10, 2026 (Asia/Manila).

## Architecture and audit

AUDIA remains a Flask application with Jinja templates, vanilla JavaScript,
SQLAlchemy and PostgreSQL. No replacement framework or frontend build was added.
Existing registration, separate customer/admin login, database sessions, CSRF,
authorization, catalog, account, inventory, chatbot and learning routes remain.
The user's existing changes to the chatbot panel and landing templates were preserved.

The audit found persisted online payment attempts and stock reservation already
implemented. Missing pieces were counter POS, receipts, a refund ledger, payment
audits, online-payment revenue, collection-date reporting, and payment branding.
The old refund transition automatically restocked products; this is corrected.

Online checkout and counter POS now share `audia/services/checkout.py`. It locks
the requesting user for idempotency, validates quantities and current prices,
locks inventory in product-ID order, and conditionally decrements available stock.
Order items keep product IDs, names, categories and unit-price snapshots.
Creation, inventory, payment and financial mutations commit together or roll back.

`audia/services/ledger.py` owns internal collections and refunds. One payment row
belongs to each order, so no second POS ledger or duplicate revenue row is needed.
`channel` distinguishes `online` and `pos`; `staff_id` records the counter operator.
Refund operations lock the parent order, reject over-refunds and replay safely.
`audia/services/reporting.py` is shared by dashboard calculations and transaction
drilldowns. Reports use stored records, Decimal arithmetic and Asia/Manila dates.

## Features and entry points

- **Shop → cart → checkout:** validated delivery information and seven choices:
  GCash, Maya, BDO, BPI, Metrobank, LandBank, and Cash on Delivery.
- **My Orders:** persistent order/payment history, tracking, safe retry, unpaid
  cancellation, and a receipt link after successful collection.
- **Administration → Point of sale:** search by name/product ID, scanner input
  when it produces a known product code/ID, quantities, removal, flat PHP discount
  with a reason, cash/electronic test collection, and receipt. An uncertain network
  response freezes and retains the original payload/key for recovery. No sale is
  silently replaced after a lost response.
- **Administration → Orders:** separate fulfillment changes and explicit COD
  collection after delivery. Packed and Returned states were added.
- **Administration → Payments & transactions:** search, method/channel/status
  filters, date range, sorting, pagination, audited detail, full/partial refunds,
  receipt links, and CSV export using the same filters.
- **Overview:** collected totals, gross/net merchandise sales, current Manila
  day/week/month revenue, pending balances/payments, collected transaction counts,
  cancellations/refunds, products sold, and store activity. Financial cards open
  supporting transactions. Daily/weekly/monthly/yearly chart grouping, payment
  method/channel/category charts, order status distribution and best sellers use
  database records. Print the summary with the report button.
- Visible admin order/summary/ledger views refresh at roughly 15-second intervals.
  Mutations refetch relevant records. Normal page and admin section navigation
  resets scrolling; deliberate hash anchors and history navigation are preserved.

New endpoints are `/api/admin/pos`, `/api/admin/transactions`,
`/api/admin/transactions/export`, `/api/admin/transactions/<order_id>`,
`/api/admin/transactions/<order_id>/refunds`, and `/receipts/<order_id>`.
All administrative endpoints require the database-derived admin role. Receipt
access requires the owning customer or administrator. Mutations retain CSRF.

## Payment behavior

All new payments are internal simulations. There are no banking APIs, money
transfers, account numbers, PINs, OTPs, uploads of bank evidence, or provider
verification claims. Normal method names appear with a discreet **Test Mode —
No real funds transferred** notice in confirmation and receipts.

GCash, Maya and all four banks follow the same explicit simulator:

1. An order reserves inventory and creates a Pending payment with a unique
   internal TXN reference and server-calculated amount.
2. Opening confirmation creates a Processing payment attempt with a ten-minute
   expiry. Different tabs reuse the active attempt.
3. Backend confirmation records Paid, collection time, actor, immutable audit
   events and a unique receipt number; fulfillment becomes Confirmed.
4. Decline/expiry records Failed. Cancellation records Cancelled on the payment
   attempt/payment; the saved order remains unpaid and retryable. A new attempt
   reuses the existing order and reserved stock.
5. Replayed confirmations return the committed outcome and never collect twice.

The confirm button is explicitly an **internal test payment** action, not a claim
that a customer has made a real bank transfer. There is no manual bank verification
feature or “I Have Paid” proof flow.

COD stays Pending through acceptance/dispatch and even delivery until the admin
explicitly checks the collection confirmation and supplies a verification note.
Only then does the internal collection contribute to revenue. Repeated COD
collection does not change the collection date or create another receipt.

Counter POS requires explicit test-collection confirmation. Cash records the
internal collection directly; electronic methods use the same payment simulator.
The customer collects the goods at the counter, so fulfillment becomes Delivered.

Refunds create Completed refund records and change payment status to Partially
Refunded or Refunded. Fulfillment remains separate. Cancelling an already paid,
undispatched order reverses its remaining collection and releases reserved stock.
Refunds/returns after delivery never automatically restock goods. Inspect goods
and adjust inventory through the existing editor when appropriate.

Successful receipts are AUDIA-issued HTML pages with original prices, subtotals,
discount, tax, shipping, amount collected, refunds, net collection, references,
customer, method, status and Manila collection time. **Print / Save PDF** uses
the browser's print dialog. These are test receipts, not provider receipts.

Official local assets for GCash, Maya, BDO, BPI and Metrobank are in
`assets/images/payments/`; exact source URLs and attribution are in `SOURCES.md`
there. LandBank uses a text fallback because a usable official asset could not be
retrieved. Brand assets retain their proportions, have visible text labels and
do not imply an official partnership. No invented logos were created.

## Financial definitions

Amounts are PHP stored as Numeric/Decimal. The frontend preview is advisory;
the backend validates price snapshots, stock, discounts and expected totals.

```
Line subtotal = unit-price snapshot × quantity
Merchandise subtotal = sum(line subtotals)
Order total = subtotal − discount + tax + shipping

Gross merchandise sales = merchandise subtotals of collections in the period
Collected before refunds = successful payment amounts collected in the period
Completed refunds = completed refund amounts dated in the period
Total collected / paid-order revenue = collections − completed refunds
Net merchandise sales = collected merchandise after discounts − merchandise refunds
Pending collection = unpaid balances of active orders placed in the period
```

Gross/net sales exclude shipping and tax. The current store retains free shipping
and zero additional tax; no new VAT policy is implied. Counter discounts must be
nonnegative, less than the subtotal, and supported by an admin-entered reason.
Refunds allocate proportionally to merchandise versus fees; final refunds absorb
centavo rounding. Category/product allocations also reconcile to discounted
merchandise totals. Units and best-seller/category figures are labelled **before
returns**, because a monetary refund alone is not evidence of returned units.

Payment collection date, not order creation/delivery date, determines revenue.
Refund date determines the reduction. Therefore a refund in a later period can
produce negative revenue/net sales for that period. CSV exports include
`collection_in_period`, `refunds_in_period` and `net_collection_in_period` so the
selected dashboard total can be reconciled even when original collection dates
fall outside the selected period. Refund-only rows retain the original collection
date in the main transaction-date column; audit details show the refund date.

Today/week/month cards show the current Manila calendar period; the other cards
and charts use the selected reporting dates. Stored timestamps remain UTC-aware.

## Database upgrade and preservation

`upgrade-db` saves a private, gzip-compressed pre-upgrade row/schema snapshot in
`instance/backups/` before making changes. PostgreSQL DDL uses a transaction and
an advisory migration lock. The upgrade is additive and repeatable.

Added order columns: `subtotal`, `discount`, `shipping_fee`, `tax`, `channel`,
`staff_id`. Added payment columns: `amount`, `currency`, `is_simulated`,
`receipt_number`, `created_at`; payment status allows Partially Refunded.
New tables: `payment_events` and `refunds`, with foreign keys, lookup indexes,
positive refund constraints and per-payment unique refund request keys. Receipt
numbers are unique; one payment per order and existing checkout/attempt unique
request-key constraints are preserved. Staff has a users foreign key.

Legacy totals are copied into subtotal/payment amount; shipping/discount/tax
default to zero. Existing Demo paid/Demo refunded states become Paid/Refunded.
Successful attempt timestamps can supply an existing, evidenced collection time;
missing dates are not invented. Historical refunded payments without refund-date
evidence, and paid records without collection dates, are excluded from dated
financial totals with a visible warning. Orders without a payment record receive
an explicit unpaid balance; Delivered never implies Paid. This fixed one such
record in this workspace. Existing users, passwords, product IDs and orders remain.

There is no destructive automatic downgrade. Keep the private snapshots for row
recovery. For deployment rollback, also keep a normal PostgreSQL backup and restore
it into a separate database before pointing the prior code at it; do not drop new
financial tables from a database that has accepted new sales.

## Run and verify

No new runtime environment variables or runtime packages are required.
`DEMO_PAYMENT_TEST_CONTROLS=true` remains an optional existing local setting for
decline/timeout controls; successful/cancelled flows work without it. Restart the
Flask process after changes; hot reload is disabled by default.

```powershell
# PostgreSQL must be running, with existing .env credentials configured.
# This workspace's PostgreSQL 18 Windows service is already running.
# If stopped, from an elevated PowerShell terminal:
Start-Service -Name postgresql-x64-18
.venv\Scripts\python.exe -m flask --app app upgrade-db
.venv\Scripts\python.exe app.py

# New empty databases only:
.venv\Scripts\python.exe -m flask --app app init-db
.venv\Scripts\python.exe -m flask --app app create-admin

# Backend regressions, isolated SQLite database:
.venv\Scripts\python.exe -B -m unittest discover -s tests -v

# Actual PostgreSQL lock/idempotency checks in a temporary test schema:
.venv\Scripts\python.exe tests/postgres_concurrency.py

# Optional browser test dependencies; uses installed Microsoft Edge on Windows:
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe tests/browser_commerce.py
```

Frontend and backend run together at `http://localhost:5000`; no separate frontend
or database-container command is required. PostgreSQL remains an external service.
The browser test starts its own isolated test server at port 5097 and never seeds
the configured application database. The PostgreSQL concurrency test creates and
removes only its generated `audia_test_<random>` schema, requiring schema creation
permission for the configured DB user.

Executed verification results are recorded below. Browser
screenshots, a printed PDF, CSV and JSON results live in ignored
`test-results/commerce/`. These contain synthetic test data only.

## Executed verification results

| Check | Actual result |
| --- | --- |
| Backend unit/integration regressions | 31 passed on isolated SQLite with foreign keys enabled |
| Browser workflows in installed Microsoft Edge | 7 scenario groups passed; no JavaScript runtime errors |
| PostgreSQL concurrency | 4 scenario groups passed in a temporary schema, then schema removed |
| Changed JavaScript modules | All 7 passed Node syntax checks |
| Templates | All Jinja templates compiled successfully |
| Python modules | Compile checks passed |
| Patch whitespace | `git diff --check` passed |
| Configured database migration | Applied after private backups; repeat run reported up to date |

Backend coverage includes registration/login, role isolation and CSRF, catalog
details/saved products, checkout validation and rollback, immutable prices,
duplicate submissions, every online method, failed/cancelled/expired/interrupted
payments, retries, repeated collections, COD, counter discounts, receipts and
ownership, partial/full and duplicate refunds, no automatic return restocking,
date boundaries, later-period refunds, financial allocation/rounding, CSV formula
protection, pagination and legacy migration preservation/unpaid backfill.

Browser groups cover checkout/selection and failed payment; successful retry and
receipt/history; revenue drilldown; counter POS and recovery after a committed
sale's response is deliberately lost; payment detail/refund/CSV; mobile/tablet
layouts with selectable payment cards; and authorization/runtime errors.
Responsive checks used 390×844, 768×1024 and 1440×1000 viewports. Screenshots were
visually reviewed, including corrected provider logo contrast and identity.

PostgreSQL checks used six concurrent callers for scarce stock, duplicate
checkouts, duplicate confirmations, and duplicate/competing refunds. They verified
no overselling, one order/deduction, one collection/receipt, and no over-refund.

## Limits

- No real provider, carrier, financial settlement, bank proof or email receipt
  integration is configured. This is the requested school-project simulator.
- Receipt PDF and summary printing use the browser; there is no server PDF service.
- Interrupted/failed unpaid orders reserve stock until cancellation. Attempt
  expiry is checked on the next payment request; there is no background stock
  release scheduler.
- Returns need staff inspection/manual stock adjustment; refunds are monetary.
- Barcode input supports existing IDs/product codes, not a separate barcode registry.
- Reporting filters and paginates on the backend after loading records. This suits
  the school dataset; large production datasets need database aggregate queries.
- Tests cover the commerce changes and core existing account/catalog routes.
  Physical scanners, microphones, third-party AI/mail availability, and exhaustive
  unrelated lessons/chatbot regression checks were not performed.
