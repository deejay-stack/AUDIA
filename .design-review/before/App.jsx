import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Storefront from './components/Storefront'
import AuthPage from './components/AuthPage'
import AdminDashboard from './components/AdminDashboard'

export default function App() {
  const [screen, setScreen] = useState('store')
  const [user, setUser] = useState(null)
  const [authRole, setAuthRole] = useState('customer')
  const [theme, setTheme] = useState(() => localStorage.getItem('audia-theme') || 'dark')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('audia-theme', theme)
  }, [theme])

  const navigate = (next) => {
    setScreen(next)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleLogin = (account) => {
    setUser(account)
    navigate(account.role === 'admin' ? 'dashboard' : 'store')
  }

  return (
    <div className="min-h-screen bg-stone-50 text-zinc-950 transition-colors duration-300 dark:bg-ink dark:text-white">
      <AnimatePresence mode="wait">
        <motion.div key={screen} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: .25 }}>
          {screen === 'store' && <Storefront theme={theme} setTheme={setTheme} user={user} onAuth={() => { setAuthRole('customer'); navigate('auth') }} onAdminLogin={() => { setAuthRole('admin'); navigate('auth') }} onAdmin={() => navigate('dashboard')} />}
          {screen === 'auth' && <AuthPage initialRole={authRole} theme={theme} setTheme={setTheme} onBack={() => navigate('store')} onLogin={handleLogin} />}
          {screen === 'dashboard' && <AdminDashboard theme={theme} setTheme={setTheme} onStore={() => navigate('store')} onLogout={() => { setUser(null); navigate('store') }} />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
