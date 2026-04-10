'use client'
import { Bell, Search, User } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 h-16 bg-white/80 backdrop-blur-md border-b border-border z-40 flex items-center justify-between px-8 ml-64">
      {/* Search Bar */}
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <input 
          type="text" 
          placeholder="Rechercher un marché, un code HS..." 
          className="w-full pl-10 pr-4 py-2 bg-secondary/50 border-none rounded-full text-sm focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-text-muted"
        />
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        <button className="p-2 text-text-secondary hover:bg-secondary rounded-full transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-danger rounded-full border-2 border-white" />
        </button>
        
        <div className="h-8 w-px bg-border mx-1" />
        
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-text-primary leading-none">Exportateur Maroc</p>
            <p className="text-[11px] text-text-muted mt-1">PME Artisanat</p>
          </div>
          <button className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center border border-border hover:border-primary/30 transition-colors">
            <User className="w-5 h-5 text-text-secondary" />
          </button>
        </div>

        <button className="hidden md:block px-4 py-2 bg-primary text-white text-sm font-semibold rounded-lg hover:bg-primary/90 transition-colors shadow-sm">
          Nouvelle Analyse
        </button>
      </div>
    </header>
  )
}
