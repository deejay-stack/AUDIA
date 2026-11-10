"""Exercise the new customer-to-admin workflows in Edge on isolated data."""
import json
import logging
import sys
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_operations import OperationsTests
from test_commerce import app
from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server


def run():
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    OperationsTests.setUpClass();fixture=OperationsTests();fixture.setUp()
    output=Path('test-results/operations');output.mkdir(parents=True,exist_ok=True)
    delivered=fixture.deliver(fixture.paid_order());cancel=fixture.paid_order()
    fixture.configure(bank_mode='manual')
    bank=fixture.checkout('bpi').json['order'];fixture.confirm(bank,fixture.start(bank).json['attempt'])
    server=make_server('127.0.0.1',5098,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    class Forwarder(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def forward(self):
            connection=HTTPConnection('127.0.0.1',5098,timeout=20)
            body=self.rfile.read(int(self.headers.get('Content-Length',0)))
            connection.request(self.command,self.path,body=body,headers=dict(self.headers))
            response=connection.getresponse();data=response.read();self.send_response(response.status)
            for key,value in response.getheaders():
                if key.lower() not in ('connection','transfer-encoding','content-length','server','date'):self.send_header(key,value)
            self.send_header('Content-Length',str(len(data)));self.end_headers()
            try:self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass  # Browser navigation cancels in-flight assets.
            finally:connection.close()
        do_GET=do_POST=do_PUT=do_PATCH=do_DELETE=forward
    forward=ThreadingHTTPServer(('127.0.0.1',5099),Forwarder);forward_thread=threading.Thread(target=forward.serve_forever,daemon=True);forward_thread.start()
    results=[];errors=[]
    def passed(s):results.append(s);print('PASS:',s,flush=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
            customer=browser.new_context(viewport={'width':1440,'height':1000});admin=browser.new_context(viewport={'width':1440,'height':1000})
            page=customer.new_page();staff=admin.new_page()
            for view in [page,staff]:
                view.on('pageerror',lambda e:errors.append(str(e)))
                view.route('https://tile.openstreetmap.org/**',lambda route:route.abort())
            def login(view,is_admin=False,origin='http://127.0.0.1:5098'):
                view.goto(origin+('/admin/login' if is_admin else '/login'));expect(view.locator('#root')).not_to_have_attribute('inert','')
                view.locator('[data-field=email]').fill('admin@example.test' if is_admin else 'one@example.test')
                view.locator('[data-field=password]').fill(fixture.password);view.locator('[data-field=login-submit]').click()
                view.wait_for_url('**/admin' if is_admin else '**/shop')
            login(page);page.goto('http://127.0.0.1:5098/orders')
            page.locator(f'[data-order-id="{delivered["id"]}"] [data-action=view-order]').click()
            expect(page.locator('dialog [data-field=request-refund]')).to_be_visible()
            page.locator('dialog [data-field=request-refund]').click();form=page.locator('[data-form=customer-request]')
            form.locator('[data-item-id]').first.fill('1');form.locator('[name=explanation]').fill('Damaged item for school test')
            form.locator('[type=submit]').click();expect(form).to_have_count(0)
            expect(page.locator('[data-field=request-history]')).to_contain_text('Requested')
            page.screenshot(path=str(output/'customer-request.png'),full_page=True)
            page.locator('dialog [data-action=dialog-close]').click();passed('Customer submits an item/quantity refund request and sees stored history')
            login(staff,True);staff.goto('http://127.0.0.1:5098/admin/refunds')
            expect(staff.locator('[data-field=operations-rows]')).to_contain_text('Requested');staff.reload()
            expect(staff.locator('[data-field=admin-title]')).to_have_text('Returns & Refunds')
            def review(status,amount=None,restock=False):
                staff.locator('[data-field=operations-rows] button').first.click();f=staff.locator('[data-form=review-request]')
                f.locator('[name=status]').select_option(status)
                if amount:f.locator('[name=amount]').fill(amount)
                f.locator('[name=note]').fill('School return inspected and reviewed')
                if restock:f.locator('[name=restock]').check()
                f.locator('[type=submit]').click();expect(f).to_have_count(0)
                expect(staff.locator('[data-field=operations-rows]')).to_contain_text('Partially Refunded' if status=='Refunded' else status)
            review('Under Review');review('Approved','80.00');review('Awaiting Return');review('Item Received');review('Refund Processing',restock=True);review('Refunded')
            staff.screenshot(path=str(output/'refunds-desktop.png'),full_page=True)
            staff.locator('[data-field=operations-rows] button').first.click()
            with staff.expect_popup() as popup:staff.locator('[data-field=review-confirmation]').click()
            confirmation=popup.value;expect(confirmation.locator('body')).to_contain_text('80.00');confirmation.close();staff.locator('dialog [data-action=dialog-close]').click()
            passed('Admin review, inspected restock, partial refund, confirmation and refreshable deep link')
            staff.goto('http://127.0.0.1:5098/admin/transactions')
            staff.locator('form[data-form=ledger] [name=status]').select_option('Pending Verification');staff.locator('form[data-form=ledger] [type=submit]').click()
            expect(staff.locator('[data-field=ledger-rows] tr')).to_have_count(1);staff.locator('[data-field=ledger-rows] button').click()
            verify=staff.locator('dialog form').filter(has=staff.get_by_role('heading',name='Verify simulated bank authorization'))
            verify.locator('input').fill('Authorized by school store');verify.locator('[type=submit]').click()
            expect(staff.locator('dialog')).to_have_count(0);passed('Pending bank payment verified by administrator through payment ledger')
            staff.goto('http://127.0.0.1:5098/admin/delivery');staff.locator('[data-form=operations-filter] [name=q]').fill(cancel['id']);staff.locator('[data-form=operations-filter] [type=submit]').click()
            expect(staff.locator('[data-field=operations-rows] article')).to_have_count(1);staff.get_by_role('button',name='Manage delivery').click()
            f=staff.locator('[data-form=delivery-editor]');f.locator('[name=route]').fill('14.50, 121.00\n14.55, 121.04\n14.60, 121.10')
            f.locator('[name=progress]').fill('2');f.locator('[name=note]').fill('Simulated distribution waypoint');f.locator('[type=submit]').click();expect(f).to_have_count(0)
            fixture.configure(map_provider='google',google_maps_key='SCHOOL_TEST_KEY_1234567890')
            page.route('https://maps.googleapis.com/**',lambda route:route.abort())
            page.reload();page.locator(f'[data-order-id="{cancel["id"]}"] [data-action=view-order]').click()
            page.locator('[data-field=show-delivery-map]').click();expect(page.locator('.leaflet-container')).to_be_visible()
            expect(page.locator('[data-field=delivery-map-error]')).to_contain_text('tiles are unavailable')
            expect(page.locator('[data-field=delivery-map] img[src*="guitar"]')).to_have_count(0)
            page.locator('[data-field=delivery-map]').scroll_into_view_if_needed()
            page.screenshot(path=str(output/'tracking-map-fallback.png'),full_page=True)
            passed('Stored delivery route, map markers and usable route when external tiles fail')
            page.locator('[data-field=cancel-order]').click();f=page.locator('[data-form=customer-request]');f.locator('[type=submit]').click();expect(f).to_have_count(0)
            expect(page.locator('[data-field=request-history]')).to_contain_text('Cancellation');page.locator('dialog [data-action=dialog-close]').click()
            page.reload();expect(page.locator('[data-field=account-notifications]')).to_contain_text('Cancellation request')
            page.get_by_role('button',name='Mark read').click();expect(page.locator('[data-field=account-notifications] [data-read=false]')).to_have_count(0)
            passed('Paid cancellation request and persisted customer notifications')
            staff.goto('http://127.0.0.1:5098/admin/settings');expect(staff.locator('[name=bank_mode]')).to_have_value('manual')
            staff.locator('[name=shipping_fee]').fill('35.00');staff.locator('[data-form=settings] [type=submit]').click()
            expect(staff.locator('#notice')).to_contain_text('saved');staff.reload();expect(staff.locator('[name=shipping_fee]')).to_have_value('35.00')
            staff.set_viewport_size({'width':390,'height':844})
            staff.wait_for_function("document.querySelector('aside').getBoundingClientRect().right <= 1")
            staff.screenshot(path=str(output/'settings-mobile.png'),full_page=True)
            assert staff.evaluate('document.documentElement.scrollWidth <= innerWidth')
            passed('Backend settings save, persisted bank mode and mobile policy form')
            # A different browser origin exercises relative API requests/cookies without localhost pinning.
            alt=browser.new_context();view=alt.new_page();login(view,False,'http://localhost:5098');view.goto('http://localhost:5098/orders')
            expect(view.locator('[data-action=view-order]').first).to_be_visible();passed('Alternate-host same-origin API and session restoration')
            forwarded=browser.new_context();proxy=forwarded.new_page();login(proxy,False,'http://127.0.0.1:5099');proxy.goto('http://127.0.0.1:5099/orders');expect(proxy.locator('[data-action=view-order]').first).to_be_visible()
            proxy.reload();expect(proxy.locator('[data-action=view-order]').first).to_be_visible();passed('Forwarded port through local HTTP proxy preserves API origin, cookies and refresh')
            assert not errors,errors
            browser.close()
    finally:
        forward.shutdown();forward.server_close();forward_thread.join(timeout=10);server.shutdown();thread.join(timeout=10);fixture.tearDown()
        (output/'browser-results.json').write_text(json.dumps({'passed':results,'runtime_errors':errors},indent=2),encoding='utf-8')
    print(f'{len(results)} operations browser scenario groups passed.',flush=True)


if __name__=='__main__':run()
