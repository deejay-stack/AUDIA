import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, ArrowRight, Check, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, UserRound } from 'lucide-react'
import { Logo, ThemeToggle } from './UI'

export default function AuthPage({ initialRole = 'customer', theme, setTheme, onBack, onLogin }) {
  const [role, setRole] = useState(initialRole)
  const [email, setEmail] = useState(initialRole === 'admin' ? 'admin@audia.ph' : 'user@audia.ph')
  const [password, setPassword] = useState(initialRole === 'admin' ? 'admin123' : 'audia123')
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(true)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const changeRole = (nextRole) => {
    setRole(nextRole); setError('')
    if (nextRole === 'admin') { setEmail('admin@audia.ph'); setPassword('admin123') }
    else { setEmail('user@audia.ph'); setPassword('audia123') }
  }

  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError('')
    try {
      const response = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password, role }) })
      if (!response.ok) throw new Error('Incorrect email or password.')
      const data = await response.json(); onLogin(data.user)
    } catch (requestError) {
      const demoIsValid = role === 'admin' ? email === 'admin@audia.ph' && password === 'admin123' : email.includes('@') && password.length >= 6
      if (demoIsValid) onLogin({ name: role === 'admin' ? 'AUDIA Admin' : 'Jay Player', email, role })
      else setError(requestError.message || 'Unable to sign in.')
    } finally { setLoading(false) }
  }

  return (
    <div className="grid min-h-screen bg-stone-50 dark:bg-ink lg:grid-cols-[1.03fr_.97fr]">
      <div className="relative hidden overflow-hidden bg-zinc-950 lg:block">
        <motion.img initial={{ scale: 1.08 }} animate={{ scale: 1 }} transition={{ duration: 1.3, ease: [0.22, 1, 0.36, 1] }} src="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1500&q=90" alt="Guitarist on stage" className="absolute inset-0 h-full w-full object-cover opacity-70" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/15 to-black/30" />
        <div className="relative flex h-full flex-col justify-between p-12 text-white xl:p-16">
          <Logo onClick={onBack} size="large" />
          <div className="max-w-xl"><p className="text-[10px] font-semibold uppercase tracking-[.2em] text-white/55">AUDIA member access</p><h1 className="mt-5 font-display text-5xl font-semibold leading-[1.03] tracking-[-.04em] xl:text-6xl">Your next guitar is closer than you think.</h1><p className="mt-6 max-w-lg leading-7 text-white/65">Save instruments, keep your Guitar Finder results, review purchases, and track every delivery from one account.</p><div className="mt-9 flex gap-7 text-xs text-white/65">{['Saved gear', 'Order history', 'Faster checkout'].map((item) => <span key={item} className="flex items-center gap-2"><Check size={14} className="text-acid" /> {item}</span>)}</div></div>
          <p className="text-xs text-white/40">AUDIA — Find Your Sound.</p>
        </div>
      </div>

      <div className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between p-5 sm:p-8"><button onClick={onBack} className="secondary-btn px-4 py-2.5"><ArrowLeft size={16} /> Back to store</button><ThemeToggle theme={theme} setTheme={setTheme} compact /></header>
        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 pb-14 sm:px-8">
          <div className="mb-9 lg:hidden"><Logo onClick={onBack} size="large" /></div>
          <motion.div key={role} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }}>
            <p className="section-label">Secure account access</p>
            <h1 className="mt-3 font-display text-4xl font-semibold tracking-tight">Welcome to AUDIA.</h1>
            <p className="mt-3 text-sm leading-6 text-zinc-500">Sign in to continue as a customer or open the store administration workspace.</p>
          </motion.div>

          <div className="mt-8 grid grid-cols-2 rounded-2xl bg-zinc-100 p-1.5 dark:bg-white/[.055]">
            <button onClick={() => changeRole('customer')} className={`flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition ${role === 'customer' ? 'bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white' : 'text-zinc-500'}`}><UserRound size={15} /> Customer</button>
            <button onClick={() => changeRole('admin')} className={`flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-xs font-semibold transition ${role === 'admin' ? 'bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white' : 'text-zinc-500'}`}><ShieldCheck size={15} /> Administrator</button>
          </div>

          <form onSubmit={submit} className="mt-7 space-y-5">
            <label className="block"><span className="mb-2 block text-xs font-semibold">Email address</span><span className="input-shell rounded-xl px-4"><Mail size={16} /><input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-transparent py-3.5 text-sm outline-none" /></span></label>
            <label className="block"><span className="mb-2 block text-xs font-semibold">Password</span><span className="input-shell rounded-xl px-4"><LockKeyhole size={16} /><input required type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-transparent py-3.5 text-sm outline-none" /><button type="button" onClick={() => setShowPassword(!showPassword)} className="text-zinc-500" aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></span></label>
            <div className="flex items-center justify-between text-xs"><label className="flex items-center gap-2 text-zinc-500"><input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="range-acid" /> Remember me</label><button type="button" className="font-semibold hover:underline">Forgot password?</button></div>
            {error && <p className="rounded-xl bg-rose-50 px-4 py-3 text-xs text-rose-600 dark:bg-rose-500/10 dark:text-rose-300">{error}</p>}
            <button disabled={loading} className="primary-btn w-full py-4">{loading ? 'Signing in…' : role === 'admin' ? 'Open dashboard' : 'Sign in'} <ArrowRight size={16} /></button>
          </form>

          <div className="mt-6 rounded-xl border border-zinc-200 px-4 py-3 text-xs text-zinc-500 dark:border-white/10"><span className="font-semibold text-zinc-700 dark:text-zinc-300">Demo access:</span> {role === 'admin' ? 'admin@audia.ph / admin123' : 'user@audia.ph / audia123'}</div>
          {role === 'customer' && <p className="mt-7 text-center text-xs text-zinc-500">New to AUDIA? <button className="font-semibold text-zinc-950 hover:underline dark:text-white">Create an account</button></p>}
        </div>
      </div>
    </div>
  )
}
