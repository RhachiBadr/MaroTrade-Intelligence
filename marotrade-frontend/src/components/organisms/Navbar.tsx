'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const NAV = [
  { href: '/',            label: 'Accueil'      },
  { href: '/analyze',     label: 'Analyser'     },
  { href: '/regulations', label: 'Réglementation' },
  { href: '/forecast',    label: 'Prévisions'   },
]

export function Navbar() {
  const pathname = usePathname()
  const [dark, setDark] = useState(false)
  const [open, setOpen] = useState(false)

  const toggleDark = () => {
    setDark((d) => {
      document.documentElement.classList.toggle('dark', !d)
      return !d
    })
  }

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-gray-950/80 border-b border-gray-100 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🇲🇦</span>
            <span className="font-display font-bold text-marine-900 dark:text-white text-lg">MaroTrade</span>
            <span className="hidden sm:inline text-xs font-medium text-export-500 bg-export-50 dark:bg-export-900/30 px-2 py-0.5 rounded-full">Intelligence</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV.map(({ href, label }) => (
              <Link key={href} href={href} className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                pathname === href
                  ? 'bg-marine-50 text-marine-900 dark:bg-marine-900/30 dark:text-marine-300'
                  : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
              )}>
                {label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-2">
            {/* Dark mode */}
            <button onClick={toggleDark} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Changer le thème">
              {dark ? '☀️' : '🌙'}
            </button>
            <Link href="/analyze" className="hidden md:inline-flex items-center gap-1 bg-marine-900 hover:bg-marine-500 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors">
              🔍 Analyser
            </Link>
            {/* Mobile */}
            <button onClick={() => setOpen(o => !o)} className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800">
              {open ? '✕' : '☰'}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {open && (
          <div className="md:hidden pb-4 space-y-1">
            {NAV.map(({ href, label }) => (
              <Link key={href} href={href} onClick={() => setOpen(false)} className={cn(
                'block px-4 py-2 rounded-lg text-sm font-medium',
                pathname === href ? 'bg-marine-50 text-marine-900' : 'text-gray-600 hover:bg-gray-100'
              )}>
                {label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}
