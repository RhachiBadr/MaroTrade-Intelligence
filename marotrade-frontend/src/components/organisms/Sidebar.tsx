'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { LayoutDashboard, Search, ShieldCheck, TrendingUp, History, Sparkles, BarChart3, Settings, CreditCard, LogOut, Building2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useShell } from '@/components/shell/shell-context'
import { useState, type KeyboardEvent } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { useI18n } from '@/lib/i18n'
import { LanguageSwitcher } from '@/components/i18n/LanguageSwitcher'
import { BrandLogo } from '@/components/brand/BrandLogo'

const NAV_ITEMS = [
  { key: 'nav.dashboard', icon: LayoutDashboard, href: '/dashboard' }, { key: 'nav.analytics', icon: BarChart3, href: '/analytics' },
  { key: 'nav.marketAnalysis', icon: Search, href: '/analyze' }, { key: 'nav.regulations', icon: ShieldCheck, href: '/regulations' },
  { key: 'nav.forecasts', icon: TrendingUp, href: '/forecast' }, { key: 'nav.history', icon: History, href: '/history' },
]
const BOTTOM_ITEMS = [{ key: 'nav.pricing', icon: CreditCard, href: '/pricing' }, { key: 'nav.settings', icon: Settings, href: '/settings' }]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { mobileNavOpen, setMobileNavOpen } = useShell()
  const [fastAnalysis, setFastAnalysis] = useState('')
  const { account, logout } = useAuth()
  const { t } = useI18n()
  const closeMobile = () => setMobileNavOpen(false)
  function onQuickSearchKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key !== 'Enter' || !fastAnalysis.trim()) return
    closeMobile(); router.push('/analyze'); setFastAnalysis('')
  }
  const navLink = (item: typeof NAV_ITEMS[number]) => {
    const active = pathname === item.href
    return <Link key={item.href} href={item.href} onClick={closeMobile} className={cn('group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200', active ? 'bg-primary-500/15 text-primary-300 shadow-sm' : 'text-text-secondary hover:bg-white/5 hover:text-text-primary')}>
      <item.icon className={cn('h-4 w-4 shrink-0', active ? 'text-primary-400' : 'text-text-muted')} aria-hidden />{t(item.key)}
    </Link>
  }
  return (
    <aside className={cn('fixed inset-y-0 left-0 z-50 flex w-[min(17rem,88vw)] flex-col glass-strong transition-transform duration-300 ease-out lg:w-64', mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0')}>
      <div className="flex h-16 shrink-0 items-center gap-3 border-b border-border px-5">
        <BrandLogo size="sm" priority />
        <div><span className="block text-sm font-semibold text-text-primary">MaroTrade</span><span className="text-[10px] uppercase text-text-muted">Intelligence</span></div>
      </div>
      <div className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-5">
        <nav className="flex flex-col gap-0.5" aria-label={t('nav.mainNavigation')}>{NAV_ITEMS.map(navLink)}</nav>
        <div className="px-1"><label htmlFor="quick-search" className="mb-2 block text-xs font-medium text-text-muted">{t('nav.quickAccess')}</label>
          <div className="relative"><Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
            <input id="quick-search" type="search" placeholder={t('nav.quickPlaceholder')} value={fastAnalysis} onChange={e => setFastAnalysis(e.target.value)} onKeyDown={onQuickSearchKeyDown}
              className="w-full rounded-xl border border-border bg-surface-elevated py-2.5 pl-9 pr-3 text-xs text-text-primary placeholder:text-text-muted focus:outline-none" />
          </div>
        </div>
      </div>
      <div className="mt-auto space-y-2 border-t border-border p-3">
        <div className="rounded-xl border border-border bg-surface-elevated p-3"><div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-500/15 text-primary-400"><Building2 className="h-4 w-4" /></span>
          <div className="min-w-0 flex-1"><p className="truncate text-xs font-semibold text-text-primary">{account?.organization.name}</p><p className="truncate text-[10px] text-text-muted">{account?.user.email}</p></div>
        </div></div>
        <nav className="flex flex-col gap-0.5">{BOTTOM_ITEMS.map(navLink)}</nav>
        <div className="rounded-xl border border-primary-500/20 bg-primary-500/5 p-3"><div className="flex items-center gap-2 text-text-primary"><Sparkles className="h-4 w-4 text-primary-400" /><span className="text-xs font-semibold">MaroTrade Pro</span></div><p className="mt-1 text-[11px] text-text-muted">{t('nav.proDescription')}</p></div>
        <LanguageSwitcher className="w-full justify-center" />
        <button type="button" onClick={async () => { await logout(); router.replace('/login') }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-text-muted hover:bg-danger-500/10 hover:text-danger-500"><LogOut className="h-4 w-4" />{t('nav.logout')}</button>
      </div>
    </aside>
  )
}
