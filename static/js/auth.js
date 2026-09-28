import {$, field, icon} from './dom.js';

const selectedRole = 'flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white';
const plainRole = 'flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition text-zinc-500';

export function mountAuth(page, app, initialRole) {
  let role = initialRole;
  let showPassword = false;
  let loading = false;
  let alive = true;
  function setError(message) {
    const error = field(page, 'login-error'); error.textContent = message; error.hidden = !message;
  }
  function renderSubmit() {
    const button = field(page, 'login-submit'); button.disabled = loading;
    button.replaceChildren(loading ? 'Signing in… ' : role === 'admin' ? 'Open dashboard ' : 'Sign in ', icon('arrow-right', 16));
  }
  function changeRole(next) {
    role = next; setError('');
    field(page, 'email').value = role === 'admin' ? 'admin@audia.ph' : 'user@audia.ph';
    field(page, 'password').value = role === 'admin' ? 'admin123' : 'audia123';
    $(page, '[data-action="role-customer"]').className = role === 'customer' ? selectedRole : plainRole;
    $(page, '[data-action="role-admin"]').className = role === 'admin' ? selectedRole : plainRole;
    const demo = field(page, 'demo');
    const label = $(demo, 'span');
    demo.replaceChildren(label, role === 'admin' ? ' admin@audia.ph / admin123' : ' user@audia.ph / audia123');
    field(page, 'signup').hidden = role !== 'customer';
    renderSubmit();
  }
  page.addEventListener('click', event => {
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (action === 'home' || action === 'store') app.navigate('storefront');
    if (action === 'role-customer') changeRole('customer');
    if (action === 'role-admin') changeRole('admin');
    if (action === 'password') {
      showPassword = !showPassword;
      field(page, 'password').type = showPassword ? 'text' : 'password';
      const button = $(page, '[data-action="password"]');
      button.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
      button.replaceChildren(icon(showPassword ? 'eye-off' : 'eye', 16));
    }
  });
  page.addEventListener('submit', async event => {
    event.preventDefault();
    const email = field(page, 'email').value;
    const password = field(page, 'password').value;
    const submittedRole = role;
    loading = true; setError(''); renderSubmit();
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password, role: submittedRole}),
      });
      if (!response.ok) throw new Error('Incorrect email or password.');
      const data = await response.json(); if (alive) app.login(data.user);
    } catch (requestError) {
      const demoIsValid = submittedRole === 'admin' ? email === 'admin@audia.ph' && password === 'admin123' : email.includes('@') && password.length >= 6;
      if (alive && demoIsValid) app.login({name: submittedRole === 'admin' ? 'AUDIA Admin' : 'Jay Player', email, role: submittedRole});
      else if (alive) setError(requestError.message || 'Unable to sign in.');
    } finally { loading = false; if (alive) renderSubmit(); }
  });
  changeRole(role);
  return {destroy() {alive = false;}};
}
