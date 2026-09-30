import {$, field, icon} from './dom.js';
import {api} from './api.js';

const selectedRole = 'flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white';
const plainRole = 'flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition text-zinc-500';

export function mountAuth(page, app, initialRole) {
  let role = initialRole === 'admin' ? 'admin' : 'customer';
  let mode = initialRole === 'reset' ? 'reset' : initialRole === 'register' ? 'register' : 'login';
  let loading = false, alive = true;
  const titles = {login:'Welcome to AUDIA.', register:'Find your people. Find your sound.', forgot:'Let’s get you back in.', reset:'A fresh start.'};
  const subtitles = {login:'Sign in to your account or open the store administration workspace.', register:'Create your account to save instruments, place orders, and keep track of your gear.', forgot:'Enter your account email and we’ll send you a password reset link.', reset:'Choose a new password for your AUDIA account.'};
  const labels = {login:role === 'admin' ? 'Open dashboard' : 'Sign in', register:'Create account', forgot:'Send reset link', reset:'Reset password'};
  function error(message) {field(page,'login-error').textContent=message; field(page,'login-error').hidden=!message;}
  function success(message) {field(page,'auth-success').textContent=message; field(page,'auth-success').hidden=!message;}
  function render() {
    field(page,'auth-title').textContent=titles[mode]; field(page,'auth-subtitle').textContent=subtitles[mode];
    field(page,'roles').hidden=mode!=='login'; field(page,'signup').hidden=mode!=='login'||role==='admin';
    field(page,'back-login').hidden=mode==='login'; field(page,'login-options').hidden=mode!=='login';
    for (const [name, visible] of [['name',mode==='register'], ['email',mode!=='reset'], ['password',mode!=='forgot'], ['confirm',['register','reset'].includes(mode)]]) {
      field(page,`${name}-wrap`).hidden=!visible;
      field(page,name).required=visible; field(page,name).disabled=!visible;
    }
    field(page,'password').minLength=mode==='login'?1:10;
    field(page,'password').autocomplete=mode==='login'?'current-password':'new-password';
    field(page,'password-hint').hidden=!['register','reset'].includes(mode);
    for (const option of ['customer','admin']) {
      const button=$(page,`[data-action="role-${option}"]`);
      button.className=role===option?selectedRole:plainRole; button.setAttribute('aria-pressed',String(role===option));
    }
    labels.login=role==='admin'?'Open dashboard':'Sign in';
    const submit=field(page,'login-submit'); submit.disabled=loading;
    submit.replaceChildren(loading?'Please wait… ':labels[mode]+' ',icon('arrow-right',16));
  }
  function change(next) {mode=next; error(''); success(''); render();}
  page.addEventListener('click', event => {
    const action=event.target.closest('[data-action]')?.dataset.action;
    if (action==='home'||action==='store') {
      app.catalogCategory = '';
      app.navigate(app.user ? 'storefront' : 'landing');
    }
    if (loading) return;
    if (action==='role-customer'||action==='role-admin') {role=action.slice(5); error(''); render();}
    if (action==='register') {role='customer'; change('register');}
    if (action==='forgot') change('forgot');
    if (action==='back-login') change('login');
    if (action==='password') {
      const input=field(page,'password'), showing=input.type==='password'; input.type=showing?'text':'password';
      const button=$(page,'[data-action="password"]'); button.setAttribute('aria-label',showing?'Hide password':'Show password');
      button.replaceChildren(icon(showing?'eye-off':'eye',16));
    }
  });
  page.addEventListener('submit', async event => {
    event.preventDefault(); if (loading) return;
    const password=field(page,'password').value;
    if (['register','reset'].includes(mode)&&password!==field(page,'confirm').value) return error('The passwords do not match.');
    loading=true; error(''); success(''); render();
    const submitted=mode;
    try {
      const paths={login:'login',register:'register',forgot:'forgot-password',reset:'reset-password'};
      const data=await api(`/auth/${paths[submitted]}`,{method:'POST',body:{
        email:field(page,'email').value, password, name:field(page,'name').value,
        role, remember:field(page,'remember').checked, token:app.resetToken||'',
      }});
      if (!alive) return;
      if (data.user) app.login(data.user);
      else {
        if (submitted==='reset') {app.resetToken=''; change('login');}
        success(data.message);
      }
    } catch (failure) {if(alive) error(failure.message);}
    finally {loading=false; if(alive) render();}
  });
  render();
  return {destroy(){alive=false;}};
}
