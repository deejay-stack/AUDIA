# Enhancement audit and implementation plan

Audit date: November 10, 2026 (Asia/Manila).

The existing application uses Flask/Jinja, vanilla JavaScript and component CSS,
SQLAlchemy, PostgreSQL, database login sessions and CSRF-protected JSON APIs.
Customer/admin pages have separate server guards. Products, order item snapshots,
stock reservation, payment attempts, one collection per order, separate refunds,
POS and collection-date reporting already work and must be retained.

Missing integrations found by tracing routes, services, models and templates:

1. Customers cannot request paid-order cancellation or item-based refunds. There
   is no review/return lifecycle or evidence storage.
2. Electronic methods share a basic modal. Bank review mode, merchant test account
   configuration and pending verification controls are missing.
3. Receipts are persisted but have no QR verification route or refund confirmation.
4. Tracking has a status timeline but no stored route, delivery metadata or map.
5. Settings contain only name/email. Shipping/payment/cancellation/return policies
   are not configurable. Stock edits and reservations lack a movement ledger.
6. Customer management lacks order drilldowns and account suspension controls.
7. Generic API fetches lack a timeout; error pages and retry controls need work.

No files will be removed based on their names. Existing URL groups, single-admin
policy, music lessons, tuner, Finder, chatbot, product IDs and historical records
remain. A private source zip was saved in instance/backups before structural work;
upgrade-db also snapshots database rows/schema before additive DDL.

Implementation sequence:

1. Add request/audit, delivery, stock movement and account status tables; preserve
   existing financial tables. Test migration preservation and repeatability.
2. Add validated store policies, explicit bank review, receipt QR verification and
   refund confirmations using the existing locked payment ledger.
3. Add customer cancellation/refund requests and administrator review/return/
   processing actions, quantity/amount bounds, idempotency and inspected restock.
4. Add stored simulated routes, delivery metadata, Leaflet/OSM fallback and optional
   configured Google Maps; label all route progress as simulated.
5. Integrate admin workspaces, customer dialogs, settings, inventory/customer
   history, notifications, filtering and errors into the existing navigation.
6. Execute backend, PostgreSQL concurrency and browser workflows on isolated data;
   apply the additive migration after those checks and document actual results.
