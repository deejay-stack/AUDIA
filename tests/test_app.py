"""Integration checks use a disposable SQLite database, never the configured PostgreSQL server."""
import re
import tempfile
import unittest
from pathlib import Path
from sqlalchemy import URL, select
from werkzeug.security import generate_password_hash
from app import create_app
from modules.database import db, initialize
from modules.models import User, Product, LoginSession


class AudiaTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test-key','DATABASE_URL':f'sqlite:///{Path(self.directory.name)/"test.db"}', 'MAIL_BACKEND':'memory'})
        initialize(self.app)
        self.client=self.app.test_client()
        self.csrf=self.client.get('/api/auth/session').json['csrf_token']

    def tearDown(self):
        self.app.extensions['engine'].dispose()
        self.directory.cleanup()

    def send(self,path,data=None,method='POST',client=None,csrf=None):
        response=(client or self.client).open('/api'+path,method=method,json=data,
                    headers={'X-CSRF-Token':csrf or self.csrf})
        if client is None and response.is_json and response.json.get('csrf_token'):
            self.csrf=response.json['csrf_token']
        return response

    def register(self,email='player@example.com',name='Test Player'):
        result=self.send('/auth/register',dict(name=name,email=email,password='correct-horse-123'))
        self.assertEqual(result.status_code,200,result.json)
        return result.json['user']

    def admin(self):
        with self.app.app_context():
            user=db().scalar(select(User).where(User.email=='admin@example.com'))
            if not user:
                db().add(User(name='Store Admin',email='admin@example.com',password_hash=generate_password_hash('admin-password-123'),role='admin'))
                db().commit()
        response=self.send('/auth/login',dict(email='admin@example.com',password='admin-password-123',role='admin'))
        self.assertEqual(response.status_code,200,response.json)

    def order(self,quantity=1,key='unique-request-key-12345'):
        return self.send('/orders',dict(items=[dict(product_id=1,quantity=quantity)],address='123 Guitar Street, Quezon City',phone='09171234567',request_key=key))

    def test_assets_and_template_registry(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        for name in ('landing','account','auth','checkout','product-form','settings','notifications'):
            self.assertIn(f'id="{name}-template"'.encode(),response.data)
        self.assertNotRegex(response.get_data(as_text=True),r'<style\b|\sstyle=')
        for asset in Path(self.app.static_folder).rglob('*'):
            if asset.is_file():
                with self.client.get('/static/'+asset.relative_to(self.app.static_folder).as_posix()) as result:
                    self.assertEqual(result.status_code,200,str(asset))

    def test_unconfigured_landing_has_no_catalog_or_fake_authentication(self):
        preview=create_app({'TESTING':True,'SECRET_KEY':'preview','DATABASE_URL':''}).test_client()
        self.assertEqual(preview.get('/').status_code,200)
        self.assertEqual(preview.get('/api/products').status_code,401)
        self.assertEqual(preview.get('/api/health').status_code,503)
        token=preview.get('/api/auth/session').json['csrf_token']
        response=self.send('/auth/login',dict(email='admin@audia.ph',password='admin123'),client=preview,csrf=token)
        self.assertEqual(response.status_code,503)
        self.assertIsNone(preview.get('/api/auth/session').json['user'])

    def test_registration_password_hash_role_and_duplicate(self):
        response=self.send('/auth/register',dict(name='New Player',email='PLAYER@EXAMPLE.COM',password='correct-horse-123',role='admin'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['user']['role'],'customer')
        self.assertEqual(response.json['user']['email'],'player@example.com')
        with self.app.app_context():
            user=db().get(User,response.json['user']['id'])
            self.assertNotEqual(user.password_hash,'correct-horse-123')
            self.assertTrue(user.password_hash.startswith('scrypt:'))
        self.assertEqual(self.send('/auth/register',dict(name='Other',email='player@example.com',password='correct-horse-123')).status_code,409)

    def test_login_rejects_demo_wrong_password_and_role_escalation(self):
        self.register()
        self.send('/auth/logout')
        for email,password,role in [('player@example.com','wrong','customer'),('admin@audia.ph','admin123','admin'),('player@example.com','correct-horse-123','admin')]:
            self.assertEqual(self.send('/auth/login',dict(email=email,password=password,role=role)).status_code,401)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        good=self.send('/auth/login',dict(email='PLAYER@example.com',password='correct-horse-123',remember=True))
        self.assertEqual(good.status_code,200)
        cookie=good.headers.get('Set-Cookie','')
        self.assertIn('HttpOnly',cookie);self.assertIn('SameSite=Lax',cookie);self.assertIn('Expires=',cookie)

    def test_csrf_admin_and_order_access(self):
        self.assertEqual(self.client.post('/api/auth/login',json={}).status_code,403)
        for path in ['/api/admin/sales','/api/admin/products','/api/admin/customers','/api/admin/summary','/api/admin/settings','/api/admin/sales/export']:
            self.assertEqual(self.client.get(path).status_code,401,path)
        self.register()
        self.assertEqual(self.client.get('/api/admin/sales').status_code,403)
        self.assertEqual(self.send('/admin/products',{},method='POST').status_code,403)

    def test_logout_invalidates_replayed_cookie(self):
        self.register()
        old_cookie=self.client.get_cookie('session').value
        self.send('/auth/logout')
        self.client.set_cookie('session',old_cookie)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])

    def test_reset_single_use_and_session_revocation(self):
        self.register()
        old_cookie=self.client.get_cookie('session').value
        response=self.send('/auth/forgot-password',dict(email='player@example.com'))
        self.assertEqual(response.status_code,200)
        message=self.app.extensions['outbox'][-1].get_content()
        token=re.search(r'/#reset/([^\s]+)',message)[1]
        self.assertNotIn(token,str(response.json))
        self.assertEqual(self.send('/auth/reset-password',dict(token=token,password='new-password-123')).status_code,200)
        self.assertEqual(self.send('/auth/reset-password',dict(token=token,password='other-password-123')).status_code,400)
        other=self.app.test_client();other.set_cookie('session',old_cookie)
        self.assertIsNone(other.get('/api/auth/session').json['user'])
        self.assertEqual(self.send('/auth/login',dict(email='player@example.com',password='correct-horse-123')).status_code,401)
        self.assertEqual(self.send('/auth/login',dict(email='player@example.com',password='new-password-123')).status_code,200)

    def test_password_change_profile_and_rate_limit(self):
        self.register()
        self.assertEqual(self.send('/auth/password',dict(current_password='wrong',password='new-password-123')).status_code,400)
        self.assertEqual(self.send('/auth/password',dict(current_password='correct-horse-123',password='new-password-123')).status_code,200)
        updated=self.send('/auth/profile',dict(name='Updated Player',phone='09171234567',address='Guitar Street'),method='PATCH')
        self.assertEqual(updated.json['user']['name'],'Updated Player')
        for _ in range(9):
            response=self.send('/auth/login',dict(email='none@example.com',password='incorrect'))
        self.assertEqual(response.status_code,429)

    def test_catalog_finder_and_wishlist(self):
        self.register()
        self.assertEqual(self.client.get('/api/products?category=acoustic&q=ACOUSTIC_001').json['count'],1)
        self.assertEqual(self.client.get('/api/products/999').status_code,404)
        profile=dict(budget=20000,category='Electric',level='Beginner',genre='Rock')
        result=self.send('/finder',profile)
        self.assertEqual(result.json['recommendations'][0]['name'],'ELECTRIC_010')
        self.assertEqual(self.send('/finder',dict(profile,budget='bad')).status_code,400)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,200)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,200)
        data=self.client.get('/api/account/saved').json
        self.assertEqual(len(data['products']),1);self.assertEqual(data['profile'],profile)
        self.send('/account/saved/1',method='DELETE')
        self.assertEqual(self.client.get('/api/account/saved').json['products'],[])

    def test_checkout_server_prices_stock_idempotency_and_ownership(self):
        self.register()
        first=self.order(2);self.assertEqual(first.status_code,201,first.json)
        self.assertEqual(first.json['order']['amount'],25980)
        self.assertEqual(self.order(2).json['order']['id'],first.json['order']['id'])
        self.assertEqual(self.client.get('/api/products/1').json['stock'],6)
        self.assertEqual(self.order(99,'other-request-key-12345').status_code,400)
        self.assertEqual(self.client.get('/api/products/1').json['stock'],6)
        self.assertEqual(len(self.client.get('/api/orders').json['orders']),1)
        self.register('another@example.com')
        self.assertEqual(self.client.get('/api/orders/'+first.json['order']['id']).status_code,404)

    def test_invalid_checkout_rolls_back_all_items(self):
        self.register()
        response=self.send('/orders',dict(request_key='rollback-request-key-123',address='123 Guitar Street',phone='09171234567',
                           items=[dict(product_id=1,quantity=1),dict(product_id=2,quantity=99)]))
        self.assertEqual(response.status_code,400)
        self.assertEqual(self.client.get('/api/products/1').json['stock'],8)
        self.assertEqual(self.client.get('/api/orders').json['orders'],[])

    def test_admin_inventory_orders_reporting_export_settings(self):
        self.register(name='=FORMULA')
        order=self.order().json['order']
        self.admin()
        base=self.client.get('/api/products/1').json
        data=dict(base,name='Test instrument',stock=3,price=12345.67)
        created=self.send('/admin/products',data)
        self.assertEqual(created.status_code,201,created.json)
        product_id=created.json['product']['id']
        self.assertEqual(self.send(f'/admin/products/{product_id}',dict(data,stock=5),method='PUT').json['product']['stock'],5)
        self.assertEqual(self.send(f'/admin/products/{product_id}',method='DELETE').status_code,200)
        self.assertEqual(self.client.get(f'/api/products/{product_id}').status_code,404)
        for status in ['Processing','Shipped','Delivered']:
            self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status=status),method='PATCH').status_code,200)
        summary=self.client.get('/api/admin/summary').json
        self.assertEqual(summary['gross_revenue'],12990)
        self.assertEqual(summary['categories']['Electric'],12990)
        self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status='Pending'),method='PATCH').status_code,400)
        self.assertEqual(self.send('/admin/sales/'+order['id'],dict(status='Refunded'),method='PATCH').status_code,200)
        self.send('/admin/sales/'+order['id'],dict(status='Refunded'),method='PATCH')
        self.assertEqual(self.client.get('/api/products/1').json['stock'],8)
        exported=self.client.get('/api/admin/sales/export').get_data(as_text=True)
        self.assertIn("'=FORMULA",exported)
        settings=self.send('/admin/settings',dict(store_name='AUDIA Studio',support_email='studio@example.com'),method='PUT')
        self.assertEqual(settings.json['settings']['store_name'],'AUDIA Studio')
        self.assertEqual(len(self.client.get('/api/admin/customers').json['customers']),1)

    def test_malformed_requests_and_validation(self):
        self.assertEqual(self.send('/auth/register',[]).status_code,400)
        self.assertEqual(self.send('/auth/register',dict(name='Player',email='bad',password='short')).status_code,400)
        self.admin()
        data=self.client.get('/api/products/1').json
        for changes in [dict(price='NaN'),dict(stock=-1),dict(image='javascript:alert(1)'),dict(category='Unknown')]:
            self.assertEqual(self.send('/admin/products',dict(data,**changes)).status_code,400)

    def test_uploaded_catalog_codes_categories_and_files(self):
        self.register()
        products=self.client.get('/api/products').json['products']
        guitars=[p for p in products if p['category'] in ('Electric','Acoustic','Bass','Classical')]
        self.assertEqual(len(guitars),40)
        self.assertEqual(len({p['image'] for p in guitars}),40)
        for category in ('Electric','Acoustic','Bass','Classical'):
            group=[p for p in guitars if p['category']==category]
            self.assertEqual([p['name'] for p in group],[f'{category.upper()}_{i:03d}' for i in range(1,11)])
            for product in group:
                self.assertTrue(product['image'].startswith(f'/static/images/{category.lower()}/'))
                self.assertIsInstance(product['id'],int)
                self.assertGreater(product['stock'],0)
                self.assertGreater(product['price'],0)
                self.assertTrue(product['description'])
                self.assertTrue(product['specs'])
                self.assertEqual(product['reviews'],0)
        self.assertIn('images/guitar_performance.jpg',self.client.get('/').get_data(as_text=True))

    def test_initialization_preserves_inventory_and_does_not_duplicate_catalog(self):
        self.register()
        with self.app.app_context():
            product=db().get(Product,1)
            product.stock=2
            product.price=5432
            db().commit()
        initialize(self.app)
        response=self.client.get('/api/products').json
        self.assertEqual(response['count'],42)
        first=next(p for p in response['products'] if p['id']==1)
        self.assertEqual((first['stock'],first['price']),(2,5432))

    def test_local_and_https_inventory_images(self):
        self.admin()
        product=self.client.get('/api/products/1').json
        for path in ('/static/images/electric/Amber_Flame.png','https://example.com/guitar.png'):
            result=self.send('/admin/products/1',dict(product,image=path),method='PUT')
            self.assertEqual(result.status_code,200,result.json)
            self.assertEqual(result.json['product']['image'],path)
        for path in ('/static/images/missing.png','/static/images/../../.env',
                     '/static/images/../icons/play.svg','//example.com/guitar.png',
                     'data:image/svg+xml,<svg/>','/static/images/%2e%2e/.env'):
            self.assertEqual(self.send('/admin/products/1',dict(product,image=path),method='PUT').status_code,400,path)

    def test_sqlalchemy_url_object_configuration(self):
        app=create_app({'TESTING':True,'SECRET_KEY':'url-test',
                        'DATABASE_URL':URL.create('sqlite',database=':memory:')})
        try:
            initialize(app)
            self.assertEqual(app.test_client().get('/api/products').status_code,401)
            with app.app_context():
                self.assertEqual(db().query(Product).count(),42)
        finally:
            app.extensions['engine'].dispose()

    def test_guests_cannot_read_catalog_find_products_or_checkout(self):
        for path in ('/api/products','/api/products?category=Electric','/api/products/1',
                     '/api/account/saved','/api/orders'):
            response=self.client.get(path)
            self.assertEqual(response.status_code,401,path)
            self.assertNotIn('products',response.json)
        self.assertEqual(self.send('/finder',dict(budget=20000,category='Electric',level='Beginner')).status_code,401)
        self.assertEqual(self.order().status_code,401)
        self.assertEqual(self.send('/account/saved/1',method='PUT').status_code,401)
        self.register()
        self.assertEqual(self.client.get('/api/products').json['count'],42)
        self.send('/auth/logout')
        self.assertEqual(self.client.get('/api/products').status_code,401)
        self.assertEqual(self.client.get('/api/products/1').status_code,401)

    def test_expired_session_cannot_read_products(self):
        from datetime import timedelta
        from modules.models import now
        self.register()
        with self.app.app_context():
            for login in db().scalars(select(LoginSession)):
                login.expires_at=now()-timedelta(seconds=1)
            db().commit()
        self.assertEqual(self.client.get('/api/products').status_code,401)


if __name__=='__main__':
    unittest.main()
