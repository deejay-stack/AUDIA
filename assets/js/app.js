import {clone, $$, icon, animate, disposeAnimations} from './dom.js';
import {mountStore} from './storefront.js';
import {mountAuth} from './auth.js';
import {mountAdmin} from './admin.js';
import {mountAccount} from './account.js';
import {api} from './api.js';
import {notice} from './ui.js';

const root = document.getElementById('root');
let current;
let user = null;
let theme = localStorage.getItem('audia-theme') || 'dark';

function updateTheme() {
  document.documentElement.classList.toggle('dark', theme === 'dark');
  localStorage.setItem('audia-theme', theme);
  $$(root, '[data-action="theme"]').forEach(button => {
    const label = `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`;
    button.setAttribute('aria-label', label); button.title = label;
    button.replaceChildren(icon(theme === 'dark' ? 'sun' : 'moon', 17));
  });
}

const app = {
  get user() { return user; },
  set user(value) { user = value; },
  navigate(screen, role = 'customer') {
    if (screen === 'dashboard' && user?.role !== 'admin') {screen = 'auth'; role = 'admin';}
    if (screen === 'account' && !user) screen = 'auth';
    document.querySelectorAll('dialog[open]').forEach(dialog => dialog.close());
    history.replaceState(null, '', screen === 'storefront' ? '/' : `/#${screen}`);
    current?.destroy?.();
    disposeAnimations(root);
    const page = clone(screen);
    root.replaceChildren(page);
    current = screen === 'storefront' ? mountStore(page, app)
      : screen === 'auth' ? mountAuth(page, app, role)
      : screen === 'account' ? mountAccount(page, app) : mountAdmin(page, app);
    updateTheme();
    animate(page);
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
      page.animate([{opacity: 0}, {opacity: 1}], {duration: 250, easing: 'ease-in-out'});
    }
    window.scrollTo({top: 0, behavior: 'smooth'});
  },
  login(account) { user = account; app.navigate(account.role === 'admin' ? 'dashboard' : 'storefront'); },
  async logout() {
    try {await api('/auth/logout', {method:'POST'}); user = null; app.navigate('storefront');}
    catch (error) {notice(error.message);}
  },
};

root.addEventListener('click', event => {
  if (event.target.closest('[data-action="theme"]')) {
    theme = theme === 'dark' ? 'light' : 'dark'; updateTheme();
  }
});
const initialHash = location.hash;
try {user = (await api('/auth/session')).user;} catch (error) {notice(error.message);}
if (initialHash.startsWith('#reset/')) {
  app.resetToken = initialHash.slice(7); app.navigate('auth', 'reset');
} else app.navigate(['#dashboard', '#account', '#auth'].includes(initialHash) ? initialHash.slice(1) : 'storefront');
