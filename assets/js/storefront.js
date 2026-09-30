import {imageSource} from './media.js';
import {api} from './api.js';
import {dialog, notice, formError, busy, orderDetails} from './ui.js';
import {readCart, writeCart} from './cart-storage.js';
import {$, $$, field, text, clone, icon, peso, animate, dismiss} from './dom.js';

const questions = [
  {key: 'budget', title: 'What is your budget?'},
  {key: 'level', title: 'What is your experience level?', options: ['Beginner', 'Intermediate', 'Advanced']},
  {key: 'genre', title: 'What do you want to play?', options: ['Rock', 'Pop', 'Blues', 'Jazz', 'Classical']},
  {key: 'category', title: 'Which guitar type do you prefer?', options: ['Electric', 'Acoustic', 'Classical', 'Bass']},
];
const selectedOption = 'rounded-2xl border p-5 text-left text-sm transition border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid';
const plainOption = 'rounded-2xl border p-5 text-left text-sm transition border-zinc-200 hover:border-zinc-400 dark:border-white/10';

export function mountStore(page, app) {
  // State is scoped to this visit, matching the original screen's lifetime.
  let products = [];
  let saved = new Set();
  const storedCart = readCart();
  let cart = [];
  let filter = 'All';
  let search = app.searchProduct || ''; app.searchProduct = '';
  field(page, 'search').value = search;
  let sort = 'Featured';
  let cartPanel;
  let finder;
  let finderStep = 0;
  let results = [];
  let answers = {budget: 20000, level: 'Beginner', genre: 'Rock', category: 'Electric'};
  let mobile;
  let chat;
  let chatInput = '';
  let messages = [{role: 'guide', text: 'Hi, I’m AUDI. Tell me your budget or the kind of music you want to play, and I’ll help narrow the options.'}];
  const cards = new Map();
  const timers = new Set();
  const soundTimers = new Map();
  let alive = true;

  const account = $(page, '[data-action="account"]');
  account.setAttribute('aria-label', app.user ? 'Open account' : 'Sign in');

  function renderProducts() {
    let list = products.filter(p => (filter === 'All' || p.category === filter)
      && `${p.name} ${p.brand}`.toLowerCase().includes(search.toLowerCase()));
    if (sort === 'Price: low') list = [...list].sort((a, b) => a.price - b.price);
    if (sort === 'Price: high') list = [...list].sort((a, b) => b.price - a.price);
    if (sort === 'Rating') list = [...list].sort((a, b) => b.rating - a.rating);
    const grid = field(page, 'products');
    const activeIds = new Set(list.map(p => p.id));
    for (const [id, card] of cards) if (!activeIds.has(id)) {card.remove(); cards.delete(id);}
    const nextCards = list.map((product, index) => {
      let card = cards.get(product.id);
      const fresh = !card;
      if (fresh) {
        card = clone('product-card'); cards.set(product.id, card);
        const motion = JSON.parse(card.dataset.motion);
        motion.transition.delay = index * .05; card.dataset.motion = JSON.stringify(motion);
      }
      card.dataset.productId = product.id;
      const image = field(card, 'image'); image.src = imageSource(product.image); image.alt = product.name;
      text(card, 'badge', product.badge); text(card, 'category', `${product.brand} · ${product.category}`);
      text(card, 'rating', `${product.rating} (${product.reviews})`); text(card, 'name', product.name);
      text(card, 'description', product.description); text(card, 'price', peso(product.price));
      text(card, 'stock', product.stock ? `${product.stock} available` : 'Out of stock');
      const add = $(card, '[data-action="add"]'); add.disabled = product.stock < 1;
      const heart = $(card, '[data-action="like"] svg');
      heart.setAttribute('fill', saved.has(product.id) ? 'currentColor' : 'none'); heart.classList.toggle('text-rose-500', saved.has(product.id));
      $(card, '[data-action="add"]').setAttribute('aria-label', `Add ${product.name} to cart`);
      return {card, fresh};
    });
    grid.replaceChildren(...nextCards.map(item => item.card));
    nextCards.filter(item => item.fresh).forEach(item => animate(item.card));
    field(page, 'no-products').hidden = list.length > 0;
    $$(page, '.filter-chip').forEach(button => button.classList.toggle('filter-chip-active', button.dataset.category === filter));
  }

  function renderCart() {
    writeCart(cart);
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const button = $(page, '[data-action="cart"]');
    let badge = $(button, 'span');
    if (count && !badge) {
      badge = clone('cart-badge'); button.append(badge);
    }
    if (badge) {badge.textContent = count; badge.hidden = count === 0;}
    if (!cartPanel) return;
    text(cartPanel, 'cart-count', `${count} items`);
    const body = field(cartPanel, 'cart-body');
    if (!cart.length) body.replaceChildren(clone('cart-empty'));
    else {
      const rows = clone('cart-items');
      rows.replaceChildren(...cart.map(item => {
        const row = clone('cart-item'); row.dataset.productId = item.id;
        field(row, 'image').src = imageSource(item.image);
        text(row, 'brand', item.brand); text(row, 'name', item.name);
        text(row, 'price', peso(item.price)); text(row, 'quantity', item.qty);
        return row;
      }));
      body.replaceChildren(rows);
    }
    field(cartPanel, 'cart-footer').hidden = cart.length === 0;
    text(cartPanel, 'subtotal', peso(cart.reduce((sum, item) => sum + item.price * item.qty, 0)));
  }
  function openCart() {
    if (!cartPanel) {cartPanel = clone('cart'); page.append(cartPanel); animate(cartPanel);}
    renderCart();
  }
  function addToCart(product) {
    if (!product || product.stock < 1) return notice('This item is currently out of stock.');
    if ((cart.find(item => item.id === product.id)?.qty || 0) >= product.stock) return notice('You have reached the available stock for this item.');
    cart = cart.some(item => item.id === product.id)
      ? cart.map(item => item.id === product.id ? {...item, qty: item.qty + 1} : item)
      : [...cart, {...product, qty: 1}];
    openCart();
  }
  function changeQuantity(id, delta) {
    const item = cart.find(item => item.id === id);
    if (delta > 0 && item && item.qty >= item.stock) return notice('You have reached the available stock for this item.');
    cart = cart.map(item => item.id === id ? {...item, qty: Math.max(0, item.qty + delta)} : item).filter(item => item.qty > 0);
    renderCart();
  }
  function closeCart() { const closing = cartPanel; cartPanel = null; dismiss(closing, 'cart'); }

  function renderFinder() {
    if (!finder) return;
    const modal = $(finder, '.finder-modal');
    modal.children[1]?.remove();
    if (finderStep === 4) {
      const body = clone('finder-results');
      field(body, 'matches').replaceChildren(...results.map((product, index) => {
        const row = clone('finder-match'); row.dataset.productId = product.id;
        field(row, 'image').src = imageSource(product.image);
        text(row, 'rank', index + 1); text(row, 'name', product.name);
        text(row, 'category', `${product.category} · ${product.level}`); text(row, 'price', peso(product.price));
        return row;
      }));
      modal.append(body);
    } else {
      const body = field(clone('finder'), 'finder-body');
      const question = questions[finderStep];
      text(body, 'question-number', `Question ${finderStep + 1} of 4`);
      text(body, 'question-title', question.title);
      [...field(body, 'progress').children].forEach((bar, i) => {
        bar.className = `h-1 flex-1 rounded-full ${i <= finderStep ? 'bg-zinc-950 dark:bg-acid' : 'bg-zinc-200 dark:bg-white/10'}`;
      });
      field(body, 'budget').hidden = finderStep !== 0;
      text(body, 'budget-value', peso(answers.budget)); field(body, 'budget-input').value = answers.budget;
      const options = field(body, 'options'); options.hidden = finderStep === 0;
      options.replaceChildren(...(question.options || []).map(option => {
        const button = clone('finder-option'); button.dataset.option = option;
        button.textContent = option;
        const selected = answers[question.key] === option;
        button.className = selected ? selectedOption : plainOption;
        if (selected) button.append(clone('check'));
        return button;
      }));
      $(body, '[data-action="finder-next"]').replaceChildren(finderStep === 3 ? 'Show my matches ' : 'Continue ', icon('arrow-right', 16));
      modal.append(body);
    }
  }
  function openFinder() {
    closeMobile();
    if (finder) return;
    finder = clone('finder'); page.append(finder); renderFinder(); animate(finder);
  }
  function closeFinder() {
    const closing = finder; finder = null; finderStep = 0; results = []; dismiss(closing);
  }
  async function finishFinder() {
    const button = $(finder, '[data-action="finder-next"]');
    if (button.disabled) return; button.disabled = true;
    try {
      const data = await api('/finder', {method:'POST', body:answers}); results = data.recommendations;
      finderStep = 4; if (alive) renderFinder();
    } catch (error) {notice(error.message); button.disabled = false;}
  }

  function openCheckout() {
    if (!app.user) {notice('Sign in to place your order. Your cart is saved.'); app.navigate('auth'); return;}
    if (!cart.length) return;
    const panel = dialog('Your next chapter starts here.', 'checkout');
    const form = panel.querySelector('form');
    form.elements.address.value = app.user.address || ''; form.elements.phone.value = app.user.phone || '';
    field(form,'checkout-total').textContent = peso(cart.reduce((sum,item)=>sum+item.price*item.qty,0));
    const requestKey = crypto.randomUUID();
    form.addEventListener('submit', async event => {
      event.preventDefault(); if(form.querySelector('[type=submit]').disabled)return;
      busy(form,true);formError(form,'');
      try {
        const data=await api('/orders',{method:'POST',body:{request_key:requestKey,address:form.elements.address.value,phone:form.elements.phone.value,
          items:cart.map(item=>({product_id:item.id,quantity:item.qty}))}});
        for(const item of cart) {const product=products.find(p=>p.id===item.id);if(product)product.stock-=item.qty;}
        cart=[];renderCart();renderProducts();panel.close();closeCart();orderDetails(data.order);notice('Your order has been placed.');
      }catch(error){formError(form,error.message);}
      finally{busy(form,false,'Place order');}
    });
  }

  async function trackOrder() {
    if (!app.user) {notice('Sign in to track orders securely.');app.navigate('auth');return;}
    const id=field(page,'order').value.trim(); if(!id)return notice('Enter your order number.');
    try {const data=await api(`/orders/${encodeURIComponent(id)}`);if(alive)orderDetails(data.order);}
    catch(error){notice(error.message);}
  }

  function renderMessages() {
    if (!chat) return;
    const container = field(chat, 'messages');
    container.replaceChildren(...messages.map(message => {
      const bubble = clone('message');
      bubble.className = `max-w-[86%] rounded-2xl px-4 py-3 text-xs leading-5 ${message.role === 'user'
        ? 'ml-auto bg-zinc-950 text-white dark:bg-acid dark:text-ink' : 'bg-zinc-100 dark:bg-white/[.07]'}`;
      bubble.textContent = message.text;
      return bubble;
    }));
    if (messages.length === 1) container.append(clone('chat-suggestions'));
  }
  function toggleChat() {
    if (chat) {const closing = chat; chat = null; dismiss(closing);}
    else {chat = clone('chat'); page.append(chat); field(chat, 'chat-input').value = chatInput; renderMessages(); animate(chat);}
    $(page, '[data-action="chat"]').replaceChildren(icon(chat ? 'x' : 'message-circle', chat ? 20 : 21));
  }
  async function send(preset) {
    const message = preset || chatInput.trim(); if (!message) return;
    messages = [...messages, {role: 'user', text: message}]; chatInput = '';
    if (chat) field(chat, 'chat-input').value = '';
    renderMessages();
    try {
      const data = await api('/chat', {method: 'POST', body: {message}}); messages = [...messages, {role: 'guide', text: data.reply}];
    } catch (error) {
      messages = [...messages, {role: 'guide', text: error.message}];
    }
    if (alive) renderMessages();
  }

  function closeMobile() {
    if (mobile) {mobile.remove(); mobile = null;}
    $(page, '[data-action="menu"]').replaceChildren(icon('menu', 19));
  }
  function toggleMobile() {
    if (mobile) return closeMobile();
    mobile = clone('mobile-nav'); $(page, 'header').append(mobile); animate(mobile);
    $(page, '[data-action="menu"]').replaceChildren(icon('x', 19));
  }
  function playSound(button) {
    function display(playing) {
      const label = $(button, 'span');
      const glyph = icon(playing ? 'pause' : 'play', 15); glyph.setAttribute('fill', 'currentColor');
      button.replaceChildren(glyph);
      if (label) {label.textContent = playing ? 'Playing' : 'Hear the tone'; button.append(label);}
    }
    if (soundTimers.has(button)) {
      clearTimeout(soundTimers.get(button)); soundTimers.delete(button); display(false); return;
    }
    display(true);
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      [164.81, 196, 246.94, 329.63].forEach((frequency, index) => {
        const oscillator = ctx.createOscillator(); const gain = ctx.createGain();
        oscillator.type = 'triangle'; oscillator.frequency.value = frequency;
        gain.gain.setValueAtTime(0, ctx.currentTime + index * .18);
        gain.gain.linearRampToValueAtTime(.055, ctx.currentTime + index * .18 + .03);
        gain.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + index * .18 + .72);
        oscillator.connect(gain).connect(ctx.destination);
        oscillator.start(ctx.currentTime + index * .18); oscillator.stop(ctx.currentTime + index * .18 + .75);
      });
      soundTimers.set(button, setTimeout(() => {soundTimers.delete(button); display(false); ctx.close();}, 1450));
    } catch {display(false);}
  }

  page.addEventListener('click', async event => {
    const button = event.target.closest('[data-action]'); if (!button) return;
    if (button.tagName === 'A') event.preventDefault();
    const id = Number(button.closest('[data-product-id]')?.dataset.productId);
    switch (button.dataset.action) {
      case 'home': window.scrollTo({top: 0, behavior: 'smooth'}); break;
      case 'account': {
        const fromMobile = mobile?.contains(button); closeMobile();
        app.navigate(app.user?.role === 'admin' ? 'dashboard' : app.user ? 'account' : 'auth'); break;
      }
      case 'admin-login': app.navigate('auth', 'admin'); break;
      case 'menu': toggleMobile(); break;
      case 'mobile-link': closeMobile(); break;
      case 'finder': openFinder(); break;
      case 'close-finder': closeFinder(); break;
      case 'finder-next': if (finderStep === 3) finishFinder(); else {finderStep += 1; renderFinder();} break;
      case 'finder-option': answers = {...answers, [questions[finderStep].key]: button.dataset.option}; renderFinder(); break;
      case 'finder-restart': finderStep = 0; renderFinder(); break;
      case 'add-match': addToCart(results.find(p => p.id === id)); closeFinder(); break;
      case 'search':
        $(page, '#shop').scrollIntoView({behavior: 'smooth'});
        timers.add(setTimeout(() => field(page, 'search')?.focus(), 450)); break;
      case 'category': filter = button.dataset.category; renderProducts(); $(page, '#shop').scrollIntoView({behavior: 'smooth'}); break;
      case 'filter': filter = button.dataset.category; renderProducts(); break;
      case 'add': addToCart(products.find(p => p.id === id)); break;
      case 'cart': openCart(); break;
      case 'checkout': openCheckout(); break;
      case 'bundle': {
        const product = products.find(p=>p.category==='Bundles');
        if(product) {const panel=dialog(product.name,'bundle-detail');field(panel,'description').textContent=product.description;field(panel,'price').textContent=peso(product.price);field(panel,'image').src = imageSource(product.image);field(panel,'image').alt=product.name;
          field(panel,'bundle-add').addEventListener('click',()=>{panel.close();addToCart(product);});}
        else notice('This bundle is not currently available. Please contact the store.');
        break;
      }
      case 'support-info': {
        const panel=dialog(button.textContent.trim(),'support-info');
        const topic=button.dataset.topic;
        const descriptions={delivery:'Delivery details are confirmed with your order. For a return, contact the store with your order number before sending an item back.', warranty:'Warranty coverage depends on the instrument and manufacturer. Contact the store with your order number and a description of the issue.', setup:'Every instrument benefits from a setup matched to your playing style. Ask the store about action, string gauge, and setup availability.'};
        field(panel,'support-copy').textContent=descriptions[topic]||'Ask AUDI for guitar guidance or contact the store about an existing order.';
        api('/store').then(data=>{if(panel.isConnected){const link=field(panel,'support-email');link.textContent=data.store.support_email;link.href=`mailto:${data.store.support_email}`;}}).catch(error=>notice(error.message));
        break;
      }
      case 'close-cart': closeCart(); break;
      case 'increase': changeQuantity(id, 1); break;
      case 'decrease': changeQuantity(id, -1); break;
      case 'like': {
        if(!app.user) {notice('Sign in to save instruments.');app.navigate('auth');break;}
        button.disabled=true;
        try {const data=await api(`/account/saved/${id}`,{method:saved.has(id)?'DELETE':'PUT'});
          if(data.saved)saved.add(id);else saved.delete(id);if(alive)renderProducts();}
        catch(error){notice(error.message);}finally{button.disabled=false;}
        break;
      }
      case 'sound': playSound(button); break;
      case 'track': trackOrder(); break;
      case 'chat': toggleChat(); break;
      case 'chat-suggestion': send(button.textContent); break;
    }
  });
  page.addEventListener('input', event => {
    switch (event.target.dataset.field) {
      case 'search': search = event.target.value; renderProducts(); break;
      
      case 'budget-input': answers = {...answers, budget: Number(event.target.value)}; text(finder, 'budget-value', peso(answers.budget)); break;
      case 'chat-input': chatInput = event.target.value; break;
    }
  });
  page.addEventListener('change', event => {
    if (event.target.dataset.field === 'sort') {sort = event.target.value; renderProducts();}
  });
  page.addEventListener('submit', event => {
    if (event.target.dataset.form === 'chat') {event.preventDefault(); send();}
  });
  field(page,'no-products').hidden=false; field(page,'no-products').textContent='Loading instruments…';
  api('/products').then(data=>{
    if(!alive)return;products=data.products;
    cart=storedCart.map(item=>{const product=products.find(p=>p.id===item.id);return product?{...product,qty:item.qty}:null;}).filter(Boolean);
    field(page,'no-products').textContent='No guitar matches that search.';renderProducts();renderCart();
    if(app.openFinder){app.openFinder=false;openFinder();}
    if(search) $(page,'#shop').scrollIntoView();
  }).catch(error=>{if(alive){field(page,'no-products').hidden=false;field(page,'no-products').textContent=error.message;}});
  if(app.user)api('/account/saved').then(data=>{if(alive){saved=new Set(data.products.map(p=>p.id));if(data.profile)answers=data.profile;renderProducts();}}).catch(error=>notice(error.message));
  return {destroy() {alive = false; timers.forEach(clearTimeout);}};
}
