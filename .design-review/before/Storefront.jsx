import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import {
  ArrowRight, ArrowUpRight, Check, ChevronDown, ChevronRight, CircleUserRound, Compass,
  Guitar, Headphones, Heart, Menu, MessageCircle, Minus, PackageCheck, Pause, Play, Plus,
  Search, ShieldCheck, ShoppingBag, SlidersHorizontal, Star, Truck, Volume2, Wand2, X,
} from 'lucide-react'
import { categories, fallbackProducts } from '../data'
import { Logo, Reveal, ThemeToggle, peso } from './UI'

function Announcement() {
  return (
    <div className="bg-zinc-950 px-5 py-2.5 text-center text-[10px] font-semibold uppercase tracking-[.18em] text-white dark:bg-acid dark:text-ink">
      Free nationwide delivery over ₱15,000 <span className="mx-2 opacity-40">•</span> Professional setup included
    </div>
  )
}

function Header({ cartCount, onCart, onFinder, onSearch, theme, setTheme, user, onAuth, onAdmin }) {
  const [mobile, setMobile] = useState(false)
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/80 bg-stone-50/90 backdrop-blur-xl dark:border-white/10 dark:bg-ink/90">
      <div className="shell flex h-[76px] items-center justify-between">
        <Logo onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} />
        <nav className="hidden items-center gap-8 text-sm font-medium text-zinc-600 dark:text-zinc-400 lg:flex">
          <a className="nav-link" href="#shop">Shop</a>
          <a className="nav-link" href="#categories">Guitars</a>
          <button className="nav-link flex items-center gap-2" onClick={onFinder}><Compass size={15} /> Guitar finder</button>
          <a className="nav-link" href="#bundles">Bundles</a>
          <a className="nav-link" href="#track">Track order</a>
        </nav>
        <div className="flex items-center gap-1.5">
          <ThemeToggle theme={theme} setTheme={setTheme} compact />
          <button onClick={onSearch} className="icon-btn" aria-label="Search"><Search size={18} /></button>
          <button onClick={user?.role === 'admin' ? onAdmin : onAuth} className="icon-btn hidden sm:grid" aria-label={user ? 'Open account' : 'Sign in'}><CircleUserRound size={19} /></button>
          <button onClick={onCart} className="icon-btn relative" aria-label="Open cart">
            <ShoppingBag size={19} />
            {cartCount > 0 && <span className="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink">{cartCount}</span>}
          </button>
          <button onClick={() => setMobile(!mobile)} className="icon-btn lg:hidden" aria-label="Open menu">{mobile ? <X size={19} /> : <Menu size={19} />}</button>
        </div>
      </div>
      <AnimatePresence>
        {mobile && (
          <motion.nav initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="shell overflow-hidden border-t border-zinc-200 dark:border-white/10 lg:hidden">
            <div className="flex flex-col gap-1 py-4 text-sm">
              {[['Shop', '#shop'], ['Guitars', '#categories'], ['Bundles', '#bundles'], ['Track order', '#track']].map(([label, href]) => <a key={label} onClick={() => setMobile(false)} href={href} className="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5">{label}</a>)}
              <button onClick={() => { setMobile(false); onFinder() }} className="flex items-center gap-2 rounded-xl px-3 py-3 text-left"><Compass size={16} /> Guitar finder</button>
              <button onClick={() => { setMobile(false); onAuth() }} className="flex items-center gap-2 rounded-xl px-3 py-3 text-left"><CircleUserRound size={16} /> Sign in</button>
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}

function SoundButton({ label = false }) {
  const [playing, setPlaying] = useState(false)
  const timer = useRef()
  const play = () => {
    if (playing) { setPlaying(false); clearTimeout(timer.current); return }
    setPlaying(true)
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      const ctx = new AudioCtx()
      ;[164.81, 196, 246.94, 329.63].forEach((frequency, index) => {
        const oscillator = ctx.createOscillator(); const gain = ctx.createGain()
        oscillator.type = 'triangle'; oscillator.frequency.value = frequency
        gain.gain.setValueAtTime(0, ctx.currentTime + index * .18)
        gain.gain.linearRampToValueAtTime(.055, ctx.currentTime + index * .18 + .03)
        gain.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + index * .18 + .72)
        oscillator.connect(gain).connect(ctx.destination); oscillator.start(ctx.currentTime + index * .18); oscillator.stop(ctx.currentTime + index * .18 + .75)
      })
      timer.current = setTimeout(() => setPlaying(false), 1450)
    } catch { setPlaying(false) }
  }
  return <button onClick={play} className={`${label ? 'h-11 gap-2 px-4' : 'h-10 w-10'} inline-flex items-center justify-center rounded-full bg-white text-zinc-950 shadow-lg transition hover:scale-105`} aria-label="Play guitar tone">{playing ? <Pause size={15} fill="currentColor" /> : <Play size={15} fill="currentColor" />}{label && <span className="text-xs font-semibold">{playing ? 'Playing' : 'Hear the tone'}</span>}</button>
}

function Hero({ onFinder }) {
  const reduce = useReducedMotion()
  return (
    <section id="top" className="relative overflow-hidden border-b border-zinc-200 dark:border-white/10">
      <div className="hero-mesh absolute inset-0 opacity-70 dark:opacity-100" />
      <div className="shell relative grid min-h-[720px] items-center gap-12 py-16 lg:grid-cols-[.9fr_1.1fr] lg:py-10">
        <motion.div initial={reduce ? false : { opacity: 0, y: 32 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .8, ease: [0.22, 1, 0.36, 1] }} className="relative z-10 max-w-xl">
          <p className="section-label">The 2026 electric edit</p>
          <h1 className="mt-5 font-display text-[clamp(3.4rem,7.5vw,7rem)] font-semibold leading-[.88] tracking-[-.065em]">
            Make some<br /><span className="text-outline">noise.</span>
          </h1>
          <p className="mt-7 max-w-lg text-base leading-7 text-zinc-600 dark:text-zinc-400 sm:text-lg">Discover guitars chosen for feel, tone, and lasting value. Compare the details, listen to a preview, and find an instrument you’ll keep reaching for.</p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <a href="#shop" className="primary-btn">Shop guitars <ArrowRight size={17} /></a>
            <button onClick={onFinder} className="secondary-btn"><Compass size={16} /> Find my guitar</button>
          </div>
          <div className="mt-12 grid grid-cols-3 border-t border-zinc-200 pt-6 dark:border-white/10">
            {[['120+', 'instruments'], ['4.9', 'buyer rating'], ['2-year', 'warranty']].map(([value, label]) => <div key={label}><div className="font-display text-xl font-semibold sm:text-2xl">{value}</div><div className="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]">{label}</div></div>)}
          </div>
        </motion.div>
        <motion.div initial={reduce ? false : { opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1, delay: .12, ease: [0.22, 1, 0.36, 1] }} className="relative min-h-[480px] lg:min-h-[650px]">
          <div className="absolute inset-0 overflow-hidden rounded-[2rem] bg-zinc-900 shadow-2xl sm:inset-5 lg:inset-8">
            <img className="h-full w-full object-cover object-center transition duration-1000 hover:scale-[1.025]" src="https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=1500&q=90" alt="Guitarist performing with an electric guitar" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-black/5" />
            <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between text-white sm:bottom-8 sm:left-8 sm:right-8">
              <div><p className="text-[10px] font-semibold uppercase tracking-[.18em] text-white/60">Featured sound</p><h2 className="mt-2 font-display text-2xl font-semibold">Midnight Drive</h2><p className="mt-1 text-xs text-white/60">Warm humbuckers · crisp overdrive</p></div>
              <SoundButton label />
            </div>
          </div>
          <div className="absolute right-0 top-3 rounded-2xl border border-zinc-200 bg-white p-4 shadow-xl dark:border-white/10 dark:bg-zinc-900 sm:right-1 sm:top-12">
            <div className="flex items-center gap-3"><Guitar size={18} /><div><p className="text-xs font-semibold">Free setup</p><p className="mt-0.5 text-[10px] text-zinc-500">Ready to play on arrival</p></div></div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function Categories({ onSelect }) {
  return (
    <section id="categories" className="shell py-24 sm:py-28">
      <Reveal className="mb-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div><p className="section-label">Browse the collection</p><h2 className="section-title">Choose your voice.</h2></div>
        <p className="max-w-sm text-sm leading-6 text-zinc-500">Start with the instrument family that fits the sound in your head.</p>
      </Reveal>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {categories.map((category, index) => (
          <Reveal key={category.name} delay={index * .07}>
            <motion.button whileHover={{ y: -7 }} onClick={() => onSelect(category.name)} className="group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm">
              <img src={category.image} alt={`${category.name} guitar`} className="h-full w-full object-cover transition duration-700 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent" />
              <div className="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"><div><p className="text-[10px] uppercase tracking-[.16em] text-white/55">0{index + 1} · {category.count}</p><h3 className="mt-2 font-display text-2xl font-semibold">{category.name}</h3></div><span className="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"><ArrowUpRight size={17} /></span></div>
            </motion.button>
          </Reveal>
        ))}
      </div>
    </section>
  )
}

function ProductCard({ product, onAdd }) {
  const [liked, setLiked] = useState(false)
  return (
    <motion.article layout className="product-card group">
      <div className="relative aspect-[4/4.5] overflow-hidden rounded-[1.15rem] bg-zinc-100 dark:bg-zinc-900">
        <img src={product.image} alt={product.name} className="h-full w-full object-cover transition duration-700 group-hover:scale-[1.04]" />
        <span className="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1.5 text-[9px] font-bold uppercase tracking-[.12em] text-zinc-950 backdrop-blur">{product.badge}</span>
        <button onClick={() => setLiked(!liked)} className="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full bg-white/90 text-zinc-950 shadow-sm" aria-label="Save guitar"><Heart size={15} fill={liked ? 'currentColor' : 'none'} className={liked ? 'text-rose-500' : ''} /></button>
        <div className="absolute bottom-3 right-3"><SoundButton /></div>
      </div>
      <div className="px-1 pb-2 pt-5">
        <div className="flex items-center justify-between text-[10px] uppercase tracking-[.14em] text-zinc-500"><span>{product.brand} · {product.category}</span><span className="flex items-center gap-1 normal-case tracking-normal"><Star size={11} className="fill-amber-400 text-amber-400" /> {product.rating} ({product.reviews})</span></div>
        <h3 className="mt-2 font-display text-lg font-semibold">{product.name}</h3>
        <p className="mt-2 line-clamp-2 min-h-[40px] text-xs leading-5 text-zinc-500">{product.description}</p>
        <div className="mt-5 flex items-center justify-between"><div><p className="text-lg font-semibold">{peso(product.price)}</p><p className="mt-0.5 text-[10px] text-zinc-500">{product.stock} available</p></div><button onClick={() => onAdd(product)} className="grid h-11 w-11 place-items-center rounded-full bg-zinc-950 text-white transition hover:scale-105 dark:bg-acid dark:text-ink" aria-label={`Add ${product.name} to cart`}><Plus size={17} /></button></div>
      </div>
    </motion.article>
  )
}

function Shop({ products, onAdd, filter, setFilter, search, setSearch }) {
  const [sort, setSort] = useState('Featured')
  const filtered = useMemo(() => {
    const list = products.filter((p) => (filter === 'All' || p.category === filter) && `${p.name} ${p.brand}`.toLowerCase().includes(search.toLowerCase()))
    if (sort === 'Price: low') return [...list].sort((a, b) => a.price - b.price)
    if (sort === 'Price: high') return [...list].sort((a, b) => b.price - a.price)
    if (sort === 'Rating') return [...list].sort((a, b) => b.rating - a.rating)
    return list
  }, [products, filter, search, sort])
  return (
    <section id="shop" className="border-y border-zinc-200 bg-white py-24 dark:border-white/10 dark:bg-[#0c0c0f] sm:py-28">
      <div className="shell">
        <Reveal className="flex flex-col justify-between gap-7 lg:flex-row lg:items-end">
          <div><p className="section-label">Curated instruments</p><h2 className="section-title">Guitars worth playing.</h2></div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <label className="input-shell min-w-[270px]"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} className="w-full bg-transparent py-3 text-sm outline-none" placeholder="Search guitars or brands" /></label>
            <label className="input-shell"><SlidersHorizontal size={15} /><select value={sort} onChange={(e) => setSort(e.target.value)} className="appearance-none bg-transparent py-3 pr-4 text-sm outline-none"><option>Featured</option><option>Price: low</option><option>Price: high</option><option>Rating</option></select><ChevronDown size={13} /></label>
          </div>
        </Reveal>
        <div className="mt-8 flex gap-2 overflow-x-auto pb-2">{['All', 'Electric', 'Acoustic', 'Classical', 'Bass'].map((item) => <button key={item} onClick={() => setFilter(item)} className={`filter-chip ${filter === item ? 'filter-chip-active' : ''}`}>{item}</button>)}</div>
        <motion.div layout className="mt-9 grid gap-x-5 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">{filtered.map((product, index) => <Reveal key={product.id} delay={index * .05}><ProductCard product={product} onAdd={onAdd} /></Reveal>)}</motion.div>
        {!filtered.length && <div className="mt-9 rounded-2xl border border-dashed border-zinc-300 py-20 text-center text-sm text-zinc-500 dark:border-white/15">No guitar matches that search.</div>}
      </div>
    </section>
  )
}

function FinderBanner({ onOpen }) {
  return (
    <section className="shell py-24 sm:py-28">
      <Reveal>
        <div className="relative overflow-hidden rounded-[2rem] bg-zinc-950 px-7 py-16 text-white dark:bg-gradient-to-br dark:from-[#1c1330] dark:via-zinc-950 dark:to-zinc-950 sm:px-12 lg:px-20 lg:py-20">
          <div className="absolute -right-28 -top-28 h-80 w-80 rounded-full bg-violet-500/25 blur-[100px]" />
          <div className="relative grid items-center gap-12 lg:grid-cols-[1fr_.72fr]">
            <div><p className="text-[10px] font-semibold uppercase tracking-[.2em] text-acid">Guitar finder</p><h2 className="mt-4 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">Four questions.<br />A much better shortlist.</h2><p className="mt-5 max-w-xl leading-7 text-zinc-400">Choose your budget, experience, preferred style, and guitar type. AUDIA will narrow the catalog to practical matches.</p><button onClick={onOpen} className="primary-btn mt-8">Start guitar finder <Compass size={17} /></button></div>
            <div className="rounded-3xl border border-white/10 bg-white/[.055] p-6 backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[.16em] text-zinc-500">Example profile</p>
              <div className="mt-6 divide-y divide-white/10">{[['Budget', '₱10k – ₱20k'], ['Experience', 'Beginner'], ['Genre', 'Rock'], ['Type', 'Electric']].map(([label, value]) => <div key={label} className="flex items-center justify-between py-4 text-sm"><span className="text-zinc-500">{label}</span><span className="font-medium">{value}</span></div>)}</div>
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  )
}

function Bundle() {
  return (
    <section id="bundles" className="shell pb-24 sm:pb-28">
      <Reveal className="grid overflow-hidden rounded-[2rem] border border-zinc-200 bg-white shadow-sm dark:border-white/10 dark:bg-panel lg:grid-cols-2">
        <div className="relative min-h-[430px] overflow-hidden"><img src="https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=1200&q=88" alt="Complete guitar bundle" className="absolute inset-0 h-full w-full object-cover transition duration-1000 hover:scale-105" /><span className="absolute left-6 top-6 rounded-full bg-white px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-zinc-950">Save ₱3,500</span></div>
        <div className="flex flex-col justify-center p-8 sm:p-12 lg:p-16"><p className="section-label">Complete starter rig</p><h2 className="mt-3 font-display text-4xl font-semibold">Everything after the guitar.</h2><p className="mt-4 leading-7 text-zinc-500">A matched practice amp, padded bag, cable, tuner, strap, picks, and a professional setup—ready from day one.</p><div className="mt-7 grid grid-cols-2 gap-3 text-sm">{['15W practice amp', 'Padded gig bag', 'Clip-on tuner', 'Cable + strap', 'Assorted picks', 'Free setup'].map((item) => <div key={item} className="flex items-center gap-2"><Check size={14} className="text-emerald-500" /> {item}</div>)}</div><div className="mt-8 flex items-end gap-3"><span className="font-display text-3xl font-semibold">₱19,990</span><span className="pb-1 text-sm text-zinc-500 line-through">₱23,490</span></div><button className="primary-btn mt-7 self-start">View the bundle <ArrowRight size={17} /></button></div>
      </Reveal>
    </section>
  )
}

function OrderTracking() {
  const [order, setOrder] = useState('')
  const [tracked, setTracked] = useState(false)
  const steps = [[PackageCheck, 'Processing'], [Truck, 'Shipped'], [ArrowRight, 'Out for delivery'], [Check, 'Delivered']]
  return (
    <section id="track" className="border-y border-zinc-200 bg-zinc-100 py-24 dark:border-white/10 dark:bg-white/[.02]">
      <Reveal className="shell grid gap-12 lg:grid-cols-[.72fr_1.28fr] lg:items-center">
        <div><p className="section-label">Delivery updates</p><h2 className="section-title">Know where it is.</h2><p className="mt-4 leading-7 text-zinc-500">Enter your order number to see its current status and estimated delivery.</p><div className="input-shell mt-7 max-w-md p-1.5 pl-5"><Search size={16} /><input value={order} onChange={(e) => setOrder(e.target.value)} placeholder="AUD-24018" className="min-w-0 flex-1 bg-transparent py-2 text-sm outline-none" /><button onClick={() => setTracked(Boolean(order))} className="rounded-full bg-zinc-950 px-5 py-2.5 text-xs font-bold text-white dark:bg-white dark:text-zinc-950">Track</button></div></div>
        <div className="surface-card p-6 sm:p-8"><div className="flex items-center justify-between"><div><p className="text-xs text-zinc-500">Order</p><p className="mt-1 font-semibold">{tracked ? order.toUpperCase() : 'AUD-24018'}</p></div><span className="rounded-full bg-blue-100 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-blue-700 dark:bg-blue-400/10 dark:text-blue-300">In transit</span></div><div className="mt-10 grid grid-cols-4">{steps.map(([Icon, label], index) => <div key={label} className="relative text-center"><div className={`relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border ${index < 2 ? 'border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid dark:text-ink' : 'border-zinc-200 bg-white text-zinc-400 dark:border-white/10 dark:bg-panel'}`}><Icon size={15} /></div>{index < 3 && <div className={`absolute left-1/2 top-5 h-px w-full ${index < 2 ? 'bg-zinc-950 dark:bg-acid' : 'bg-zinc-200 dark:bg-white/10'}`} />}<p className="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">{label}</p></div>)}</div><div className="mt-7 flex justify-between border-t border-zinc-200 pt-5 text-xs dark:border-white/10"><span className="text-zinc-500">Estimated arrival</span><span className="font-semibold">Thursday, Sep 10</span></div></div>
      </Reveal>
    </section>
  )
}

function CartDrawer({ open, onClose, cart, setCart }) {
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0)
  const update = (id, delta) => setCart(cart.map((item) => item.id === id ? { ...item, qty: Math.max(0, item.qty + delta) } : item).filter((item) => item.qty > 0))
  return <AnimatePresence>{open && <div className="fixed inset-0 z-50"><motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} className="absolute inset-0 bg-black/55 backdrop-blur-sm" aria-label="Close cart" /><motion.aside initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'spring', stiffness: 300, damping: 32 }} className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-[#101014]"><div className="flex items-center justify-between border-b border-zinc-200 px-6 py-5 dark:border-white/10"><div className="flex items-center gap-3"><ShoppingBag size={19} /><h2 className="font-display text-xl font-semibold">Your cart</h2><span className="text-xs text-zinc-500">{cart.reduce((s, p) => s + p.qty, 0)} items</span></div><button onClick={onClose} className="icon-btn"><X size={18} /></button></div><div className="flex-1 overflow-y-auto p-6">{cart.length ? <div className="space-y-5">{cart.map((item) => <div key={item.id} className="flex gap-4"><img src={item.image} alt="" className="h-24 w-20 rounded-xl object-cover" /><div className="flex min-w-0 flex-1 flex-col"><p className="text-[10px] uppercase tracking-widest text-zinc-500">{item.brand}</p><p className="mt-1 truncate text-sm font-semibold">{item.name}</p><div className="mt-auto flex items-center justify-between"><span className="text-sm font-semibold">{peso(item.price)}</span><div className="flex items-center gap-3 rounded-full border border-zinc-200 px-2 py-1 dark:border-white/10"><button onClick={() => update(item.id, -1)}><Minus size={13} /></button><span className="text-xs">{item.qty}</span><button onClick={() => update(item.id, 1)}><Plus size={13} /></button></div></div></div></div>)}</div> : <div className="grid h-full place-items-center text-center"><div><ShoppingBag size={36} className="mx-auto text-zinc-300 dark:text-zinc-700" /><p className="mt-4 text-sm text-zinc-500">Your cart is empty.</p></div></div>}</div>{cart.length > 0 && <div className="border-t border-zinc-200 p-6 dark:border-white/10"><div className="flex justify-between"><span className="text-sm text-zinc-500">Subtotal</span><span className="font-display text-xl font-semibold">{peso(total)}</span></div><button className="primary-btn mt-5 w-full">Proceed to checkout <ShieldCheck size={16} /></button></div>}</motion.aside></div>}</AnimatePresence>
}

function FinderModal({ open, onClose, products, onAdd }) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({ budget: 20000, level: 'Beginner', genre: 'Rock', category: 'Electric' })
  const [results, setResults] = useState([])
  useEffect(() => { if (!open) { setStep(0); setResults([]) } }, [open])
  const questions = [
    { key: 'budget', title: 'What is your budget?' },
    { key: 'level', title: 'What is your experience level?', options: ['Beginner', 'Intermediate', 'Advanced'] },
    { key: 'genre', title: 'What do you want to play?', options: ['Rock', 'Pop', 'Blues', 'Jazz', 'Classical'] },
    { key: 'category', title: 'Which guitar type do you prefer?', options: ['Electric', 'Acoustic', 'Classical', 'Bass'] },
  ]
  const finish = async () => {
    try { const response = await fetch('/api/finder', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(answers) }); const data = await response.json(); setResults(data.recommendations || []) }
    catch { setResults(products.filter((p) => p.category === answers.category).sort((a, b) => Math.abs(a.price - answers.budget) - Math.abs(b.price - answers.budget)).slice(0, 2)) }
    setStep(4)
  }
  return <AnimatePresence>{open && <div className="fixed inset-0 z-[60] grid place-items-center p-4"><motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} className="absolute inset-0 bg-black/65 backdrop-blur-md" aria-label="Close finder" /><motion.div initial={{ opacity: 0, y: 28, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 18 }} className="relative w-full max-w-2xl overflow-hidden rounded-[2rem] bg-white shadow-2xl dark:bg-panel"><div className="flex items-center justify-between border-b border-zinc-200 p-6 dark:border-white/10"><div className="flex items-center gap-3"><Compass size={20} /><div><p className="font-display font-semibold">AUDIA Guitar Finder</p><p className="text-[10px] text-zinc-500">Four quick questions</p></div></div><button onClick={onClose} className="icon-btn"><X size={18} /></button></div>{step < 4 ? <div className="p-7 sm:p-10"><div className="mb-8 flex gap-2">{questions.map((_, i) => <span key={i} className={`h-1 flex-1 rounded-full ${i <= step ? 'bg-zinc-950 dark:bg-acid' : 'bg-zinc-200 dark:bg-white/10'}`} />)}</div><p className="section-label">Question {step + 1} of 4</p><h2 className="mt-3 font-display text-3xl font-semibold">{questions[step].title}</h2>{step === 0 ? <div className="mt-10"><div className="mb-7 text-center font-display text-4xl font-semibold">{peso(answers.budget)}</div><input type="range" min="8000" max="60000" step="1000" value={answers.budget} onChange={(e) => setAnswers({ ...answers, budget: Number(e.target.value) })} className="range-acid w-full" /><div className="mt-3 flex justify-between text-xs text-zinc-500"><span>₱8,000</span><span>₱60,000</span></div></div> : <div className="mt-9 grid gap-3 sm:grid-cols-2">{questions[step].options.map((option) => <button key={option} onClick={() => setAnswers({ ...answers, [questions[step].key]: option })} className={`rounded-2xl border p-5 text-left text-sm transition ${answers[questions[step].key] === option ? 'border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid' : 'border-zinc-200 hover:border-zinc-400 dark:border-white/10'}`}>{option}{answers[questions[step].key] === option && <Check size={15} className="float-right" />}</button>)}</div>}<button onClick={() => step === 3 ? finish() : setStep(step + 1)} className="primary-btn mt-10 w-full">{step === 3 ? 'Show my matches' : 'Continue'} <ArrowRight size={16} /></button></div> : <div className="p-7 sm:p-10"><p className="section-label">Recommended for you</p><h2 className="mt-3 font-display text-3xl font-semibold">Your closest matches.</h2><div className="mt-7 space-y-3">{results.map((product, index) => <div key={product.id} className="flex items-center gap-4 rounded-2xl border border-zinc-200 p-3 dark:border-white/10"><div className="relative"><img src={product.image} alt="" className="h-20 w-16 rounded-xl object-cover" /><span className="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink">{index + 1}</span></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{product.name}</p><p className="mt-1 text-xs text-zinc-500">{product.category} · {product.level}</p><p className="mt-2 text-sm font-semibold">{peso(product.price)}</p></div><button onClick={() => { onAdd(product); onClose() }} className="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"><Plus size={16} /></button></div>)}</div><button onClick={() => setStep(0)} className="secondary-btn mt-6 w-full">Start again</button></div>}</motion.div></div>}</AnimatePresence>
}

function Assistant() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([{ role: 'guide', text: 'Hi, I’m AUDI. Tell me your budget or the kind of music you want to play, and I’ll help narrow the options.' }])
  const send = async (preset) => {
    const message = preset || input.trim(); if (!message) return
    setMessages((items) => [...items, { role: 'user', text: message }]); setInput('')
    try { const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) }); const data = await response.json(); setMessages((items) => [...items, { role: 'guide', text: data.reply }]) }
    catch { setMessages((items) => [...items, { role: 'guide', text: 'For a first guitar, comfort matters most. What is your preferred style and maximum budget?' }]) }
  }
  return <><button onClick={() => setOpen(!open)} className="fixed bottom-5 right-5 z-40 grid h-14 w-14 place-items-center rounded-full bg-zinc-950 text-white shadow-2xl transition hover:scale-105 dark:bg-acid dark:text-ink" aria-label="Open customer support">{open ? <X size={20} /> : <MessageCircle size={21} />}</button><AnimatePresence>{open && <motion.div initial={{ opacity: 0, y: 20, scale: .97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 16 }} className="fixed bottom-24 right-4 z-40 flex h-[510px] w-[calc(100%-2rem)] max-w-sm flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-white/10 dark:bg-[#101014]"><div className="flex items-center gap-3 border-b border-zinc-200 p-4 dark:border-white/10"><div className="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"><Headphones size={17} /></div><div><p className="font-display text-sm font-semibold">AUDI customer guide</p><p className="text-[10px] text-zinc-500">Available now</p></div></div><div className="flex-1 space-y-3 overflow-y-auto p-4">{messages.map((message, index) => <div key={index} className={`max-w-[86%] rounded-2xl px-4 py-3 text-xs leading-5 ${message.role === 'user' ? 'ml-auto bg-zinc-950 text-white dark:bg-acid dark:text-ink' : 'bg-zinc-100 dark:bg-white/[.07]'}`}>{message.text}</div>)}{messages.length === 1 && <div className="flex flex-wrap gap-2">{['Best guitar under ₱20k', 'I am a beginner', 'Acoustic or electric?'].map((suggestion) => <button key={suggestion} onClick={() => send(suggestion)} className="rounded-full border border-zinc-200 px-3 py-2 text-[10px] text-zinc-500 hover:border-zinc-500 dark:border-white/10">{suggestion}</button>)}</div>}</div><form onSubmit={(event) => { event.preventDefault(); send() }} className="flex gap-2 border-t border-zinc-200 p-3 dark:border-white/10"><input value={input} onChange={(e) => setInput(e.target.value)} className="min-w-0 flex-1 rounded-full bg-zinc-100 px-4 text-xs outline-none dark:bg-white/[.06]" placeholder="Ask about a guitar" /><button className="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"><ArrowRight size={16} /></button></form></motion.div>}</AnimatePresence></>
}

function Footer({ onAdmin }) {
  return <footer className="border-t border-zinc-200 bg-white pt-16 dark:border-white/10 dark:bg-ink"><div className="shell grid gap-12 pb-14 sm:grid-cols-2 lg:grid-cols-[1.4fr_repeat(3,1fr)]"><div><Logo onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} /><p className="mt-6 max-w-xs text-sm leading-6 text-zinc-500">A guitar-only marketplace helping players find, hear, compare, and purchase the right instrument.</p></div>{[['Shop', 'Electric guitars', 'Acoustic guitars', 'Bass guitars', 'Accessories'], ['Services', 'Guitar finder', 'Sound previews', 'Bundles', 'Professional setup'], ['Support', 'Order tracking', 'Delivery & returns', 'Warranty', 'Contact us']].map(([title, ...links]) => <div key={title}><h3 className="text-xs font-semibold uppercase tracking-[.18em]">{title}</h3><div className="mt-5 flex flex-col gap-3">{links.map((link) => <a key={link} href="#shop" className="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white">{link}</a>)}</div></div>)}</div><div className="border-t border-zinc-200 dark:border-white/10"><div className="shell flex flex-col justify-between gap-3 py-6 text-[11px] text-zinc-500 sm:flex-row"><span>© 2026 AUDIA Guitar Marketplace</span><button onClick={onAdmin} className="hover:text-zinc-950 dark:hover:text-white">Admin portal</button></div></div></footer>
}

export default function Storefront({ theme, setTheme, user, onAuth, onAdminLogin, onAdmin }) {
  const [products, setProducts] = useState(fallbackProducts)
  const [cart, setCart] = useState([])
  const [cartOpen, setCartOpen] = useState(false)
  const [finderOpen, setFinderOpen] = useState(false)
  const [filter, setFilter] = useState('All')
  const [search, setSearch] = useState('')
  useEffect(() => { fetch('/api/products').then((response) => response.json()).then((data) => data.products?.length && setProducts(data.products)).catch(() => {}) }, [])
  const addToCart = (product) => { setCart((current) => current.some((item) => item.id === product.id) ? current.map((item) => item.id === product.id ? { ...item, qty: item.qty + 1 } : item) : [...current, { ...product, qty: 1 }]); setCartOpen(true) }
  const chooseCategory = (category) => { setFilter(category); document.getElementById('shop')?.scrollIntoView({ behavior: 'smooth' }) }
  const focusSearch = () => { document.getElementById('shop')?.scrollIntoView({ behavior: 'smooth' }); setTimeout(() => document.querySelector('#shop input')?.focus(), 450) }
  return <div className="min-h-screen overflow-x-hidden"><Announcement /><Header cartCount={cart.reduce((sum, item) => sum + item.qty, 0)} onCart={() => setCartOpen(true)} onFinder={() => setFinderOpen(true)} onSearch={focusSearch} theme={theme} setTheme={setTheme} user={user} onAuth={onAuth} onAdmin={onAdmin} /><main><Hero onFinder={() => setFinderOpen(true)} /><Categories onSelect={chooseCategory} /><Shop products={products} onAdd={addToCart} filter={filter} setFilter={setFilter} search={search} setSearch={setSearch} /><FinderBanner onOpen={() => setFinderOpen(true)} /><Bundle /><OrderTracking /><div className="shell grid gap-4 py-14 sm:grid-cols-3">{[[ShieldCheck, 'Authentic gear', 'Official products with warranty'], [Volume2, 'Hear before buying', 'Tone previews on key models'], [Headphones, 'Player-first support', 'Help choosing and setting up']].map(([Icon, title, text]) => <Reveal key={title} className="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"><Icon size={20} /><div><p className="text-sm font-semibold">{title}</p><p className="mt-1 text-xs text-zinc-500">{text}</p></div></Reveal>)}</div></main><Footer onAdmin={onAdminLogin} /><CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} cart={cart} setCart={setCart} /><FinderModal open={finderOpen} onClose={() => setFinderOpen(false)} products={products} onAdd={addToCart} /><Assistant /></div>
}
