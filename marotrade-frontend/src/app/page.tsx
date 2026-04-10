'use client'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { HS_CATALOGUE, searchHS } from '@/lib/hs-catalogue'
import { Search, Globe, ShieldCheck, TrendingUp, ArrowRight } from 'lucide-react'

const FEATURES = [
  { 
    icon: Globe, 
    title: 'Scoring IA de Marché', 
    desc: 'Analyse multicritère (XGBoost) sur 15 indicateurs clés pour classer vos opportunités.',
    color: 'bg-primary/10 text-primary'
  },
  { 
    icon: ShieldCheck, 
    title: 'Veille Réglementaire', 
    desc: 'Analyse sémantique (Claude 3.5 Haiku) des normes EUR-Lex, RASFF et FDA.',
    color: 'bg-green-50 text-success'
  },
  { 
    icon: TrendingUp, 
    title: 'Prévisions Stratégiques', 
    desc: 'Modélisation Comet/Prophet pour anticiper les tendances de consommation 2026.',
    color: 'bg-purple-50 text-purple-600'
  },
]

export default function LandingPage() {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<typeof HS_CATALOGUE>([])

  function handleInput(val: string) {
    setQuery(val)
    setSuggestions(val.length >= 2 ? searchHS(val) : [])
  }

  function handleSelect(label: string, hs: string) {
    router.push(`/analyze?product=${encodeURIComponent(label.replace(/^[^ ]+ /, ''))}&hs=${hs}`)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!query) return
    const match = searchHS(query)[0]
    if (match) handleSelect(match.label, match.hs_code)
    else router.push(`/analyze?product=${encodeURIComponent(query)}`)
  }

  return (
    <div className="max-w-6xl mx-auto py-12">
      {/* Hero Section */}
      <section className="mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/5 border border-primary/10 mb-6 group cursor-default">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs font-semibold text-primary uppercase tracking-wider">Solution d'Intelligence Export</span>
        </div>
        
        <h1 className="text-5xl lg:text-6xl font-extrabold text-text-primary mb-6 tracking-tight leading-[1.1]">
          Propulsez votre export avec<br />
          <span className="text-primary">l'intelligence artificielle</span>
        </h1>
        
        <p className="text-lg text-text-secondary max-w-2xl mb-10 leading-relaxed font-medium">
          Identifiez vos meilleurs marchés, anticipez les freins réglementaires et visualisez 
          les tendances de demain. Conçu pour les PME marocaines ambitieuses.
        </p>

        {/* Search Bar (Stripe Style) */}
        <form onSubmit={handleSubmit} className="relative max-w-2xl group">
          <div className="relative flex items-center bg-white border border-border rounded-2xl p-1.5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] group-focus-within:border-primary/30 group-focus-within:ring-4 group-focus-within:ring-primary/5 transition-all">
            <div className="pl-4 pr-2">
              <Search className="w-5 h-5 text-text-muted" />
            </div>
            <input
              type="text"
              value={query}
              onChange={e => handleInput(e.target.value)}
              placeholder="Quel produit souhaitez-vous exporter ? (ex: Safran, Huile d'Argan)"
              className="flex-1 py-3 text-text-primary placeholder:text-text-muted bg-transparent outline-none text-base"
            />
            <button type="submit" className="bg-primary text-white font-bold px-6 py-3 rounded-xl hover:bg-primary/90 transition-all flex items-center gap-2">
              Analyser
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-border rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-300">
              {suggestions.map((s) => (
                <button
                  key={s.hs_code}
                  type="button"
                  onClick={() => handleSelect(s.label, s.hs_code)}
                  className="w-full flex items-center justify-between px-5 py-4 text-sm text-text-secondary hover:bg-secondary hover:text-text-primary transition-colors border-b border-border/50 last:border-0"
                >
                  <span className="font-medium">{s.label}</span>
                  <span className="text-xs font-mono bg-secondary px-2 py-1 rounded text-text-muted uppercase">HS {s.hs_code}</span>
                </button>
              ))}
            </div>
          )}
        </form>

        <div className="flex flex-wrap items-center gap-3 mt-6">
          <span className="text-xs font-semibold text-text-muted uppercase tracking-widest mr-2">Suggestions :</span>
          {HS_CATALOGUE.slice(0, 4).map((p) => (
            <button 
              key={p.hs_code} 
              onClick={() => handleSelect(p.label, p.hs_code)}
              className="text-xs font-semibold text-text-secondary bg-white border border-border px-3 py-1.5 rounded-full hover:border-primary hover:text-primary transition-all"
            >
              {p.label}
            </button>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="grid md:grid-cols-3 gap-6 mb-16">
        {FEATURES.map((f) => (
          <div key={f.title} className="bg-white border border-border rounded-2xl p-8 hover:shadow-lg transition-all duration-300 group">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform ${f.color}`}>
              <f.icon className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-text-primary mb-3">{f.title}</h3>
            <p className="text-text-secondary text-sm leading-relaxed font-medium">
              {f.desc}
            </p>
          </div>
        ))}
      </section>

      {/* Social Proof / Stats */}
      <section className="bg-white border border-border rounded-[2.5rem] p-12 text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#2563EB 1px, transparent 0)', backgroundSize: '40px 40px' }} />
        
        <h2 className="text-3xl font-extrabold text-text-primary mb-4">
          La data au service de votre croissance
        </h2>
        <p className="text-text-secondary max-w-xl mx-auto mb-12 font-medium">
          MaroTrade Intelligence regroupe les sources les plus fiables pour garantir la précision de vos analyses stratégiques.
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { label: 'Indicateurs IA', value: '15' },
            { label: 'Marchés analysés', value: '40+' },
            { label: 'Précision Forecast', value: '94%' },
            { label: 'Mise à jour', value: '24h' },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-4xl font-black text-primary mb-1">{stat.value}</div>
              <div className="text-xs font-bold text-text-muted uppercase tracking-widest">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="mt-16 text-center">
        <Link 
          href="/analyze" 
          className="inline-flex items-center gap-3 bg-text-primary text-white font-bold px-10 py-5 rounded-2xl hover:scale-105 active:scale-95 transition-all shadow-xl shadow-gray-200"
        >
          Démarrer une analyse gratuite
          <ArrowRight className="w-5 h-5" />
        </Link>
        <p className="mt-6 text-sm font-medium text-text-muted">
          Pas d'abonnement requis · Analyse complète en 60s
        </p>
      </section>
    </div>
  )
}
