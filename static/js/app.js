import {clone, $$, icon, animate, disposeAnimations} from './dom.js';
import {mountStore} from './storefront.js';
import {mountAuth} from './auth.js';
import {mountAdmin} from './admin.js';

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
  navigate(screen, role = 'customer') {
    current?.destroy?.();
    disposeAnimations(root);
    const page = clone(screen);
    root.replaceChildren(page);
    current = screen === 'storefront' ? mountStore(page, app)
      : screen === 'auth' ? mountAuth(page, app, role) : mountAdmin(page, app);
    updateTheme();
    animate(page);
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
      page.animate([{opacity: 0}, {opacity: 1}], {duration: 250, easing: 'ease-in-out'});
    }
    window.scrollTo({top: 0, behavior: 'smooth'});
  },
  login(account) { user = account; app.navigate(account.role === 'admin' ? 'dashboard' : 'storefront'); },
  logout() { user = null; app.navigate('storefront'); },
};

root.addEventListener('click', event => {
  if (event.target.closest('[data-action="theme"]')) {
    theme = theme === 'dark' ? 'light' : 'dark'; updateTheme();
  }
});
app.navigate('storefront');
