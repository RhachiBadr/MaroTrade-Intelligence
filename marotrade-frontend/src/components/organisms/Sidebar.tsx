'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  Search, 
  ShieldCheck, 
  TrendingUp, 
  History, 
  Settings,
  Globe
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { label: 'Market Analysis', icon: Search, href: '/analyze' },
  { label: 'Regulations', icon: ShieldCheck, href: '/regulations' },
  { label: 'Forecasts', icon: TrendingUp, href: '/forecast' },
  { label: 'History', icon: History, href: '#' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 h-screen bg-card border-r border-border fixed left-0 top-0 flex flex-col z-50 animate-fade-in shadow-[1px_0_40px_rgba(0,0,0,0.02)]">
      {/* Logo */}
      <div className="p-6 border-b border-border/60">
        <Link href="/" className="flex items-center gap-3 transition-transform hover:scale-[1.02] active:scale-95">
          <div className="w-9 h-9 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center shadow-sm shadow-primary/20">
            <Globe className="text-white w-5 h-5" />
          </div>
          <span className="font-extrabold text-xl text-text-primary tracking-tight">
            MaroTrade
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider mb-3 px-3">Menu Principal</div>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                isActive 
                  ? "bg-primary/10 text-primary shadow-[inset_0_1px_0_rgba(255,255,255,0.8)]" 
                  : "text-text-secondary hover:bg-secondary hover:text-text-primary"
              )}
            >
              <item.icon className={cn(
                "w-5 h-5 transition-transform duration-200 group-hover:scale-110", 
                isActive ? "text-primary" : "text-text-muted group-hover:text-text-primary"
              )} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-border/60 bg-card">
        <Link
          href="#"
          className="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-text-secondary hover:bg-secondary hover:text-text-primary transition-all duration-200"
        >
          <Settings className="w-5 h-5 transition-transform duration-200 group-hover:scale-110 group-hover:rotate-45 text-text-muted group-hover:text-text-primary" />
          Settings
        </Link>
        
        <div className="mt-4 p-4 rounded-2xl bg-gradient-to-br from-secondary/80 to-secondary border border-border/50 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-50" />
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <p className="text-xs font-bold text-text-primary tracking-wide">MaroTrade Pro</p>
            </div>
            <p className="text-[11px] text-text-muted leading-relaxed mb-3">Accédez à l'IA avancée et aux prévisions illimitées.</p>
            <button className="w-full py-2 bg-white shadow-sm border border-border rounded-xl text-xs font-semibold text-text-primary hover:text-primary hover:border-primary/30 transition-all duration-200 active:scale-95">
              Upgrade to Pro
            </button>
          </div>
        </div>
      </div>
    </aside>
  )
}
