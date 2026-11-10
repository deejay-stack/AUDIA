r"""Run browser workflows against an isolated SQLite test server, never the real DB.

Requires the optional Playwright development package and installed Microsoft Edge.
Run: .venv\Scripts\python.exe tests/browser_commerce.py
"""
import json
import logging
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_commerce import CommerceTests, app
from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server


def run():
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    CommerceTests.setUpClass()
    fixture = CommerceTests(); fixture.setUp()
    output=Path('test-results/commerce');output.mkdir(parents=True,exist_ok=True)
    server=make_server('127.0.0.1',5097,app)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    results=[]; errors=[]
    def passed(name):
        results.append(name);print('PASS:',name,flush=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
            context=browser.new_context(viewport={'width':1440,'height':1000})
            page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            def login(page, admin=False):
                page.goto('http://127.0.0.1:5097/admin/login' if admin else 'http://127.0.0.1:5097/login')
                expect(page.locator('#root')).not_to_have_attribute('inert','')
                page.locator('[data-field=email]').fill('admin@example.test' if admin else 'one@example.test')
                page.locator('[data-field=password]').fill(fixture.password)
                page.locator('[data-field=login-submit]').click()
                page.wait_for_url('**/admin' if admin else '**/shop')
            login(page)
            expect(page.locator('[data-field=products] [data-action=add]').first).to_be_enabled()
            page.locator('[data-field=products] [data-action=product-detail]').first.click()
            expect(page.locator('dialog')).to_be_visible();page.locator('dialog [data-action=dialog-close]').click()
            page.locator('[data-field=products] [data-action=add]').first.click()
            page.locator('[data-action=increase]').first.click()
            page.locator('[data-action=decrease]').first.click()
            page.locator('[data-action=checkout]').click()
            checkout=page.locator('form[data-form=checkout]')
            checkout.locator('[name=address]').fill('123 Test Street, Manila')
            checkout.locator('[name=phone]').fill('09171234567')
            checkout.locator('[name=payment_method][value=gcash]').check()
            expect(checkout.locator('[name=payment_method]:checked')).to_have_count(1)
            page.screenshot(path=str(output/'checkout-desktop.png'),full_page=True)
            checkout.locator('[type=submit]').click()
            payment=page.locator('form.demo-payment')
            expect(payment.locator('[type=submit]')).to_be_enabled()
            expect(payment.locator('[data-field=payment-success]')).to_be_hidden()
            payment.locator('[name=outcome]').select_option('failure')
            payment.locator('[type=submit]').click()
            expect(payment.locator('[data-field=payment-result]')).to_contain_text('failed')
            payment.locator('[data-field=cancel-payment]').click()
            expect(checkout.locator('[data-field=payment-preview]')).to_contain_text('saved and unpaid')
            passed('Customer checkout, payment selection, declined payment and preserved order')
            checkout.locator('[type=submit]').click()
            expect(payment.locator('[type=submit]')).to_be_enabled()
            payment.locator('[type=submit]').click()
            expect(payment.locator('[data-field=gcash-authorization]')).to_be_visible()
            expect(payment.locator('[data-field=payment-success]')).to_be_hidden()
            payment.locator('[name=gcash_number]').fill('09171234567')
            payment.locator('[type=submit]').click()
            expect(payment.locator('[data-field=payment-result]')).to_contain_text('confirmed')
            expect(payment.locator('[data-field=payment-success]')).to_be_visible()
            expect(payment.locator('[data-field=success-number]')).to_have_text('GCash number: 09•••••4567')
            expect(payment.locator('[data-field=form-error]')).to_be_hidden()
            expect(payment.locator('[data-field=success-qr]')).to_have_attribute('src',__import__('re').compile(r'/receipts/qr/RCT-'))
            page.wait_for_function("document.querySelector('[data-field=success-qr]').complete && document.querySelector('[data-field=success-qr]').naturalWidth > 0")
            payment.locator('[data-field=payment-success]').scroll_into_view_if_needed()
            payment.locator('[data-field=payment-success]').screenshot(path=str(output/'payment-success.png'))
            payment.locator('[data-field=cancel-payment]').click()
            expect(page.locator('dialog [data-field=payment_status]')).to_have_text('Paid')
            with page.expect_popup() as receipt_info:
                page.locator('dialog [data-field=receipt]').click()
            receipt=receipt_info.value;expect(receipt.locator('body')).to_contain_text('No real funds transferred')
            receipt.screenshot(path=str(output/'receipt.png'),full_page=True)
            receipt.pdf(path=str(output/'receipt.pdf'),format='A4',print_background=True)
            receipt.close();page.locator('dialog [data-action=dialog-close]').click()
            page.goto('http://127.0.0.1:5097/orders')
            expect(page.locator('[data-action=view-order]').first).to_be_visible()
            passed('Successful retry, persisted customer order history and printable receipt')
            admin_context=browser.new_context(viewport={'width':1440,'height':1000})
            admin_page=admin_context.new_page();admin_page.on('pageerror',lambda error:errors.append(str(error)))
            login(admin_page,True)
            expect(admin_page.locator('[data-field=gross_revenue]')).not_to_have_text('—')
            admin_page.screenshot(path=str(output/'dashboard-desktop.png'),full_page=True)
            admin_page.locator('[data-metric=gross_revenue]').click()
            expect(admin_page.locator('[data-field=ledger-rows] tr')).to_have_count(1)
            passed('Revenue card opens supporting persisted transaction')
            admin_page.locator('aside [data-action=pos]').click()
            expect(admin_page.locator('[data-field=pos-products] button').first).to_be_enabled()
            admin_page.locator('[data-field=pos-search]').fill('TEST_GUITAR')
            admin_page.locator('[data-field=pos-products] button').first.click()
            pos=admin_page.locator('form[data-form=pos]')
            pos.locator('[name=discount]').fill('10.10')
            pos.locator('[name=discount_reason]').fill('School counter discount')
            pos.locator('[name=confirmed]').check()
            admin_page.screenshot(path=str(output/'pos-desktop.png'),full_page=True)
            def interrupt_response(route):
                response=route.fetch()
                assert response.status==201
                response.dispose()
                route.abort('failed')
            admin_page.route('**/api/admin/pos',interrupt_response,times=1)
            pos.locator('[type=submit]').click()
            expect(pos.locator('[data-field=form-error]')).to_contain_text('recover the original')
            pos.locator('[type=submit]').click()
            expect(pos.locator('[data-field=pos-receipt]')).to_be_visible()
            passed('Admin POS discounted sale, lost-response recovery without duplication, collection and receipt')
            admin_page.locator('aside [data-action=transactions]').click()
            expect(admin_page.locator('[data-field=ledger-rows] tr')).to_have_count(2)
            admin_page.locator('[data-field=ledger-rows] tr').first.get_by_role('button').click()
            refund_form=admin_page.locator('dialog [data-field=refund-form]')
            refund_form.locator('[name=amount]').fill('5.00')
            refund_form.locator('[name=reason]').fill('School partial refund')
            refund_form.locator('[type=checkbox]').check()
            refund_form.locator('[type=submit]').click()
            expect(admin_page.locator('[data-field=ledger-rows]')).to_contain_text('Partially Refunded')
            with admin_page.expect_download() as download_info:
                admin_page.locator('[data-field=ledger-export]').click()
            download_info.value.save_as(output/'transactions.csv')
            passed('Admin payment details, audit events, partial refund and filtered CSV export')
            admin_page.locator('aside nav [data-action=overview]').click()
            expect(admin_page.locator('[data-field=refunded_total]')).to_contain_text('5.00')
            for width,height,label in [(768,1024,'tablet'),(390,844,'mobile')]:
                admin_page.set_viewport_size({'width':width,'height':height})
                admin_page.screenshot(path=str(output/f'dashboard-{label}.png'),full_page=True)
                assert admin_page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Admin overflow at {width}'
                page.set_viewport_size({'width':width,'height':height});page.goto('http://127.0.0.1:5097/shop')
                expect(page.locator('[data-field=products] [data-action=add]').first).to_be_enabled()
                page.locator('[data-field=products] [data-action=add]').first.click();page.locator('[data-action=checkout]').click()
                page.locator('form[data-form=checkout] [name=payment_method][value=bpi]').check()
                page.screenshot(path=str(output/f'checkout-{label}.png'),full_page=False)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Checkout overflow at {width}'
                page.locator('dialog [data-action=dialog-close]').click()
            passed('Tablet and mobile checkout/dashboard layouts without horizontal page overflow')
            # Customer cannot load any administrator API, even with a signed-in browser.
            response=context.request.get('http://127.0.0.1:5097/api/admin/transactions')
            assert response.status==403
            assert not errors,errors
            passed('Browser authorization guard and no JavaScript runtime errors')
            browser.close()
    finally:
        server.shutdown();thread.join(timeout=10);fixture.tearDown()
        (output/'browser-results.json').write_text(json.dumps({'passed':results,'runtime_errors':errors},indent=2),encoding='utf-8')
    print(f'{len(results)} browser scenarios passed. Artifacts: {output}',flush=True)


if __name__=='__main__':run()
