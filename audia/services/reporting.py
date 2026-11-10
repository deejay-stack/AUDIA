"""Decimal-safe event-date reports in Asia/Manila, shared by dashboard and ledger."""
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from audia.database.models import now, utc_iso
from audia.services.ledger import ZERO, SETTLED, merchandise_allocations

MANILA = ZoneInfo('Asia/Manila')


def local_date(stamp):
    if stamp is None:
        return None
    return (stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp).astimezone(MANILA).date()


def date_range(args):
    end = local_date(now())
    days = {'day': 1, 'week': 7, 'month': 30, 'year': 365}.get(args.get('period'), 7)
    start = end - timedelta(days=days - 1)
    try:
        start = date.fromisoformat(args['start']) if args.get('start') else start
        end = date.fromisoformat(args['end']) if args.get('end') else end
    except (ValueError, TypeError) as error:
        raise ValueError('Use valid YYYY-MM-DD report dates.') from error
    if start > end or (end - start).days > 3660:
        raise ValueError('Choose an ordered date range of at most ten years.')
    return start, end


def in_range(stamp, start, end):
    day = local_date(stamp)
    return day is not None and start <= day <= end


def transaction(order):
    p = order.payment_record
    refunds = sum((r.amount for r in p.refunds), ZERO) if p else ZERO
    if p and p.status == 'Refunded' and not p.refunds:
        refunds = p.amount
    return dict(order_id=order.id, reference=p.reference if p else '', customer=order.customer,
                email=order.email, method=order.payment, amount=float(p.amount if p else order.total),
                status=p.status if p else 'Pending', channel=order.channel,
                date=utc_iso(p.collected_at or p.created_at) if p else utc_iso(order.created_at),
                collected_at=utc_iso(p.collected_at) if p and p.collected_at else None,
                refunded=float(refunds), receipt_url=f'/receipts/{order.id}' if p and p.receipt_number else None,
                verification='Internal test record' if p and p.is_simulated else 'Legacy offline record',
                fulfillment=order.status,
                events=[dict(previous=e.previous_status, status=e.new_status, action=e.action,
                             actor_id=e.actor_id, at=utc_iso(e.created_at)) for e in p.events] if p else [],
                refunds=[dict(id=r.id, amount=float(r.amount), reason=r.reason, status=r.status,
                              at=utc_iso(r.created_at)) for r in p.refunds] if p else [])


def report(records, args):
    start, end = date_range(args)
    today = local_date(now())
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    totals = defaultdict(lambda: ZERO)
    days, methods, channels, categories = (defaultdict(lambda: ZERO) for _ in range(4))
    best = {}
    supporting = set()
    paid_count = 0
    missing_dates = 0
    for order in records:
        p = order.payment_record
        if p is None:
            continue
        if p.status in SETTLED and (p.collected_at is None or (p.status == 'Refunded' and not p.refunds)):
            missing_dates += 1
        collected = p.status in SETTLED and p.collected_at is not None
        # Legacy fully refunded records have no trustworthy refund timestamp. Exclude
        # them from dated totals rather than fabricating an event in a chosen period.
        if p.status == 'Refunded' and not p.refunds:
            collected = False
        collection_in_range = collected and in_range(p.collected_at, start, end)
        if collection_in_range:
            paid_count += 1
            supporting.add(order.id)
            totals['collected_total'] += p.amount
            totals['gross_sales'] += order.subtotal
            totals['net_sales'] += order.subtotal - order.discount
            days[local_date(p.collected_at).isoformat()] += p.amount
            methods[order.payment] += p.amount
            channels[order.channel] += p.amount
            for item, allocated in zip(order.items, merchandise_allocations(order)):
                entry = best.setdefault(item.product_id, dict(id=item.product_id, name=item.name, quantity=0, revenue=ZERO))
                entry['quantity'] += item.quantity
                entry['revenue'] += allocated
                categories[item.category] += allocated
                totals['products_sold'] += item.quantity
        if collected:
            day = local_date(p.collected_at)
            for key, since in [('today_revenue', today), ('weekly_revenue', week_start), ('monthly_revenue', month_start)]:
                if since <= day <= today:
                    totals[key] += p.amount
        for r in p.refunds:
            day = local_date(r.created_at)
            if start <= day <= end:
                supporting.add(order.id)
                totals['refunded_total'] += r.amount
                totals['net_sales'] -= r.merchandise_amount
                days[day.isoformat()] -= r.amount
                methods[order.payment] -= r.amount
                channels[order.channel] -= r.amount
            for key, since in [('today_revenue', today), ('weekly_revenue', week_start), ('monthly_revenue', month_start)]:
                if since <= day <= today:
                    totals[key] -= r.amount
        if in_range(order.created_at, start, end) and p.status not in SETTLED and order.status not in ('Cancelled', 'Rejected'):
            totals['pending_collection'] += order.total
            totals['pending_payments'] += 1
    totals['paid_order_revenue'] = totals['collected_total'] - totals['refunded_total']
    created = [o for o in records if in_range(o.created_at, start, end)]
    group = args.get('group', 'day')
    if group not in ('day', 'week', 'month', 'year'):
        raise ValueError('Choose a valid chart grouping.')
    grouped = defaultdict(lambda: ZERO)
    for i in range((end - start).days + 1):
        day = start + timedelta(days=i)
        bucket = (day - timedelta(days=day.weekday())).isoformat() if group == 'week' else day.strftime('%Y-%m') if group == 'month' else str(day.year) if group == 'year' else day.isoformat()
        grouped[bucket] += days[day.isoformat()]
    metrics = {k: float(totals[k]) for k in ('collected_total', 'gross_sales', 'net_sales', 'refunded_total', 'paid_order_revenue',
               'pending_collection', 'pending_payments', 'products_sold', 'today_revenue', 'weekly_revenue', 'monthly_revenue')}
    return dict(**metrics, gross_revenue=metrics['paid_order_revenue'], total_orders=len(created), paid_orders=paid_count,
                completion_rate=round(100*sum(o.status == 'Delivered' for o in created)/len(created),2) if created else 0,
                cancellation_rate=round(100*sum(o.status in ('Cancelled','Rejected') for o in created)/len(created),2) if created else 0,
                cancelled_orders=sum(o.status in ('Cancelled', 'Rejected') for o in created),
                refunded_transactions=sum(bool(o.payment_record and o.payment_record.refunds) for o in records if o.id in supporting),
                chart=[dict(date=k, amount=float(v)) for k, v in sorted(grouped.items())],
                categories={k: float(v) for k, v in categories.items()},
                payment_methods={k: float(v) for k, v in methods.items()}, channels={k: float(v) for k, v in channels.items()},
                best_sellers=[dict(e, revenue=float(e['revenue'])) for e in sorted(best.values(), key=lambda e: e['quantity'], reverse=True)[:10]],
                order_statuses=dict(Counter(o.status for o in created)), supporting_orders=sorted(supporting),
                start=start.isoformat(), end=end.isoformat(), timezone='Asia/Manila', excluded_legacy_records=missing_dates,
                formula='Total collected = successful collections − completed refunds. Net sales excludes shipping and tax.')
