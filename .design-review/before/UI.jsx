import { motion, useReducedMotion } from 'framer-motion'
import { Moon, Sun } from 'lucide-react'

export const peso = (value) => new Intl.NumberFormat('en-PH', {
  style: 'currency', currency: 'PHP', maximumFractionDigits: 0,
}).format(value)

export function Logo({ onClick, size = 'default' }) {
  return (
    <button onClick={onClick} className={`audia-mark flex items-center text-left ${size === 'large' ? 'text-2xl' : 'text-lg'}`} aria-label="Go to AUDIA home">
      <span className="mark-a">A</span>UDI<span className="mark-a">A</span>
    </button>
  )
}

export function ThemeToggle({ theme, setTheme, compact = false }) {
  const isDark = theme === 'dark'
  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={`relative flex items-center rounded-full border border-zinc-200 bg-white text-zinc-700 shadow-sm transition hover:border-zinc-300 dark:border-white/10 dark:bg-white/[.05] dark:text-zinc-200 ${compact ? 'h-10 w-10 justify-center' : 'h-10 w-[74px] px-1'}`}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {compact ? (isDark ? <Sun size={17} /> : <Moon size={17} />) : (
        <>
          <motion.span animate={{ x: isDark ? 32 : 0 }} transition={{ type: 'spring', stiffness: 420, damping: 30 }} className="absolute grid h-8 w-8 place-items-center rounded-full bg-zinc-900 text-white shadow-md dark:bg-acid dark:text-ink">
            {isDark ? <Moon size={14} /> : <Sun size={14} />}
          </motion.span>
          <Sun size={13} className="ml-2" />
          <Moon size={13} className="ml-auto mr-2" />
        </>
      )}
    </button>
  )
}

export function Reveal({ children, className = '', delay = 0, y = 28 }) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y }}
      whileInView={reduce ? {} : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: .18 }}
      transition={{ duration: .7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}

export function StatusPill({ status }) {
  const styles = {
    Paid: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300',
    Processing: 'bg-blue-100 text-blue-700 dark:bg-blue-400/10 dark:text-blue-300',
    Pending: 'bg-amber-100 text-amber-700 dark:bg-amber-400/10 dark:text-amber-300',
    Refunded: 'bg-rose-100 text-rose-700 dark:bg-rose-400/10 dark:text-rose-300',
  }
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${styles[status] || styles.Pending}`}>{status}</span>
}
