"""Isolated tests: never connect to or seed the configured development database."""
import csv
import io
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine, event, select, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import app
from audia.database.models import Base, User, Product, Order, OrderPayment, OrderEvent, PaymentAttempt, PaymentEvent, Refund, Setting, now
from audia.database.migrations import upgrade_database
from audia.services.reporting import local_date, report
from audia.services.ledger import money


class CommerceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = 'School-test-password-2026'
        cls.password_hash = generate_password_hash(cls.password)

    def setUp(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
        @event.listens_for(self.engine, 'connect')
        def foreign_keys(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
        Base.metadata.create_all(self.engine)
        self.factory = sessionmaker(self.engine, expire_on_commit=False)
        self.original_extensions = app.extensions.copy()
        self.original_config = app.config.copy()
        app.extensions.update(engine=self.engine, db_factory=self.factory)
        app.config.update(TESTING=True, SECRET_KEY='isolated-test-key', DEMO_PAYMENT_TEST_CONTROLS=True)
        with self.factory() as db:
            db.add_all([User(id=1,name='Customer One',email='one@example.test',role='customer',password_hash=self.password_hash),
                        User(id=2,name='Admin',email='admin@example.test',role='admin',password_hash=self.password_hash),
                        User(id=3,name='Customer Two',email='two@example.test',role='customer',password_hash=self.password_hash),
                        Product(id=1,name='TEST_GUITAR',brand='Test',category='Acoustic',price=Decimal('100.10'),stock=20),
                        Product(id=2,name='TEST_STRINGS',brand='Test',category='Accessories',price=Decimal('20.25'),stock=20),
                        Setting(key='store_name',value='AUDIA Test Store')])
            db.commit()
        self.client = app.test_client()
        self.csrf = self.client.get('/api/auth/session').json['csrf_token']
        self.login()

    def tearDown(self):
        app.extensions.clear(); app.extensions.update(self.original_extensions)
        app.config.clear(); app.config.update(self.original_config)
        self.engine.dispose()

    def send(self, method, path, data=None, client=None, token=None):
        return (client or self.client).open(path,method=method,json=data,headers={'X-CSRF-Token':token or self.csrf})

    def login(self, admin=False, email=None):
        if self.client.get('/api/auth/session').json.get('user'):
            self.send('POST','/api/auth/logout',{})
        self.csrf=self.client.get('/api/auth/session').json['csrf_token']
        r=self.send('POST','/api/auth/admin/login' if admin else '/api/auth/login',
                    {'email':email or ('admin@example.test' if admin else 'one@example.test'),'password':self.password})
        self.assertEqual(r.status_code,200,r.json)
        self.csrf=r.json['csrf_token']

    def checkout(self, method='gcash', **changes):
        data=dict(request_key=str(uuid.uuid4()),address='123 Test Street, Manila',phone='09171234567',
                  payment_method=method,items=[dict(product_id=1,quantity=2),dict(product_id=2,quantity=1)])
        data.update(changes)
        return self.send('POST','/api/orders',data)

    def start(self, order, **changes):
        return self.send('POST',f"/api/orders/{order['id']}/payment-attempts",dict(request_key=str(uuid.uuid4()),**changes))

    def confirm(self, order, attempt, outcome='success'):
        return self.send('POST',f"/api/orders/{order['id']}/payment-attempts/{attempt['id']}/confirm",dict(outcome=outcome,gcash_number='09170000000'))

    def paid_order(self, method='gcash'):
        r=self.checkout(method); self.assertEqual(r.status_code,201,r.json)
        order=r.json['order']; r=self.start(order); self.assertEqual(r.status_code,200,r.json)
        r=self.confirm(order,r.json['attempt']);self.assertEqual(r.status_code,200,r.json)
        return r.json['order']

    def summary(self):
        r=self.client.get('/api/admin/summary?period=month');self.assertEqual(r.status_code,200,r.json);return r.json

    def test_registration_login_invalid_credentials_and_role_guard(self):
        guest=app.test_client();token=guest.get('/api/auth/session').json['csrf_token']
        r=self.send('POST','/api/auth/register',dict(name='New Student',email='new@example.test',password=self.password),guest,token)
        self.assertEqual(r.status_code,201)
        self.assertIsNone(guest.get('/api/auth/session').json['user'])
        r=self.send('POST','/api/auth/login',dict(email='new@example.test',password='wrong'),guest,token);self.assertEqual(r.status_code,401)
        r=self.send('POST','/api/auth/login',dict(email='new@example.test',password=self.password),guest,token);self.assertEqual(r.status_code,200)
        self.assertEqual(guest.get('/api/admin/summary').status_code,403)
        self.assertEqual(self.send('POST','/api/auth/register',dict(name='Hacker',email='hack@example.test',password=self.password,role='admin')).status_code,403)

    def test_admin_login_is_separate_and_customer_cannot_get_financial_records(self):
        self.assertEqual(self.send('POST','/api/auth/login',dict(email='admin@example.test',password=self.password)).status_code,401)
        for path in ['/api/admin/transactions','/api/admin/transactions/export','/api/admin/summary','/admin']:
            self.assertEqual(self.client.get(path).status_code,403,path)
        self.assertEqual(self.send('POST','/api/admin/pos',{}).status_code,403)
        self.login(True);self.assertEqual(self.client.get('/admin').status_code,200)

    def test_guest_and_csrf_protection(self):
        self.assertEqual(app.test_client().get('/api/orders').status_code,401)
        self.assertEqual(self.client.post('/api/orders',json={}).status_code,403)

    def test_catalog_browse_detail_saved_item_and_pages(self):
        self.assertEqual(self.client.get('/api/products').status_code,200)
        self.assertEqual(self.client.get('/api/products/1').json['name'],'TEST_GUITAR')
        self.assertEqual(self.client.get('/api/products/999').status_code,404)
        for path in ['/shop','/account','/orders']:
            self.assertEqual(self.client.get(path).status_code,200)
        self.assertEqual(self.send('PUT','/api/account/saved/1',{}).status_code,200)
        self.assertEqual(len(self.client.get('/api/account/saved').json['products']),1)
        self.assertEqual(self.send('DELETE','/api/account/saved/1',{}).status_code,200)

    def test_decimal_totals_snapshots_and_duplicate_checkout(self):
        key=str(uuid.uuid4());r=self.checkout(request_key=key,expected_total='220.45');self.assertEqual(r.status_code,201,r.json)
        order=r.json['order'];self.assertEqual(order['amount'],220.45)
        self.assertEqual(self.checkout(request_key=key).json['order']['id'],order['id'])
        with self.factory() as db:
            self.assertEqual(db.get(Product,1).stock,18)
            db.get(Product,1).price=Decimal('500');db.commit()
            self.assertEqual(db.get(Order,order['id']).items[0].price,Decimal('100.10'))
            self.assertEqual(len(list(db.scalars(select(Order)))),1)

    def test_invalid_checkout_rolls_back_inventory(self):
        for change in [dict(address=''),dict(phone='invalid'),dict(payment_method='unknown'),dict(expected_total='0.01'),
                       dict(items=[dict(product_id=1,quantity=1),dict(product_id=2,quantity=99)]),
                       dict(items=[dict(product_id=999,quantity=1)]),dict(items=[dict(product_id=1,quantity=True)])]:
            with self.subTest(change=change):self.assertEqual(self.checkout(**change).status_code,400)
        with self.factory() as db:
            self.assertEqual(db.get(Product,1).stock,20);self.assertEqual(len(list(db.scalars(select(Order)))),0)

    def test_all_supported_online_methods_and_receipts(self):
        for method in ['gcash','maya','bdo','bpi','metrobank','landbank']:
            with self.subTest(method=method):
                order=self.paid_order(method);self.assertEqual(order['payment_status'],'Paid');self.assertEqual(order['status'],'Confirmed')
                receipt=self.client.get(order['receipt_url']);self.assertEqual(receipt.status_code,200)
                self.assertIn(b'No real funds transferred',receipt.data)
        self.login(True);s=self.summary();self.assertEqual(s['paid_orders'],6);self.assertAlmostEqual(s['gross_revenue'],1322.70)

    def test_failed_cancelled_interrupted_timeout_retry(self):
        for outcome in ['failure','cancelled','timeout']:
            with self.subTest(outcome=outcome):
                order=self.checkout().json['order'];started=self.start(order).json
                self.assertEqual(started['order']['payment_status'],'Processing')
                r=self.confirm(order,started['attempt'],outcome);self.assertNotEqual(r.json['order']['payment_status'],'Paid')
                self.assertIsNone(r.json['order']['receipt_url']);self.assertTrue(r.json['order']['can_retry_payment'])
                retry=self.start(order).json['attempt'];self.assertNotEqual(retry['id'],started['attempt']['id'])
                self.assertEqual(self.confirm(order,retry).json['order']['payment_status'],'Paid')
        interrupted=self.checkout().json['order'];self.start(interrupted)
        self.login(True);self.assertEqual(self.summary()['paid_orders'],3)

    def test_expired_attempt_and_single_active_attempt(self):
        order=self.checkout().json['order'];first=self.start(order).json['attempt'];second=self.start(order).json['attempt']
        self.assertEqual(first['id'],second['id'])
        with self.factory() as db:
            db.get(PaymentAttempt,first['id']).expires_at=now()-timedelta(minutes=1);db.commit()
        r=self.confirm(order,first);self.assertEqual(r.json['attempt']['status'],'Timed out');self.assertEqual(r.json['order']['payment_status'],'Failed')

    def test_duplicate_payment_does_not_duplicate_revenue_or_receipt(self):
        order=self.checkout().json['order'];a=self.start(order).json['attempt']
        first=self.confirm(order,a).json['order'];second=self.confirm(order,a).json['order']
        self.assertEqual(first['receipt_url'],second['receipt_url'])
        with self.factory() as db:
            p=db.get(OrderPayment,order['id']);self.assertEqual(sum(e.new_status=='Paid' for e in p.events),1)
        self.login(True);self.assertEqual(self.summary()['gross_revenue'],220.45)

    def test_payment_failure_controls_disabled_and_status_tampering(self):
        app.config['DEMO_PAYMENT_TEST_CONTROLS']=False
        order=self.checkout().json['order'];a=self.start(order).json['attempt']
        self.assertEqual(self.confirm(order,a,'failure').status_code,400)
        self.assertEqual(self.send('PATCH',f"/api/admin/sales/{order['id']}",dict(payment_status='Paid')).status_code,403)
        self.login(True)
        self.assertEqual(self.send('PATCH',f"/api/admin/sales/{order['id']}",dict(payment_status='Paid',status='Delivered')).status_code,400)

    def test_cod_separate_collection_and_double_collection(self):
        order=self.checkout('cod').json['order'];self.login(True)
        self.assertEqual(self.summary()['gross_revenue'],0)
        path=f"/api/admin/sales/{order['id']}"
        for status in ['Confirmed','Processing','Packed','Shipped','Out for Delivery','Delivered']:
            r=self.send('PATCH',path,dict(status=status));self.assertEqual(r.status_code,200,r.json)
        self.assertEqual(self.summary()['gross_revenue'],0)
        body=dict(payment_status='Paid',collection_confirmed=True,payment_reference='Test COD collection')
        r=self.send('PATCH',path,body);self.assertEqual(r.status_code,200,r.json)
        first=r.json['order'];self.assertIsNotNone(first['payment_collected_at'])
        r=self.send('PATCH',path,body);self.assertEqual(r.json['order']['payment_collected_at'],first['payment_collected_at'])
        self.assertEqual(self.summary()['gross_revenue'],220.45)

    def test_cancel_unpaid_restores_stock_only_once(self):
        order=self.checkout().json['order'];self.start(order)
        for _ in range(2):self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/cancel",{}).status_code,200)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,20)
        self.login(True);s=self.summary();self.assertEqual(s['gross_revenue'],0);self.assertEqual(s['pending_collection'],0)

    def test_counter_sale_discount_receipt_idempotency_and_stock(self):
        self.login(True);key=str(uuid.uuid4());body=dict(request_key=key,customer='Walk-in Student',payment_method='cash',
                items=[dict(product_id=1,quantity=2),dict(product_id=2,quantity=1)],discount='20.45',discount_reason='School discount',confirmed=True,expected_total='200.00')
        r=self.send('POST','/api/admin/pos',body);self.assertEqual(r.status_code,201,r.json)
        order=r.json['order'];self.assertEqual(order['amount'],200);self.assertEqual(order['channel'],'pos');self.assertEqual(order['status'],'Delivered')
        self.assertEqual(self.send('POST','/api/admin/pos',body).json['order']['id'],order['id'])
        self.assertEqual(self.client.get(order['receipt_url']).status_code,200)
        s=self.summary();self.assertEqual(s['gross_sales'],220.45);self.assertEqual(s['net_sales'],200);self.assertEqual(s['gross_revenue'],200)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,18)

    def test_counter_all_electronic_methods(self):
        self.login(True)
        for method in ['gcash','maya','bdo','bpi','metrobank','landbank']:
            r=self.send('POST','/api/admin/pos',dict(request_key=str(uuid.uuid4()),customer='Counter Customer',payment_method=method,
                items=[dict(product_id=1,quantity=1)],confirmed=True))
            self.assertEqual(r.status_code,201,r.json);self.assertEqual(r.json['order']['payment_status'],'Paid')

    def test_counter_invalid_discount_and_unconfirmed_sale(self):
        self.login(True)
        for values in [dict(discount='101'),dict(discount='-1'),dict(discount='NaN'),dict(discount='1.001'),dict(discount='1',discount_reason=''),dict(confirmed=False),dict(payment_method='cod')]:
            body=dict(request_key=str(uuid.uuid4()),customer='Student',payment_method='cash',confirmed=True,items=[dict(product_id=1,quantity=1)])
            body.update(values);self.assertEqual(self.send('POST','/api/admin/pos',body).status_code,400)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,20)

    def test_partial_full_refund_idempotency_and_no_restock(self):
        order=self.paid_order();self.login(True);path=f"/api/admin/transactions/{order['id']}/refunds"
        body=dict(request_key=str(uuid.uuid4()),amount='20.45',reason='Partial price refund')
        r=self.send('POST',path,body);self.assertEqual(r.status_code,200,r.json);self.assertEqual(r.json['order']['payment_status'],'Partially Refunded')
        self.assertEqual(self.send('POST',path,body).json['refund_id'],r.json['refund_id'])
        s=self.summary();self.assertEqual(s['gross_revenue'],200);self.assertEqual(s['refunded_total'],20.45);self.assertEqual(s['net_sales'],200)
        self.assertEqual(self.send('POST',path,dict(request_key=str(uuid.uuid4()),amount='200.01',reason='Too much')).status_code,400)
        r=self.send('POST',path,dict(request_key=str(uuid.uuid4()),amount='200',reason='Remaining refund'));self.assertEqual(r.json['order']['payment_status'],'Refunded')
        self.assertEqual(self.summary()['gross_revenue'],0)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,18);self.assertEqual(len(db.get(OrderPayment,order['id']).refunds),2)

    def test_paid_cancel_reverses_collection_and_releases_reservation(self):
        order=self.paid_order();self.login(True)
        r=self.send('PATCH',f"/api/admin/sales/{order['id']}",dict(status='Cancelled'));self.assertEqual(r.status_code,200,r.json)
        self.assertEqual(self.summary()['gross_revenue'],0)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,20)

    def test_receipt_and_order_ownership(self):
        order=self.paid_order();self.login(email='two@example.test')
        self.assertEqual(self.client.get(order['receipt_url']).status_code,404)
        self.assertEqual(self.client.get('/api/orders/'+order['id']).status_code,404)
        self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/payment-attempts",dict(request_key=str(uuid.uuid4()))).status_code,404)

    def test_report_dates_chart_and_csv_reconcile(self):
        order=self.paid_order();self.login(True);s=self.summary()
        self.assertEqual(sum(d['amount'] for d in s['chart']),s['gross_revenue'])
        self.assertEqual(sum(s['payment_methods'].values()),s['gross_revenue'])
        self.assertEqual(sum(s['channels'].values()),s['gross_revenue'])
        params=f"start={s['start']}&end={s['end']}&metric=revenue"
        rows=self.client.get('/api/admin/transactions?'+params).json
        csv_response=self.client.get('/api/admin/transactions/export?'+params)
        exported=list(csv.DictReader(io.StringIO(csv_response.data.decode('utf-8-sig'))))
        self.assertEqual(len(exported),rows['count']);self.assertEqual(Decimal(exported[0]['amount']),Decimal('220.45'))
        self.assertEqual(self.client.get('/api/admin/summary?start=bad').status_code,400)
        self.assertEqual(self.client.get('/api/admin/summary?start=2026-12-01&end=2026-01-01').status_code,400)
        self.assertEqual(self.client.get('/api/admin/transactions?sort=invalid').status_code,400)

    def test_manila_boundary_uses_collection_date_not_order_date(self):
        order=self.paid_order()
        with self.factory() as db:
            o=db.get(Order,order['id']);o.created_at=datetime(2026,1,1,tzinfo=timezone.utc)
            o.payment_record.collected_at=datetime(2026,1,2,16,30,tzinfo=timezone.utc);db.commit()
            data=report([o],dict(start='2026-01-03',end='2026-01-03'))
            self.assertEqual(data['gross_revenue'],220.45);self.assertEqual(data['total_orders'],0)
            self.assertEqual(report([o],dict(start='2026-01-02',end='2026-01-02'))['gross_revenue'],0)
        self.assertEqual(local_date(datetime(2026,1,2,16,tzinfo=timezone.utc)).isoformat(),'2026-01-03')

    def test_financial_decimal_validation(self):
        for value in ['NaN','Infinity','0.001','9999999999999999']:
            with self.subTest(value=value),self.assertRaises(ValueError):money(value)
        self.assertEqual(money('100.10')*3,Decimal('300.30'))

    def test_large_discount_centavo_allocation_never_creates_negative_product_sales(self):
        from types import SimpleNamespace
        from audia.services.ledger import merchandise_allocations
        order=SimpleNamespace(subtotal=Decimal('50'),discount=Decimal('49.70'),
            items=[SimpleNamespace(price=Decimal('1'),quantity=1) for _ in range(50)])
        values=merchandise_allocations(order)
        self.assertEqual(sum(values),Decimal('0.30'));self.assertTrue(all(v>=0 for v in values))

    def test_refund_in_later_period_and_metric_support_reconcile(self):
        order=self.paid_order()
        with self.factory() as db:
            db.get(OrderPayment,order['id']).collected_at=datetime(2026,1,2,tzinfo=timezone.utc);db.commit()
        self.login(True)
        r=self.send('POST',f"/api/admin/transactions/{order['id']}/refunds",dict(request_key=str(uuid.uuid4()),amount='20.45',reason='Later period refund'))
        self.assertEqual(r.status_code,200,r.json)
        s=self.summary();self.assertEqual(s['gross_sales'],0);self.assertEqual(s['net_sales'],-20.45);self.assertEqual(s['gross_revenue'],-20.45)
        params=f"start={s['start']}&end={s['end']}"
        rows=self.client.get('/api/admin/transactions?'+params+'&metric=revenue').json['transactions']
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['collection_in_period'],0);self.assertEqual(rows[0]['refunds_in_period'],20.45)
        self.assertEqual(self.client.get('/api/admin/transactions?'+params+'&metric=gross_sales').json['count'],0)
        self.assertEqual(self.client.get('/api/admin/transactions?'+params+'&metric=refunded_total').json['count'],1)

    def test_discounted_merchandise_allocations_and_refund_excludes_shipping_tax(self):
        self.login(True)
        body=dict(request_key=str(uuid.uuid4()),customer='Discount Customer',payment_method='cash',confirmed=True,
                  items=[dict(product_id=1,quantity=1),dict(product_id=2,quantity=1)],discount='0.01',discount_reason='Centavo discount')
        r=self.send('POST','/api/admin/pos',body);self.assertEqual(r.status_code,201,r.json)
        s=self.summary();self.assertEqual(round(sum(s['categories'].values()),2),s['net_sales'])
        order=r.json['order']
        # Exercise financial allocation with configured fees without adding a new
        # customer-facing tax/shipping policy to this free-shipping school store.
        with self.factory() as db:
            o=db.get(Order,order['id']);o.tax=Decimal('10');o.shipping_fee=Decimal('20');o.total+=Decimal('30');o.payment_record.amount=o.total;db.commit()
        r=self.send('POST',f"/api/admin/transactions/{order['id']}/refunds",dict(request_key=str(uuid.uuid4()),amount='50',reason='Proportional fee refund'))
        self.assertEqual(r.status_code,200,r.json)
        with self.factory() as db:
            p=db.get(OrderPayment,order['id']);self.assertLess(p.refunds[0].merchandise_amount,Decimal('50'))
            remaining=p.amount-Decimal('50')
        r=self.send('POST',f"/api/admin/transactions/{order['id']}/refunds",dict(request_key=str(uuid.uuid4()),amount=str(remaining),reason='Complete remaining refund'))
        self.assertEqual(r.status_code,200,r.json)
        self.assertEqual(self.summary()['net_sales'],0)

    def test_returns_and_fulfillment_refund_never_automatically_restock(self):
        order=self.paid_order();self.login(True);path=f"/api/admin/sales/{order['id']}"
        for status in ['Processing','Shipped','Delivered','Returned']:
            r=self.send('PATCH',path,dict(status=status));self.assertEqual(r.status_code,200,r.json)
        self.assertEqual(self.send('PATCH',path,dict(status='Refunded')).status_code,400)
        self.assertEqual(self.send('PATCH',path,dict(status='Refunded',refund_confirmed=True)).status_code,200)
        self.assertEqual(self.summary()['gross_revenue'],0)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,18)

    def test_legacy_refunded_payment_cannot_be_refunded_twice(self):
        order=self.paid_order();self.login(True)
        with self.factory() as db:
            db.get(OrderPayment,order['id']).status='Refunded';db.commit()
        r=self.send('POST',f"/api/admin/transactions/{order['id']}/refunds",dict(request_key=str(uuid.uuid4()),amount='1',reason='Duplicate refund'))
        self.assertEqual(r.status_code,400)

    def test_transaction_pagination_filters_and_csv_formula_safety(self):
        self.login(True)
        for i in range(21):
            r=self.send('POST','/api/admin/pos',dict(request_key=str(uuid.uuid4()),customer='=HYPERLINK("example.test")',payment_method='cash',
                confirmed=True,items=[dict(product_id=2 if i else 1,quantity=1)]))
            self.assertEqual(r.status_code,201,r.json)
        page1=self.client.get('/api/admin/transactions?period=month&channel=pos').json
        page2=self.client.get('/api/admin/transactions?period=month&channel=pos&page=2').json
        self.assertEqual(page1['count'],21);self.assertEqual(len(page1['transactions']),20);self.assertEqual(len(page2['transactions']),1)
        data=self.client.get('/api/admin/transactions/export?period=month&channel=pos&method=Cash').data.decode('utf-8-sig')
        exported=list(csv.DictReader(io.StringIO(data)));self.assertEqual(len(exported),21);self.assertTrue(exported[0]['customer'].startswith("'="))

    def test_migration_current_schema_no_op(self):
        self.assertIsNone(upgrade_database(app))

    def test_migration_never_infers_payment_from_delivered_legacy_order(self):
        order=self.checkout('cod').json['order']
        with self.factory() as db:
            db.execute(text('DELETE FROM payment_events WHERE payment_id = :id'),{'id':order['id']})
            db.execute(text('DELETE FROM order_payments WHERE order_id = :id'),{'id':order['id']})
            db.get(Order,order['id']).status='Delivered';db.commit()
        with TemporaryDirectory(dir=Path(app.root_path)/'instance') as folder:
            from flask import Flask
            temp_app=Flask('backfill_test',instance_path=folder);temp_app.extensions['engine']=self.engine
            self.assertTrue(upgrade_database(temp_app).is_file())
            self.assertIsNone(upgrade_database(temp_app))
        with self.factory() as db:
            p=db.get(OrderPayment,order['id']);self.assertEqual(p.status,'Pending');self.assertIsNone(p.collected_at)

    def test_migration_preserves_legacy_data_and_repeats_safely(self):
        legacy=create_engine('sqlite://')
        metadata=Base.metadata
        with legacy.begin() as c:
            for table in metadata.sorted_tables:
                if table.name not in ('payment_events','refunds','refund_requests','refund_request_events','uploads','inventory_movements','deliveries','account_statuses','notifications','admin_audits'):
                    table.create(c)
            # Use the current compatible schema then remove additive columns to
            # reproduce the previous committed schema without real customer data.
            c.execute(text("INSERT INTO users (id,name,email,password_hash,role,address,phone,created_at) VALUES (1,'Legacy','legacy@example.test','hash','customer','','',CURRENT_TIMESTAMP)"))
            c.execute(text("INSERT INTO orders (id,user_id,customer,email,address,phone,total,status,payment,request_key,created_at) VALUES ('LEGACY',1,'Legacy','legacy@example.test','Address','09171234567',100,'Confirmed','GCash','legacy-request-key',CURRENT_TIMESTAMP)"))
            c.execute(text("INSERT INTO order_payments (order_id,status,reference,collected_at) VALUES ('LEGACY','Demo paid','DEMO-OLD',CURRENT_TIMESTAMP)"))
            for index in inspect(c).get_indexes('orders'):
                if index['name']=='ix_orders_channel':c.execute(text('DROP INDEX ix_orders_channel'))
            # SQLite cannot drop a UNIQUE column, so recreate legacy payment table.
            c.execute(text('DROP TABLE order_payments'))
            c.execute(text('CREATE TABLE order_payments (order_id VARCHAR(24) PRIMARY KEY REFERENCES orders(id), status VARCHAR(16), reference VARCHAR(200), collected_at DATETIME, collected_by INTEGER)'))
            c.execute(text("INSERT INTO order_payments VALUES ('LEGACY','Demo paid','DEMO-OLD',CURRENT_TIMESTAMP,NULL)"))
            for col in ['subtotal','discount','shipping_fee','tax','channel']:
                c.execute(text('ALTER TABLE orders DROP COLUMN '+col))
        with TemporaryDirectory(dir=Path(app.root_path)/'instance') as folder:
            from flask import Flask
            temp_app=Flask('migration_test',instance_path=folder);temp_app.extensions['engine']=legacy
            backup=upgrade_database(temp_app);self.assertTrue(backup.is_file())
            with legacy.connect() as c:
                row=c.execute(text('SELECT total,subtotal,discount,channel FROM orders')).one()
                self.assertEqual(tuple(row),(100,100,0,'online'))
                self.assertEqual(c.execute(text('SELECT status FROM order_payments')).scalar(),'Paid')
            self.assertIsNone(upgrade_database(temp_app))
        legacy.dispose()


if __name__ == '__main__':
    unittest.main()
