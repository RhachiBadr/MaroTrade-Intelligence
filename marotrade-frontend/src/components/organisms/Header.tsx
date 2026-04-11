'use client'
import { Bell, Search, User, ChevronDown } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 h-16 bg-white/70 backdrop-blur-xl border-b border-white/20 z-40 flex items-center justify-between px-8 ml-64 transition-all duration-300 shadow-[0_1px_2px_rgba(0,0,0,0.02),0_4px_16px_rgba(0,0,0,0.02)]">
      {/* Search Bar */}
      <div className="flex-1 max-w-md relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-blue-400/20 rounded-full blur opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 -z-10" />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted transition-colors group-focus-within:text-primary" />
        <input 
          type="text" 
          placeholder="Rechercher un marché, un code HS..." 
          className="w-full pl-11 pr-4 py-2 mt-0.5 bg-secondary/60 border border-transparent rounded-full text-sm focus:bg-white focus:border-border/80 focus:shadow-glow transition-all outline-none placeholder:text-text-muted text-text-primary"
        />
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-5">
        <button className="p-2.5 text-text-secondary hover:bg-secondary/80 rounded-full transition-all duration-200 relative hover:scale-105 active:scale-95 group">
          <Bell className="w-5 h-5 group-hover:text-text-primary group-hover:rotate-12 transition-transform" />
          <span className="absolute top-2.5 right-3 w-2 h-2 bg-danger rounded-full border-2 border-white animate-pulse" />
        </button>
        
        <div className="h-8 w-px bg-border/60 mx-1" />
        
        <button className="flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50 group">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary/10 to-blue-500/10 flex items-center justify-center border border-primary/20 transition-transform group-hover:scale-105">
            <User className="w-4 h-4 text-primary" />
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-sm font-bold text-text-primary leading-none tracking-tight">Exportateur Maroc</p>
            <p className="text-[11px] font-medium text-text-muted mt-1">PME Artisanat</p>
          </div>
          <ChevronDown className="w-4 h-4 text-text-muted ml-1 transition-transform group-hover:translate-y-0.5" />
        </button>

        <button className="hidden md:flex items-center gap-2 px-5 py-2.5 bg-primary text-white text-sm font-bold rounded-xl hover:bg-primary/90 transition-all duration-200 shadow-sm shadow-primary/25 hover:shadow-md hover:shadow-primary/30 active:scale-95 hover:-translate-y-0.5 ml-2">
          Nouvelle Analyse
        </button>
      </div>
    </header>
  )
}
