"""Regression coverage for customer requests, reviews, delivery and QR verification."""
import io
import unittest
import uuid
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from sqlalchemy import select, inspect, text
from flask import Flask
from PIL import Image
import test_commerce as fixture
from audia.database.models import (Order, OrderPayment, Product, RefundRequest, InventoryMovement,
                                   Setting, Upload, now)
from audia.database.migrations import upgrade_database


class OperationsTests(unittest.TestCase):
    setUpClass=classmethod(fixture.CommerceTests.setUpClass.__func__)
    setUp=fixture.CommerceTests.setUp
    tearDown=fixture.CommerceTests.tearDown
    send=fixture.CommerceTests.send
    login=fixture.CommerceTests.login
    checkout=fixture.CommerceTests.checkout
    start=fixture.CommerceTests.start
    confirm=fixture.CommerceTests.confirm
    paid_order=fixture.CommerceTests.paid_order
    summary=fixture.CommerceTests.summary

    def configure(self, **values):
        with self.factory() as db:
            for key,value in values.items():db.merge(Setting(key=key,value=str(value)))
            db.commit()

    def deliver(self,order):
        self.login(True)
        for status in ['Processing','Packed','Shipped','Out for Delivery','Delivered']:
            r=self.send('PATCH',f"/api/admin/sales/{order['id']}",{'status':status})
            self.assertEqual(r.status_code,200,r.json)
        self.login()
        return self.client.get('/api/orders/'+order['id']).json['order']

    def request(self,order,**changes):
        body=dict(request_key=str(uuid.uuid4()),reason='Received damaged product',explanation='Synthetic school test',
                  items=[dict(item_id=order['items'][0]['id'],quantity=1)])
        body.update(changes)
        return self.send('POST',f"/api/orders/{order['id']}/requests",body)

    def review(self,r,status,**changes):
        response=self.send('PATCH','/api/admin/requests/'+r['id'],dict(status=status,note='Store reviewed synthetic request',**changes))
        self.assertEqual(response.status_code,200,response.json)
        return response.json['request']

    def test_manual_bank_pending_review_approval_and_receipt_replay(self):
        self.configure(bank_mode='manual')
        order=self.checkout('bpi').json['order'];started=self.start(order).json
        self.assertTrue(started['attempt']['manual_review']);self.assertEqual(started['profile']['test_account'],'TEST-BPI-001')
        r=self.confirm(order,started['attempt']);self.assertEqual(r.json['order']['payment_status'],'Pending Verification')
        self.assertIsNone(r.json['order']['receipt_url']);self.assertEqual(self.start(order).status_code,400)
        path=f"/api/admin/payments/{order['id']}/verify";body=dict(action='approve',note='School bank review',attempt_id=started['attempt']['id'])
        self.assertEqual(self.send('POST',path,body).status_code,403)
        self.login(True);self.assertEqual(self.summary()['gross_revenue'],0)
        result=self.send('POST',path,body);self.assertEqual(result.status_code,200,result.json)
        self.assertEqual(result.json['order']['payment_status'],'Paid')
        receipt=result.json['order']['receipt_url'];self.assertEqual(self.client.get(receipt).status_code,200)
        self.assertEqual(self.send('POST',path,body).json['order']['receipt_url'],receipt)
        self.assertEqual(self.summary()['gross_revenue'],220.45)

    def test_bank_mode_captured_at_authorization_and_rejected_retry(self):
        self.configure(bank_mode='manual')
        order=self.checkout('bdo').json['order'];a=self.start(order).json['attempt']
        self.configure(bank_mode='automatic');r=self.confirm(order,a)
        self.assertEqual(r.json['order']['payment_status'],'Pending Verification')
        self.login(True)
        r=self.send('POST',f"/api/admin/payments/{order['id']}/verify",dict(action='reject',note='Authorization rejected',attempt_id=a['id']))
        self.assertEqual(r.json['order']['payment_status'],'Failed');self.login()
        a=self.start(order).json['attempt'];self.assertFalse(a['manual_review'])
        self.assertEqual(self.confirm(order,a).json['order']['payment_status'],'Paid')

    def test_cancel_pending_bank_voids_review_and_releases_stock_once(self):
        self.configure(bank_mode='manual');order=self.checkout('bpi').json['order'];a=self.start(order).json['attempt'];self.confirm(order,a)
        for _ in range(2):self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/cancel",dict(reason='Wrong address')).status_code,200)
        self.login(True)
        self.assertEqual(self.send('POST',f"/api/admin/payments/{order['id']}/verify",dict(action='approve',note='Late authorization',attempt_id=a['id'])).status_code,400)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,20)

    def test_paid_cancellation_request_review_reversal_and_replay(self):
        order=self.paid_order();key=str(uuid.uuid4());body=dict(request_key=key,reason='Changed my mind')
        r=self.send('POST',f"/api/orders/{order['id']}/cancel",body);self.assertEqual(r.status_code,200,r.json)
        req=r.json['request'];self.assertEqual(r.json['order']['status'],'Confirmed')
        self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/cancel",body).json['request']['id'],req['id'])
        self.login(True);self.assertEqual(self.summary()['gross_revenue'],220.45)
        req=self.review(req,'Under Review');req=self.review(req,'Approved');req=self.review(req,'Refund Processing');req=self.review(req,'Refunded')
        self.assertEqual(self.review(req,'Refunded')['refund_id'],req['refund_id']);self.assertEqual(self.summary()['gross_revenue'],0)
        self.assertEqual(self.client.get(req['confirmation_url']).status_code,200)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,20);self.assertEqual(db.get(Order,order['id']).status,'Cancelled')

    def test_return_inspection_partial_refund_and_no_double_restock(self):
        order=self.deliver(self.paid_order());r=self.request(order);self.assertEqual(r.status_code,201,r.json);req=r.json['request']
        self.assertEqual(req['amount'],100.1);self.login(True)
        req=self.review(req,'Approved',amount='80.00')
        self.assertEqual(self.send('PATCH','/api/admin/requests/'+req['id'],dict(status='Refund Processing',note='Skip returned item')).status_code,400)
        req=self.review(req,'Awaiting Return');req=self.review(req,'Item Received');req=self.review(req,'Refund Processing',restock=True)
        req=self.review(req,'Refunded');self.assertEqual(req['status'],'Partially Refunded');self.assertEqual(self.summary()['gross_revenue'],140.45)
        with self.factory() as db:self.assertEqual(db.get(Product,1).stock,19)
        self.assertEqual(self.send('PATCH','/api/admin/requests/'+req['id'],dict(status='Refund Processing',restock=True,note='Duplicate restock')).status_code,400)
        self.login();self.assertEqual(self.client.get(req['confirmation_url']).status_code,200)

    def test_request_bounds_duplicate_items_and_rejection(self):
        unpaid=self.checkout().json['order'];self.assertEqual(self.request(unpaid).status_code,400)
        order=self.deliver(self.paid_order());line=dict(item_id=order['items'][0]['id'],quantity=1)
        for items in [[dict(line,quantity=3)],[line,line],[dict(line,item_id=9999)]]:
            self.assertEqual(self.request(order,items=items).status_code,400)
        req=self.request(order).json['request'];self.assertEqual(self.request(order).status_code,400)
        self.login(True);self.assertEqual(self.send('PATCH','/api/admin/requests/'+req['id'],dict(status='Approved',amount='101',note='Over request amount')).status_code,400)
        req=self.review(req,'Rejected');self.review(req,'Closed');self.assertEqual(self.summary()['refunded_total'],0)

    def test_refund_cannot_exceed_later_remaining_collection(self):
        order=self.deliver(self.paid_order());req=self.request(order).json['request'];self.login(True)
        req=self.review(req,'Approved');req=self.review(req,'Awaiting Return');req=self.review(req,'Item Received');req=self.review(req,'Refund Processing')
        self.send('POST',f"/api/admin/transactions/{order['id']}/refunds",dict(request_key=str(uuid.uuid4()),amount='200',reason='Separate adjustment'))
        r=self.send('PATCH','/api/admin/requests/'+req['id'],dict(status='Refunded',note='Attempt stale approved amount'))
        self.assertEqual(r.status_code,400)
        with self.factory() as db:self.assertIsNone(db.get(RefundRequest,req['id']).refund_id)

    def test_shipped_cancellation_return_window_and_policy(self):
        order=self.deliver(self.paid_order())
        self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/cancel",dict(request_key=str(uuid.uuid4()),reason='Change mind')).status_code,400)
        with self.factory() as db:
            o=db.get(Order,order['id']);next(e for e in o.events if e.status=='Delivered').created_at=now()-timedelta(days=15);db.commit()
        self.assertEqual(self.request(order).status_code,400)

    def test_receipt_qr_verification_and_private_access(self):
        order=self.paid_order()
        with self.factory() as db:number=db.get(OrderPayment,order['id']).receipt_number
        verify='/verify/receipts/'+number;qr='/receipts/qr/'+number+'.svg'
        r=self.client.get(qr);self.assertEqual(r.status_code,200);self.assertEqual(r.mimetype,'image/svg+xml');self.assertIn(b'<svg',r.data)
        self.assertIn(b'Record verified',self.client.get(verify).data)
        self.assertEqual(self.client.get('/verify/receipts/invalid').status_code,404)
        self.login(email='two@example.test')
        self.assertEqual(self.client.get(verify).status_code,404);self.assertEqual(self.client.get(qr).status_code,404)
        self.assertEqual(self.client.get('/uploads/not-real').status_code,404)

    def test_delivery_validation_authorization_and_persistence(self):
        order=self.paid_order();path=f"/api/admin/orders/{order['id']}/delivery"
        body=dict(method='School route',reference='SIM-SCHOOL',window='Tomorrow afternoon',route=[[14.5,121],[14.6,121.1]],progress=1,note='Simulated waypoint')
        self.assertEqual(self.send('PUT',path,body).status_code,403);self.login(True)
        for changes in [dict(route=[[91,1],[0,0]]),dict(progress=2),dict(route='invalid'),dict(route=[[0,0],[float('inf'),0]])]:
            self.assertEqual(self.send('PUT',path,dict(body,**changes)).status_code,400)
        r=self.send('PUT',path,dict(body,status='Processing'));self.assertEqual(r.status_code,200,r.json)
        self.login();r=self.client.get(f"/api/orders/{order['id']}/delivery");self.assertEqual(r.json['delivery']['progress'],1);self.assertTrue(r.json['delivery']['simulated'])
        self.login(email='two@example.test');self.assertEqual(self.client.get(f"/api/orders/{order['id']}/delivery").status_code,404)

    def test_shipping_fee_enabled_methods_and_settings_validation(self):
        self.configure(shipping_fee='50.25',enabled_methods='gcash,cod')
        self.assertEqual(self.checkout('bpi').status_code,400)
        order=self.checkout().json['order'];self.assertEqual(order['amount'],270.7);self.assertEqual(order['shipping_fee'],50.25)
        self.assertEqual(self.checkout(expected_total='220.45').status_code,400)
        self.login(True)
        for values in [dict(shipping_fee='-1'),dict(bank_mode='unknown'),dict(test_account_bpi='123456789012'),dict(return_days='0'),dict(google_maps_key='bad'),dict(enabled_methods='realbank')]:
            self.assertEqual(self.send('PUT','/api/admin/settings',values).status_code,400)
        self.assertEqual(self.send('PUT','/api/admin/settings',dict(bank_mode='manual',shipping_fee='0.00')).status_code,200)

    def test_image_upload_content_validation_ownership_and_evidence(self):
        original=fixture.app.instance_path
        with TemporaryDirectory(dir=Path(original)) as folder:
            fixture.app.instance_path=folder
            try:
                invalid=self.client.post('/api/uploads',data={'purpose':'evidence','image':(io.BytesIO(b'<svg onload="alert(1)">'),'attack.svg')},headers={'X-CSRF-Token':self.csrf})
                self.assertEqual(invalid.status_code,400)
                image=io.BytesIO();Image.new('RGB',(12,12),'green').save(image,'PNG');image.seek(0)
                r=self.client.post('/api/uploads',data={'purpose':'evidence','image':(image,'photo.png')},headers={'X-CSRF-Token':self.csrf})
                self.assertEqual(r.status_code,201,r.json);upload=r.json
                with self.client.get(upload['url']) as response:self.assertEqual(response.mimetype,'image/jpeg')
                self.login(email='two@example.test');self.assertEqual(self.client.get(upload['url']).status_code,404)
                self.login();order=self.deliver(self.paid_order());req=self.request(order,evidence=[upload['id']]).json['request']
                self.assertEqual(req['evidence'],[upload['url']]);self.login(True)
                with self.client.get(upload['url']) as response:self.assertEqual(response.status_code,200)
            finally:fixture.app.instance_path=original

    def test_inventory_movements_and_customer_suspension(self):
        order=self.checkout().json['order'];self.send('POST',f"/api/orders/{order['id']}/cancel",dict(reason='Wrong item'))
        self.login(True);r=self.client.get('/api/admin/inventory/movements?product_id=1');self.assertEqual(r.json['count'],2)
        self.assertEqual(sum(m['delta'] for m in r.json['movements']),0)
        r=self.client.get('/api/admin/customers/1');self.assertEqual(len(r.json['orders']),1);self.assertNotIn('password_hash',r.json['customer'])
        self.assertEqual(len(self.client.get('/api/admin/products/1/history').json['orders']),1)
        self.assertEqual(self.client.get('/api/admin/audit').status_code,200)
        self.assertEqual(self.send('PUT','/api/admin/customers/2/status',dict(suspended=True,reason='Cannot change admin')).status_code,404)
        self.assertEqual(self.send('PUT','/api/admin/customers/1/status',dict(suspended=True,reason='School review')).status_code,200)
        self.send('POST','/api/auth/logout',{});self.csrf=self.client.get('/api/auth/session').json['csrf_token']
        self.assertEqual(self.send('POST','/api/auth/login',dict(email='one@example.test',password=self.password)).status_code,401)

    def test_request_information_reply_and_notification_ownership(self):
        order=self.deliver(self.paid_order());req=self.request(order).json['request'];self.login(True)
        req=self.review(req,'Under Review')
        r=self.send('PATCH','/api/admin/requests/'+req['id'],dict(status='Under Review',note='Please describe the damage'))
        self.assertEqual(r.status_code,200)
        self.login();r=self.send('POST',f"/api/orders/{order['id']}/requests/{req['id']}/reply",dict(note='The neck was damaged'))
        self.assertEqual(r.status_code,200);self.assertIn('Customer:',r.json['request']['events'][-1]['note'])
        r=self.client.get('/api/account/notifications');self.assertTrue(any('Please describe' in n['message'] for n in r.json['notifications']))
        self.assertTrue(any(not n['read'] for n in r.json['notifications']))
        self.assertEqual(self.send('POST','/api/account/notifications/read',{}).status_code,200)
        self.assertTrue(all(n['read'] for n in self.client.get('/api/account/notifications').json['notifications']))
        self.login(email='two@example.test');self.assertEqual(self.client.get('/api/account/notifications').json['notifications'],[])
        self.assertEqual(self.send('POST',f"/api/orders/{order['id']}/requests/{req['id']}/reply",dict(note='Other account')).status_code,404)

    def test_additive_migration_from_pre_request_schema(self):
        with self.engine.begin() as c:
            for name in ['uploads','refund_request_events','refund_requests','inventory_movements','deliveries','account_statuses']:
                c.execute(text('DROP TABLE '+name))
            c.execute(text('ALTER TABLE payment_attempts DROP COLUMN manual_review'))
            c.execute(text('ALTER TABLE payment_attempts DROP COLUMN payer_number_masked'))
        with TemporaryDirectory(dir=Path(fixture.app.instance_path)) as folder:
            app=Flask('upgrade_operations_test',instance_path=folder);app.extensions['engine']=self.engine
            self.assertTrue(upgrade_database(app).is_file());self.assertIsNone(upgrade_database(app))
        with self.engine.connect() as c:
            self.assertIn('refund_requests',inspect(c).get_table_names());self.assertEqual(c.execute(text('SELECT count(*) FROM users')).scalar(),3)

    def test_gcash_number_required_validated_masked_and_replay_safe(self):
        from audia.database.models import PaymentAttempt
        order=self.checkout().json['order'];attempt=self.start(order).json['attempt']
        path=f"/api/orders/{order['id']}/payment-attempts/{attempt['id']}/confirm"
        for number in ['', '123', '08171234567', 9171234567]:
            response=self.send('POST',path,dict(outcome='success',gcash_number=number))
            self.assertEqual(response.status_code,400,response.json)
        with self.factory() as db:self.assertIsNone(db.get(OrderPayment,order['id']).receipt_number)
        response=self.send('POST',path,dict(outcome='success',gcash_number='+639189876543'))
        self.assertEqual(response.status_code,200,response.json)
        self.assertEqual(response.json['attempt']['payer_number_masked'],'09•••••6543')
        self.assertEqual(response.json['order']['payment_status'],'Paid')
        self.assertNotIn('09189876543',str(response.json));self.assertNotIn('+639189876543',str(response.json))
        replay=self.send('POST',path,dict(outcome='success',gcash_number='invalid'))
        self.assertEqual(replay.json['order']['receipt_url'],response.json['order']['receipt_url'])
        with self.factory() as db:
            self.assertEqual(db.get(PaymentAttempt,attempt['id']).payer_number_masked,'09•••••6543')
            self.assertEqual(sum(e.new_status=='Paid' for e in db.get(OrderPayment,order['id']).events),1)


if __name__=='__main__':unittest.main()
