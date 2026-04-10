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
    <aside className="w-64 h-screen bg-white border-r border-border fixed left-0 top-0 flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Globe className="text-white w-5 h-5" />
          </div>
          <span className="font-bold text-lg text-text-primary tracking-tight">
            MaroTrade
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary/5 text-primary" 
                  : "text-text-secondary hover:bg-secondary hover:text-text-primary"
              )}
            >
              <item.icon className={cn("w-5 h-5", isActive ? "text-primary" : "text-text-muted")} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-border">
        <Link
          href="#"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-text-secondary hover:bg-secondary hover:text-text-primary transition-colors"
        >
          <Settings className="w-5 h-5 text-text-muted" />
          Settings
        </Link>
        
        <div className="mt-4 p-3 bg-secondary rounded-xl">
          <p className="text-xs font-semibold text-text-primary mb-1">MaroTrade Pro</p>
          <p className="text-[11px] text-text-muted mb-2">Accédez à l'IA avancée et aux prévisions illimitées.</p>
          <button className="w-full py-1.5 bg-white border border-border rounded-lg text-xs font-medium hover:bg-gray-50 transition-colors">
            Upgrade
          </button>
        </div>
      </div>
    </aside>
  )
}
