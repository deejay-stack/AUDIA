"""Concurrency checks in a temporary, isolated PostgreSQL schema.

Uses the configured database server, creates only audia_test_<random> tables,
and removes that exact schema in finally. Never seeds public application tables.
"""
import secrets
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from app import app
from audia.database.models import Base, User, Product, Order, OrderPayment, LoginSession, RefundRequest, InventoryMovement, Setting, now
from audia.routes.auth.auth import digest


def run():
    configured=app.extensions['engine']
    if configured.dialect.name!='postgresql':
        raise RuntimeError('This test requires configured PostgreSQL.')
    schema='audia_test_'+secrets.token_hex(12)
    with configured.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA {schema}'))
    engine=create_engine(configured.url,connect_args={'options':f'-csearch_path={schema}'},pool_size=8)
    original=app.extensions.copy();original_config=app.config.copy()
    try:
        Base.metadata.create_all(engine)
        factory=sessionmaker(engine,expire_on_commit=False)
        app.extensions.update(engine=engine,db_factory=factory)
        app.config.update(TESTING=True,SECRET_KEY='isolated-concurrency-tests',DEMO_PAYMENT_TEST_CONTROLS=True)
        with factory() as db:
            db.add_all([User(id=i,name=f'Concurrency {i}',email=f'test{i}@example.test',password_hash='not-a-login',role='customer') for i in range(1,7)])
            db.add(User(id=7,name='Concurrency Admin',email='admin@example.test',password_hash='not-a-login',role='admin'))
            db.add(Product(id=1,name='CONCURRENCY_TEST',brand='Test',category='Acoustic',price=Decimal('10.10'),stock=2))
            db.flush()
            for i in range(1,8):
                db.add(LoginSession(token_hash=digest(f'test-session-{i}'),user_id=i,expires_at=now()+timedelta(hours=1)))
            db.commit()
        def client(user):
            c=app.test_client()
            with c.session_transaction() as session:
                session.update(sid=f'test-session-{user}',csrf='test-csrf',auth_role='admin' if user == 7 else 'customer')
            return c
        def checkout(user,key,barrier,method='gcash'):
            c=client(user);barrier.wait(timeout=10)
            r=c.post('/api/orders',json=dict(request_key=key,payment_method=method,address='123 Isolated Test Street',phone='09171234567',
                                           items=[dict(product_id=1,quantity=1)]),headers={'X-CSRF-Token':'test-csrf'})
            return r.status_code,r.json
        barrier=threading.Barrier(6)
        with ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(lambda i:checkout(i,f'concurrent-stock-key-{i}',barrier),range(1,7)))
        assert sum(code==201 for code,_ in results)==2,results
        assert sum(code==400 for code,_ in results)==4,results
        with factory() as db:
            assert db.get(Product,1).stock==0
            assert len(list(db.scalars(select(Order))))==2
            db.get(Product,1).stock=5;db.commit()
        print('PASS: six concurrent customers cannot oversell two units',flush=True)
        barrier=threading.Barrier(6)
        with ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(lambda _:checkout(1,'duplicate-checkout-key',barrier),range(6)))
        assert sum(code==201 for code,_ in results)==1,results
        assert len({r['order']['id'] for _,r in results})==1,results
        with factory() as db:assert db.get(Product,1).stock==4
        print('PASS: six duplicate checkouts create one order and one stock deduction',flush=True)
        order=results[0][1]['order'];c=client(1)
        response=c.post(f"/api/orders/{order['id']}/payment-attempts",json=dict(request_key='concurrent-payment-key'),headers={'X-CSRF-Token':'test-csrf'})
        assert response.status_code==200,response.json
        attempt=response.json['attempt'];barrier=threading.Barrier(6)
        def confirm(_):
            c=client(1);barrier.wait(timeout=10)
            return c.post(f"/api/orders/{order['id']}/payment-attempts/{attempt['id']}/confirm",json=dict(outcome='success',gcash_number='09170000000'),headers={'X-CSRF-Token':'test-csrf'})
        with ThreadPoolExecutor(max_workers=6) as pool: responses=list(pool.map(confirm,range(6)))
        assert all(r.status_code==200 for r in responses),[(r.status_code,r.json) for r in responses]
        with factory() as db:
            p=db.get(OrderPayment,order['id'])
            assert sum(e.new_status=='Paid' for e in p.events)==1
            assert p.amount==Decimal('10.10')
            assert p.receipt_number
        print('PASS: six simultaneous payment confirmations create one collection and receipt',flush=True)
        barrier=threading.Barrier(6)
        def refund_one(key):
            c=client(7);barrier.wait(timeout=10)
            return c.post(f"/api/admin/transactions/{order['id']}/refunds",json=dict(request_key=key,amount='2.00',reason='Concurrent test refund'),headers={'X-CSRF-Token':'test-csrf'})
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(lambda _:refund_one('duplicate-refund-key'),range(6)))
        assert all(r.status_code==200 for r in responses)
        with factory() as db:assert len(db.get(OrderPayment,order['id']).refunds)==1
        barrier=threading.Barrier(6)
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(lambda i:refund_one(f'new-refund-request-{i}'),range(6)))
        assert sum(r.status_code==200 for r in responses)==4
        assert sum(r.status_code==400 for r in responses)==2
        with factory() as db:
            p=db.get(OrderPayment,order['id'])
            assert sum(r.amount for r in p.refunds)==Decimal('10.00')
            assert len(p.refunds)==5
        print('PASS: duplicate and simultaneous refunds cannot over-refund a collection',flush=True)
        code,data=checkout(1,'new-cancellation-concurrency',threading.Barrier(1));assert code==201,data
        fresh=data['order'];c=client(1);headers={'X-CSRF-Token':'test-csrf'}
        a=c.post(f"/api/orders/{fresh['id']}/payment-attempts",json=dict(request_key='new-cancel-payment'),headers=headers).json['attempt']
        assert c.post(f"/api/orders/{fresh['id']}/payment-attempts/{a['id']}/confirm",json=dict(outcome='success',gcash_number='09170000000'),headers=headers).status_code==200
        barrier=threading.Barrier(6)
        def cancel_one(_):
            c=client(1);barrier.wait(timeout=10)
            return c.post(f"/api/orders/{fresh['id']}/cancel",json=dict(request_key='same-cancel-request',reason='Changed my mind'),headers=headers)
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(cancel_one,range(6)))
        assert all(r.status_code==200 for r in responses),[(r.status_code,r.json) for r in responses]
        assert len({r.json['request']['id'] for r in responses})==1
        req=responses[0].json['request'];staff=client(7)
        for status in ['Approved','Refund Processing']:
            assert staff.patch('/api/admin/requests/'+req['id'],json=dict(status=status,note='Concurrent school cancellation'),headers=headers).status_code==200
        barrier=threading.Barrier(6)
        def finish_cancel(_):
            c=client(7);barrier.wait(timeout=10)
            return c.patch('/api/admin/requests/'+req['id'],json=dict(status='Refunded',note='Concurrent school cancellation'),headers=headers)
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(finish_cancel,range(6)))
        assert all(r.status_code==200 for r in responses),[(r.status_code,r.json) for r in responses]
        with factory() as db:
            assert len(db.get(OrderPayment,fresh['id']).refunds)==1
            assert db.get(Order,fresh['id']).status=='Cancelled'
            assert len(list(db.scalars(select(InventoryMovement).where(InventoryMovement.order_id==fresh['id'],InventoryMovement.delta>0))))==1
        print('PASS: concurrent paid cancellations create one request, reversal and stock release',flush=True)
        with factory() as db:db.add(Setting(key='bank_mode',value='manual'));db.commit()
        code,data=checkout(1,'new-bank-concurrency-key',threading.Barrier(1),'bpi');assert code==201,data
        bank=data['order'];c=client(1)
        a=c.post(f"/api/orders/{bank['id']}/payment-attempts",json=dict(request_key='new-bank-authorization'),headers=headers).json['attempt']
        assert c.post(f"/api/orders/{bank['id']}/payment-attempts/{a['id']}/confirm",json=dict(outcome='success',gcash_number='09170000000'),headers=headers).json['order']['payment_status']=='Pending Verification'
        barrier=threading.Barrier(6)
        def verify(_):
            c=client(7);barrier.wait(timeout=10)
            return c.post(f"/api/admin/payments/{bank['id']}/verify",json=dict(attempt_id=a['id'],action='approve',note='Concurrent school review'),headers=headers)
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(verify,range(6)))
        assert all(r.status_code==200 for r in responses)
        with factory() as db:assert sum(e.new_status=='Paid' for e in db.get(OrderPayment,bank['id']).events)==1
        print('PASS: concurrent bank approvals record one internal collection',flush=True)
        for status in ['Processing','Shipped','Delivered']:
            assert staff.patch('/api/admin/sales/'+bank['id'],json=dict(status=status),headers=headers).status_code==200
        item_id=client(1).get('/api/orders/'+bank['id']).json['order']['items'][0]['id']
        req=client(1).post(f"/api/orders/{bank['id']}/requests",json=dict(request_key='new-return-concurrency',reason='Received damaged product',items=[dict(item_id=item_id,quantity=1)]),headers=headers).json['request']
        for status in ['Approved','Awaiting Return','Item Received']:
            assert staff.patch('/api/admin/requests/'+req['id'],json=dict(status=status,note='School return inspection'),headers=headers).status_code==200
        barrier=threading.Barrier(6)
        def restock(_):
            c=client(7);barrier.wait(timeout=10)
            return c.patch('/api/admin/requests/'+req['id'],json=dict(status='Refund Processing',restock=True,note='School returned goods accepted'),headers=headers)
        with ThreadPoolExecutor(max_workers=6) as pool:responses=list(pool.map(restock,range(6)))
        assert all(r.status_code==200 for r in responses)
        with factory() as db:
            assert db.get(RefundRequest,req['id']).restocked
            assert len(list(db.scalars(select(InventoryMovement).where(InventoryMovement.order_id==bank['id'],InventoryMovement.delta>0))))==1
        print('PASS: concurrent return inspection restores each returned unit once',flush=True)
    finally:
        app.extensions.clear();app.extensions.update(original)
        app.config.clear();app.config.update(original_config)
        engine.dispose()
        # Generated identifier contains only our fixed prefix and random hex.
        assert schema.startswith('audia_test_') and schema[11:].isalnum()
        with configured.begin() as connection:connection.execute(text(f'DROP SCHEMA {schema} CASCADE'))
        print('Temporary PostgreSQL test schema removed.',flush=True)


if __name__=='__main__':run()
