'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  Search,
  ShieldCheck,
  TrendingUp,
  History,
  Globe,
  Sparkles,
  BarChart3,
  Settings,
  CreditCard,
  LogOut,
  Building2,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useShell } from '@/components/shell/shell-context'
import { useState, type KeyboardEvent } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'

const NAV_ITEMS = [
  { label: 'Tableau de bord', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'Analytics', icon: BarChart3, href: '/analytics' },
  { label: 'Analyse marchés', icon: Search, href: '/analyze' },
  { label: 'Réglementation', icon: ShieldCheck, href: '/regulations' },
  { label: 'Prévisions', icon: TrendingUp, href: '/forecast' },
  { label: 'Historique', icon: History, href: '/history' },
]

const BOTTOM_ITEMS = [
  { label: 'Tarifs', icon: CreditCard, href: '/pricing' },
  { label: 'Paramètres', icon: Settings, href: '/settings' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { mobileNavOpen, setMobileNavOpen } = useShell()
  const [fastAnalysis, setFastAnalysis] = useState('')
  const { account, logout } = useAuth()

  function closeMobile() {
    setMobileNavOpen(false)
  }

  function onQuickSearchKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key !== 'Enter' || !fastAnalysis.trim()) return
    closeMobile()
    router.push('/analyze')
    setFastAnalysis('')
  }

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-50 flex w-[min(17rem,88vw)] flex-col glass-strong transition-transform duration-300 ease-out lg:w-64',
        mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}
    >
      <div className="flex h-16 shrink-0 items-center gap-3 border-b border-border px-5">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-lg shadow-primary-600/30">
          <Globe className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex flex-col">
          <span className="truncate text-sm font-semibold text-text-primary leading-tight">MaroTrade</span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-text-muted">Intelligence</span>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-5">
        <nav className="flex flex-col gap-0.5" aria-label="Navigation principale">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={closeMobile}
                className={cn(
                  'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-primary-500/15 text-primary-300 shadow-sm'
                    : 'text-text-secondary hover:bg-white/5 hover:text-text-primary'
                )}
              >
                <item.icon
                  className={cn(
                    'h-4 w-4 shrink-0 transition-colors',
                    isActive ? 'text-primary-400' : 'text-text-muted group-hover:text-text-secondary'
                  )}
                  aria-hidden
                />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="px-1">
          <label htmlFor="quick-search" className="mb-2 block text-xs font-medium text-text-muted">
            Accès rapide
          </label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
            <input
              id="quick-search"
              type="search"
              placeholder="Produit, HS…"
              value={fastAnalysis}
              onChange={(e) => setFastAnalysis(e.target.value)}
              onKeyDown={onQuickSearchKeyDown}
              className="w-full rounded-xl border border-border bg-surface-elevated py-2.5 pl-9 pr-3 text-xs text-text-primary placeholder:text-text-muted focus:border-primary-500/50 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
        </div>
      </div>

      <div className="mt-auto space-y-2 border-t border-border p-3">
        <div className="rounded-xl border border-border bg-surface-elevated p-3">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-500/15 text-primary-400">
              <Building2 className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-text-primary">{account?.organization.name}</p>
              <p className="truncate text-[10px] text-text-muted">{account?.user.email}</p>
            </div>
          </div>
        </div>
        <nav className="flex flex-col gap-0.5">
          {BOTTOM_ITEMS.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={closeMobile}
                className={cn(
                  'flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'text-primary-300' : 'text-text-muted hover:text-text-secondary'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="rounded-xl border border-primary-500/20 bg-primary-500/5 p-3">
          <div className="flex items-center gap-2 text-text-primary">
            <Sparkles className="h-4 w-4 text-primary-400" />
            <span className="text-xs font-semibold">MaroTrade Pro</span>
          </div>
          <p className="mt-1 text-[11px] leading-snug text-text-muted">API et prévisions étendues.</p>
        </div>
        <button
          type="button"
          onClick={async () => {
            await logout()
            router.replace('/login')
          }}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-text-muted transition-colors hover:bg-danger-500/10 hover:text-danger-500"
        >
          <LogOut className="h-4 w-4" />
          Se déconnecter
        </button>
      </div>
    </aside>
  )
}
