"""Module: tests.test_security.

Purpose: Regression checks for separate portals, authorization, sessions and one admin.
Main components: SecurityTests, create_test_app.
Related: app.py, auth routes, User index, migrations and shared theme tokens.
Debugging: Runs on disposable SQLite only; never changes configured account records.
"""
import json
import re
import secrets
import tempfile
import unittest
from pathlib import Path

from flask import Flask
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import app as main_app
from audia.database import db, init_database, initialize
from audia.database.models import LoginSession, Order, User
from audia.database.migrations import upgrade_database
from audia.routes.auth import install_security

ROOT = Path(__file__).resolve().parent.parent


def create_test_app(directory):
    """Reuse production views on an isolated database and private temporary instance."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    app = Flask('app', root_path=main_app.root_path, static_folder=main_app.static_folder,
                static_url_path='/static', template_folder=main_app.template_folder,
                instance_path=str(Path(directory) / 'instance'))
    app.config.update(main_app.config)
    app.config.update(TESTING=True, SECRET_KEY=secrets.token_hex(32),
                      DATABASE_URL=f'sqlite:///{Path(directory) / "security.db"}', MAIL_BACKEND='memory')
    init_database(app)
    for blueprint in main_app.blueprints.values():
        app.register_blueprint(blueprint)
    install_security(app)
    for rule in main_app.url_map.iter_rules():
        if rule.endpoint not in app.view_functions:
            app.add_url_rule(rule.rule, endpoint=rule.endpoint,
                             view_func=main_app.view_functions[rule.endpoint], methods=rule.methods)
    for handlers in main_app.error_handler_spec.get(None, {}).values():
        for exception, handler in handlers.items():
            app.register_error_handler(exception, handler)
    app.cli.commands.update(main_app.cli.commands)
    initialize(app)
    return app


class SecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Random test credentials are not production defaults or a bypass.
        cls.password = secrets.token_urlsafe(24)
        cls.password_hash = generate_password_hash(cls.password)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='audia-security-')
        self.app = create_test_app(self.directory.name)
        with self.app.app_context():
            db().add_all([
                User(name='Test Administrator', email='admin@example.test', role='admin', password_hash=self.password_hash),
                User(name='Test Customer', email='customer@example.test', role='customer', password_hash=self.password_hash),
            ])
            db().commit()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.extensions['engine'].dispose()
        self.directory.cleanup()

    def send(self, url, data, method='POST', client=None):
        client = client or self.client
        token = client.get('/api/auth/session').json['csrf_token']
        return client.open(url, method=method, json=data, headers={'X-CSRF-Token': token})

    def login(self, portal='customer', account=None, client=None, **overrides):
        account = account or portal
        data = dict(email=f'{account}@example.test', password=self.password, role=portal)
        data.update(overrides)
        return self.send('/api/auth/admin/login' if portal == 'admin' else '/api/auth/login', data, client=client)

    def user_snapshot(self):
        with self.app.app_context():
            return [dict(row) for row in db().execute(select(User.__table__).order_by(User.id)).mappings()]

    def test_both_cross_role_logins_rejected_with_same_generic_error(self):
        for portal, account in [('customer', 'admin'), ('admin', 'customer')]:
            response = self.login(portal, account)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, {'error': 'Incorrect email or password.'})
            self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        with self.app.app_context():
            self.assertEqual(db().query(LoginSession).count(), 0)

    def test_correct_portals_and_server_side_redirects(self):
        for role, landing in [('customer', '/shop'), ('admin', '/admin')]:
            client = self.app.test_client()
            response = self.login(role, client=client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['user']['role'], role)
            self.assertNotIn('password_hash', response.json['user'])
            for url in ('/login', '/admin/login', '/register'):
                self.assertEqual(client.get(url).location, landing)
            self.assertEqual(client.get(landing).status_code, 200)

    def test_manipulated_login_role_never_selects_privileges(self):
        for role in ['admin', 'ADMIN', '', None, ['admin'], {'role': 'admin'}]:
            self.assertEqual(self.login('customer', role=role).status_code, 401)
        self.assertEqual(self.login('admin', role='customer').status_code, 401)
        self.assertEqual(self.login('admin', account='customer', role='admin').status_code, 401)

    def test_login_without_role_still_uses_fixed_endpoint(self):
        for portal in ('customer', 'admin'):
            url = '/api/auth/admin/login' if portal == 'admin' else '/api/auth/login'
            client = self.app.test_client()
            response = self.send(url, dict(email=f'{portal}@example.test', password=self.password), client=client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['user']['role'], portal)

    def test_every_admin_endpoint_denies_guests_and_customers_before_csrf(self):
        self.assertEqual(self.login().status_code, 200)
        guest = self.app.test_client()
        for rule in self.app.url_map.iter_rules():
            if not rule.rule.startswith('/api/admin/'):
                continue
            url = rule.rule.replace('<int:product_id>', '99999').replace('<order_id>', 'MISSING')
            for method in rule.methods - {'HEAD', 'OPTIONS'}:
                with self.subTest(url=url, method=method):
                    self.assertEqual(guest.open(url, method=method, json={}).status_code, 401)
                    self.assertEqual(self.client.open(url, method=method, json={}).status_code, 403)

    def test_direct_browser_urls_and_customer_only_workspaces(self):
        for url in ('/shop', '/orders', '/account'):
            self.assertEqual(self.client.get(url).location, '/login')
        self.assertEqual(self.client.get('/admin').location, '/admin/login')
        self.login()
        denied = self.client.get('/admin')
        self.assertEqual(denied.status_code, 403)
        self.assertIn(b'Access denied', denied.data)
        self.assertNotIn(b'data-page="dashboard"', denied.data)
        self.login('admin')
        for url in ('/shop', '/orders'):
            self.assertEqual(self.client.get(url).status_code, 403)
        for url in ('/api/orders', '/api/account/saved'):
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post('/api/orders', json={}).status_code, 403)
        self.assertEqual(self.client.get('/account').status_code, 200)

    def test_headers_query_and_body_cannot_override_database_role(self):
        self.login()
        headers = {'X-Role': 'admin', 'X-User-Role': 'admin'}
        self.assertEqual(self.client.get('/admin?role=admin', headers=headers).status_code, 403)
        self.assertEqual(self.client.get('/api/admin/sales?role=admin', headers=headers).status_code, 403)
        headers['X-CSRF-Token'] = self.client.get('/api/auth/session').json['csrf_token']
        response = self.client.patch('/api/admin/sales/MISSING', json=dict(role='admin', status='Delivered'), headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_public_registration_rejects_role_escalation_without_changes(self):
        before = self.user_snapshot()
        attempts = [{'role': 'admin'}, {'role': 'Admin'}, {'role': ['admin']},
                    {'is_admin': True}, {'roles': ['admin']}, {'permissions': ['admin']}]
        for attempt in attempts:
            response = self.send('/api/auth/register', dict(name='Forged User', email='forged@example.test', password=self.password, **attempt))
            self.assertEqual(response.status_code, 403)
        self.assertEqual(before, self.user_snapshot())

    def test_customer_registration_and_profile_password_still_work(self):
        response = self.send('/api/auth/register', dict(name='New Player', email='new@example.test', password=self.password, role='customer'))
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        with self.app.app_context():
            user = db().scalar(select(User).where(User.email == 'new@example.test'))
            self.assertEqual(user.role, 'customer')
            self.assertTrue(check_password_hash(user.password_hash, self.password))
        self.login()
        self.assertEqual(self.send('/api/auth/profile', dict(name='Updated Customer', address='123 Guitar Street', phone='09171234567'), 'PATCH').status_code, 200)
        response = self.send('/api/auth/password', dict(current_password=self.password, password=self.password + 'x'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/shop').status_code, 200)

    def test_profile_and_password_role_injection_rejected(self):
        self.login()
        before = self.user_snapshot()
        self.assertEqual(self.send('/api/auth/profile', dict(name='Escalated', role='admin'), 'PATCH').status_code, 403)
        self.assertEqual(self.send('/api/auth/password', dict(current_password=self.password, password=self.password+'x', role='admin')).status_code, 403)
        self.assertEqual(before, self.user_snapshot())

    def test_database_blocks_second_admin_and_role_promotion(self):
        before = self.user_snapshot()
        with self.app.app_context():
            db().add(User(name='Second Admin', email='second@example.test', role='admin', password_hash=self.password_hash))
            with self.assertRaises(IntegrityError):
                db().commit()
            db().rollback()
            user = db().scalar(select(User).where(User.role == 'customer'))
            user.role = 'admin'
            with self.assertRaises(IntegrityError):
                db().commit()
            db().rollback()
        self.assertEqual(before, self.user_snapshot())

    def test_cli_blocks_second_admin_and_preserves_existing_hash(self):
        before = self.user_snapshot()
        result = self.app.test_cli_runner().invoke(args=['create-admin', '--email', 'second@example.test', '--name', 'Second', '--password', self.password])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('administrator already exists', result.output)
        self.assertEqual(before, self.user_snapshot())

    def test_migration_preserves_rows_and_handles_legacy_duplicate_admins(self):
        index = next(index for index in User.__table__.indexes if index.name == 'uq_users_single_admin')
        index.drop(self.app.extensions['engine'])
        before = self.user_snapshot()
        backup = upgrade_database(self.app)
        self.assertTrue(backup.is_file())
        self.assertEqual(before, self.user_snapshot())
        self.assertTrue(any(item['name'] == index.name and item['unique'] for item in inspect(self.app.extensions['engine']).get_indexes('users')))
        self.assertIsNone(upgrade_database(self.app))
        index.drop(self.app.extensions['engine'])
        with self.app.app_context():
            db().add(User(name='Legacy Duplicate', email='duplicate@example.test', role='admin', password_hash=self.password_hash))
            db().commit()
        duplicates = self.user_snapshot()
        with self.assertRaisesRegex(RuntimeError, 'Multiple administrators'):
            upgrade_database(self.app)
        self.assertEqual(duplicates, self.user_snapshot())

    def test_no_automatic_admin_creation(self):
        with self.app.app_context():
            user = db().scalar(select(User).where(User.role == 'admin'))
            db().delete(user)
            db().commit()
        self.assertIsNone(upgrade_database(self.app))
        self.assertEqual(self.client.get('/admin/login').status_code, 200)
        self.assertTrue(all(user['role'] == 'customer' for user in self.user_snapshot()))

    def test_logout_replay_repeated_login_and_no_stale_cookie_refresh(self):
        for role in ('customer', 'admin'):
            client = self.app.test_client()
            destination = '/admin' if role == 'admin' else '/shop'
            for _ in range(3):
                response = self.login(role, client=client, remember=True)
                self.assertEqual(response.status_code, 200)
                cookie = client.get_cookie('session').value
                self.assertNotIn('Set-Cookie', client.get('/api/auth/session').headers)
                self.assertEqual(self.send('/api/auth/logout', {}, client=client).status_code, 200)
                self.assertEqual(client.get(destination).status_code, 302)
                replay = self.app.test_client(); replay.set_cookie('session', cookie)
                self.assertIsNone(replay.get('/api/auth/session').json['user'])
                self.assertEqual(self.login(role, client=client, password='incorrect').status_code, 401)

    def test_session_fixation_role_binding_and_legacy_sessions(self):
        initial = self.client.get('/api/auth/session').json['csrf_token']
        response = self.login()
        self.assertNotEqual(response.json['csrf_token'], initial)
        with self.client.session_transaction() as session:
            self.assertEqual(session['auth_role'], 'customer')
            session['auth_role'] = 'admin'
        self.assertEqual(self.client.get('/api/orders').status_code, 401)
        self.login()
        with self.client.session_transaction() as session:
            session.pop('auth_role')
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])
        self.assertEqual(self.client.get('/shop').status_code, 302)

    def test_database_role_change_invalidates_old_session(self):
        self.login()
        with self.app.app_context():
            user = db().scalar(select(User).where(User.role == 'customer'))
            user.role = 'disabled-external'
            db().commit()
        self.assertEqual(self.client.get('/api/orders').status_code, 401)
        self.assertIsNone(self.client.get('/api/auth/session').json['user'])

    def test_expiration_uses_actual_instant_for_utc_and_non_utc_datetimes(self):
        from datetime import datetime, timedelta, timezone
        from audia.routes.auth.auth import expired
        current = datetime.now(timezone.utc)
        manila = timezone(timedelta(hours=8))
        self.assertTrue(expired((current-timedelta(minutes=1)).astimezone(manila)))
        self.assertFalse(expired((current+timedelta(minutes=1)).astimezone(manila)))
        self.assertTrue(expired((current-timedelta(minutes=1)).replace(tzinfo=None)))

    def test_csrf_cache_cookie_and_explicit_remember_rules(self):
        self.assertEqual(self.client.post('/api/auth/login', json={}).status_code, 403)
        response = self.login(remember='true')
        self.assertEqual(response.status_code, 200)
        cookie = response.headers.get('Set-Cookie', '')
        self.assertIn('HttpOnly', cookie); self.assertIn('SameSite=Lax', cookie)
        self.assertNotIn('Expires=', cookie)
        self.assertEqual(self.client.patch('/api/auth/profile', json={}).status_code, 403)
        page = self.client.get('/shop')
        self.assertEqual(page.headers['Cache-Control'], 'no-store')
        self.assertEqual(page.headers['Pragma'], 'no-cache')
        self.assertEqual(page.headers['Expires'], '0')
        secure_directory = Path(self.directory.name) / 'secure-cookie'
        self.assertEqual(secure_directory.resolve().parent, Path(self.directory.name).resolve())
        secure = create_test_app(str(secure_directory))
        secure.config['SESSION_COOKIE_SECURE'] = True
        try:
            self.assertIn('Secure', secure.test_client().get('/api/auth/session').headers['Set-Cookie'])
        finally:
            secure.extensions['engine'].dispose()

    def test_separate_portal_markup_admin_profile_and_shared_practice(self):
        customer = self.client.get('/login').get_data(as_text=True)
        admin = self.client.get('/admin/login').get_data(as_text=True)
        self.assertIn('Customer sign in', customer)
        self.assertIn('Administrator sign in', admin)
        self.assertIn('data-auth-mode="admin"', admin)
        self.assertIn('href="/admin/login"', customer)
        self.assertEqual(self.client.get('/login?role=admin').location, '/admin/login')
        self.login('admin')
        page = self.client.get('/account').get_data(as_text=True)
        self.assertNotIn('data-field="orders"', page)
        self.assertIn('data-form="profile"', page)
        for url in ('/tuner', '/lessons'):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_order_ownership_and_admin_inspection_still_work(self):
        self.login()
        response = self.send('/api/orders', dict(request_key=secrets.token_urlsafe(24), address='123 Guitar Street', phone='09171234567', payment_method='cod', items=[dict(product_id=1, quantity=1)]))
        self.assertEqual(response.status_code, 201)
        order = response.json['order']
        self.assertEqual(order['payment_status'], 'Pending')
        self.assertEqual(self.client.get('/api/orders/'+order['id']).status_code, 200)
        self.assertEqual(self.send('/api/admin/sales/'+order['id'], dict(status='Delivered'), 'PATCH').status_code, 403)
        self.login('admin')
        self.assertEqual(self.client.get('/api/orders/'+order['id']).status_code, 200)
        with self.app.app_context():
            self.assertEqual(db().get(Order, order['id']).status, 'Pending')

    def test_password_recovery_directs_to_correct_portal_without_auto_login(self):
        for role in ('admin', 'customer'):
            self.assertEqual(self.send('/api/auth/forgot-password', dict(email=f'{role}@example.test')).status_code, 200)
            message = self.app.extensions['outbox'][-1].get_content()
            token = re.search(r'/reset-password\?token=([^\s]+)', message)[1]
            response = self.send('/api/auth/reset-password', dict(token=token, password=self.password+'new'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['login_role'], role)
            self.assertIsNone(self.client.get('/api/auth/session').json['user'])

    def test_theme_semantic_text_contrast(self):
        css = (ROOT/'assets/css/shared/theme.css').read_text(encoding='utf-8')
        def variables(selector):
            body = re.search(re.escape(selector)+r'\s*\{([^}]+)\}', css)[1]
            return dict(re.findall(r'(--[\w-]+):\s*([^;]+);', body))
        light = variables(':root'); dark = dict(light, **variables('html.dark'))
        def resolve(values, name):
            value = values[name]
            return resolve(values, value[4:-1]) if value.startswith('var(') else value
        def luminance(color):
            rgb = [int(color[index:index+2], 16)/255 for index in (1,3,5)]
            linear = [value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4 for value in rgb]
            return sum(value*weight for value,weight in zip(linear,[.2126,.7152,.0722]))
        pairs = [('on-primary','primary'),('text','surface'),('muted','surface'),('success','success-bg'),('warning','warning-bg'),('error','error-bg'),('info','info-bg')]
        for name,values in [('light',light),('dark',dark)]:
            for foreground,background in pairs:
                levels=sorted([luminance(resolve(values,'--'+foreground)),luminance(resolve(values,'--'+background))])
                self.assertGreaterEqual((levels[1]+.05)/(levels[0]+.05), 4.5, (name,foreground,background))


if __name__ == '__main__':
    unittest.main()
