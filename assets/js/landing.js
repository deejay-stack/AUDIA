export function mountLanding(page, app) {
  page.querySelectorAll('[data-auth-entry]').forEach(node => {node.hidden = Boolean(app.user);});
  page.querySelectorAll('[data-member-entry]').forEach(node => {node.hidden = !app.user;});
  page.addEventListener('click', event => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    if (button.dataset.action === 'register') app.navigate('auth', 'register');
    if (button.dataset.action === 'sign-in') app.navigate('auth');
    if (button.dataset.action === 'browse') {
      app.catalogCategory = button.dataset.category || '';
      app.navigate(app.user ? 'storefront' : 'auth');
    }
  });
  return {destroy() {}};
}
