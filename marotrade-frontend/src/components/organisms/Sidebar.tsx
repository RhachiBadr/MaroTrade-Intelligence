'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Search, ShieldCheck, TrendingUp, History, Settings, Globe, MoreVertical, Moon, Sun, Plus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/app/providers'
import { useState } from 'react'

const NAV_ITEMS = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { label: 'Market Analysis', icon: Search, href: '/analyze' },
  { label: 'Regulations', icon: ShieldCheck, href: '/regulations' },
  { label: 'Forecasts', icon: TrendingUp, href: '/forecast' },
  { label: 'History', icon: History, href: '/history' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { theme, toggleTheme } = useTheme()
  const [fastAnalysis, setFastAnalysis] = useState('')

  return (
    <aside className="w-60 h-screen fixed left-0 top-0 flex flex-col z-50 bg-surface border-r border-border transition-all duration-200">
      {/* Brand */}
      <div className="flex items-center gap-3 h-16 px-5 border-b border-border/50 shrinks-0">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white shrink-0">
          <Globe className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-base text-text-primary leading-tight tracking-tight">MaroTrade</span>
          <span className="text-[10px] font-semibold text-primary-600 bg-primary-50 px-1.5 py-0.5 rounded leading-none w-max">INTELLIGENCE</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-5 px-3 flex flex-col gap-8">
        {/* Navigation */}
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors border-l-2",
                  isActive
                    ? "bg-primary-50 dark:bg-primary-900/40 text-primary-600 border-primary-600"
                    : "text-text-secondary hover:text-text-primary hover:bg-background border-transparent"
                )}
              >
                <item.icon className={cn("w-4.5 h-4.5", isActive ? "text-primary-600" : "text-text-muted")} />
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* Analyse Rapide */}
        <div className="px-3">
          <label className="text-[11px] font-semibold text-text-muted uppercase tracking-wider mb-2 block">
            Analyse Rapide
          </label>
          <div className="relative flex items-center">
            <Search className="w-4 h-4 text-text-muted absolute left-2" />
            <input
              type="text"
              placeholder="Ex: Argan, Safran..."
              value={fastAnalysis}
              onChange={(e) => setFastAnalysis(e.target.value)}
              className="w-full bg-background border border-border rounded-md pl-8 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all"
            />
          </div>
        </div>
      </div>

      {/* Footer / Upgrade to Pro */}
      <div className="p-4 mt-auto border-t border-border flex flex-col gap-4 bg-surface">
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg p-4 text-white shadow-sm relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-16 h-16 bg-white/10 rounded-full blur-xl group-hover:bg-white/20 transition-colors" />
          <h4 className="text-sm font-bold flex items-center gap-2">MaroTrade Pro</h4>
          <p className="text-[10px] text-white/80 mt-1 mb-3">Débloquez l&apos;intégration API et les prévisions illimitées.</p>
          <button className="w-full py-1.5 bg-white text-primary-600 hover:bg-primary-50 rounded text-xs font-bold transition-colors shadow-sm">
            Upgrade to Pro
          </button>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[10px] font-semibold tracking-wider uppercase text-text-muted">Thème</span>
          <button
            onClick={toggleTheme}
            className="p-1.5 text-text-muted hover:text-text-primary hover:bg-border rounded-md transition-colors"
            title="Toggle Dark Mode"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </aside>
  )
}
