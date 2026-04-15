'use client'
import { Bell, Search, Plus, ChevronRight } from 'lucide-react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'

function getBreadcrumb(pathname: string) {
  if (pathname === '/') return 'Dashboard'
  if (pathname === '/analyze') return 'Nouvelle Analyse'
  if (pathname === '/regulations') return 'Réglementations'
  if (pathname === '/forecast') return 'Prévisions'
  return pathname.split('/').pop() || 'Dashboard'
}

export default function Header() {
  const pathname = usePathname()
  const currentPage = getBreadcrumb(pathname)

  return (
    <header className="fixed top-0 right-0 left-60 h-16 bg-surface/80 backdrop-blur-md border-b border-border z-40 flex items-center justify-between px-6 transition-all duration-200">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-text-muted font-medium">
        <span>MaroTrade Intelligence</span>
        <ChevronRight className="w-4 h-4 text-border" />
        <span className="text-text-primary font-semibold">{currentPage}</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        {/* Global Search */}
        <div className="relative hidden md:block w-64 group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted group-focus-within:text-primary-600 transition-colors" />
          <input
            type="text"
            placeholder="Rechercher..."
            className="w-full bg-background border border-border rounded-md pl-9 pr-12 py-1.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center">
            <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded bg-surface border border-border px-1.5 font-mono text-[10px] font-medium text-text-muted">
              <span>⌘</span>K
            </kbd>
          </div>
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-text-muted hover:text-text-primary hover:bg-background rounded-md transition-all group">
          <Bell className="w-5 h-5 group-hover:rotate-12 transition-transform" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger-600 rounded-full border border-surface shadow-sm" />
        </button>

        {/* Primary CTA Outline */}
        <Link
          href="/analyze"
          className="flex items-center gap-2 px-3 py-1.5 border border-primary-600 text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-md text-sm font-medium transition-colors active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Nouvelle analyse</span>
        </Link>
      </div>
    </header>
  )
}
