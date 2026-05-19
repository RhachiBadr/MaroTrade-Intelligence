'use client'

import { Bell, Search, Plus, ChevronRight, Menu } from 'lucide-react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useShell } from '@/components/shell/shell-context'

function getBreadcrumb(pathname: string): string {
  const map: Record<string, string> = {
    '/dashboard': 'Tableau de bord',
    '/analytics': 'Analytics',
    '/': 'Accueil',
    '/analyze': 'Analyse',
    '/regulations': 'Réglementation',
    '/forecast': 'Prévisions',
    '/history': 'Historique',
    '/settings': 'Paramètres',
    '/pricing': 'Tarifs',
    '/results': 'Résultats',
  }
  if (pathname.startsWith('/results/')) return 'Détail marché'
  return map[pathname] ?? 'MaroTrade'
}

export default function Header() {
  const pathname = usePathname()
  const currentPage = getBreadcrumb(pathname)
  const { toggleMobileNav } = useShell()

  return (
    <header className="fixed left-0 right-0 top-0 z-30 flex h-16 items-center justify-between gap-3 px-4 sm:px-6 lg:left-64">
      <div className="glass flex h-12 flex-1 items-center justify-between gap-3 rounded-2xl px-4">
        <div className="flex min-w-0 items-center gap-2">
          <button
            type="button"
            className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-text-secondary hover:bg-white/5 lg:hidden"
            onClick={toggleMobileNav}
            aria-label="Ouvrir le menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex min-w-0 items-center gap-2 text-xs font-medium text-text-muted sm:text-sm">
            <span className="hidden truncate sm:inline">MaroTrade</span>
            <ChevronRight className="hidden h-3.5 w-3.5 shrink-0 opacity-40 sm:block" />
            <span className="truncate font-semibold text-text-primary">{currentPage}</span>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <div className="relative hidden max-w-[200px] md:block md:max-w-xs">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
            <input
              type="search"
              placeholder="Rechercher…"
              className="h-9 w-full rounded-xl border border-border bg-surface-elevated py-1.5 pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:border-primary-500/50 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              aria-label="Recherche globale"
            />
          </div>

          <button
            type="button"
            className="relative hidden rounded-xl p-2 text-text-muted transition-colors hover:bg-white/5 hover:text-text-primary sm:inline-flex"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-danger-500 ring-2 ring-background" />
          </button>

          <Link
            href="/analyze"
            className="inline-flex h-9 items-center gap-1.5 rounded-xl bg-primary-600 px-3 text-sm font-semibold text-white shadow-lg shadow-primary-600/25 transition-all hover:bg-primary-500 sm:px-4"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Analyse</span>
          </Link>
        </div>
      </div>
    </header>
  )
}
