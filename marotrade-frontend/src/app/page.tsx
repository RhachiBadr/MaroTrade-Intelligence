'use client'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { HS_CATALOGUE, searchHS } from '@/lib/hs-catalogue'
import { Search, Globe, ShieldCheck, TrendingUp, ArrowRight, Sparkles } from 'lucide-react'
import { motion, AnimatePresence, Variants } from 'framer-motion'

const FEATURES = [
  { 
    icon: Globe, 
    title: 'Scoring IA de Marché', 
    desc: 'Analyse multicritère (XGBoost) sur 15 indicateurs clés pour classer vos opportunités avec précision.',
    gradient: 'from-blue-500/5 to-primary/5',
    iconBg: 'bg-primary shadow-primary/30',
    textColor: 'text-primary'
  },
  { 
    icon: ShieldCheck, 
    title: 'Veille Réglementaire', 
    desc: 'Analyse sémantique (Claude 3.5 Haiku) pointue des normes complexes EUR-Lex, RASFF et FDA.',
    gradient: 'from-emerald-500/5 to-emerald-600/5',
    iconBg: 'bg-success shadow-success/30',
    textColor: 'text-success'
  },
  { 
    icon: TrendingUp, 
    title: 'Prévisions Stratégiques', 
    desc: 'Modélisation avancée (Comet/Prophet) pour anticiper avec exactitude les tendances mondiales 2026.',
    gradient: 'from-purple-500/5 to-purple-600/5',
    iconBg: 'bg-purple-600 shadow-purple-600/30',
    textColor: 'text-purple-600'
  },
]

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    }
  }
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
}

export default function LandingPage() {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<typeof HS_CATALOGUE>([])
  const [isFocused, setIsFocused] = useState(false)

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
    <div className="max-w-[1040px] mx-auto py-16 px-4">
      {/* Hero Section */}
      <motion.section 
        className="mb-24 text-center sm:text-left flex flex-col items-center sm:items-start"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/5 border border-primary/10 mb-8 cursor-default group hover:bg-primary/10 transition-colors">
          <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          <span className="text-xs font-bold text-primary tracking-wide">La nouvelle référence de l'intelligence export</span>
        </motion.div>
        
        <motion.h1 variants={itemVariants} className="text-5xl lg:text-7xl font-extrabold text-text-primary mb-6 tracking-tight leading-[1.05]">
          Éclairez chaque marché <br className="hidden sm:block" />
          avec <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">l'intelligence artificielle</span>
        </motion.h1>
        
        <motion.p variants={itemVariants} className="text-lg lg:text-xl text-text-secondary max-w-2xl mb-12 leading-relaxed font-medium">
          La plateforme d'analyse stratégique ultime pour les entreprises marocaines. Identifiez vos meilleures opportunités, surmontez les barrières réglementaires et anticipez la demande.
        </motion.p>

        {/* Search Bar (Stripe Style) */}
        <motion.div variants={itemVariants} className="w-full max-w-3xl relative z-20">
          <form onSubmit={handleSubmit} className="relative group">
            <div className={`absolute -inset-1 bg-gradient-to-r from-primary to-blue-400 rounded-[2rem] blur-md transition-opacity duration-500 ${isFocused ? 'opacity-30' : 'opacity-0 group-hover:opacity-10'}`} />
            
            <div className={`relative flex flex-col sm:flex-row items-center bg-white border ${isFocused ? 'border-primary/50' : 'border-border'} rounded-[1.5rem] shadow-premium transition-all duration-300`}>
              <div className="pl-6 pr-3 py-4 hidden sm:block">
                <Search className={`w-6 h-6 transition-colors duration-300 ${isFocused ? 'text-primary' : 'text-text-muted'}`} />
              </div>
              <input
                type="text"
                value={query}
                onChange={e => handleInput(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setTimeout(() => setIsFocused(false), 200)}
                placeholder="Quel produit souhaitez-vous analyser ? (ex: Safran, Argan)"
                className="w-full sm:flex-1 py-4 px-6 sm:px-0 text-text-primary placeholder:text-text-muted bg-transparent outline-none text-lg font-medium"
              />
              <div className="p-2 w-full sm:w-auto">
                <button type="submit" className="w-full sm:w-auto bg-primary text-white font-bold px-8 py-3.5 rounded-xl hover:bg-blue-700 transition-all active:scale-[0.98] flex items-center justify-center gap-2 shadow-[0_2px_10px_rgba(0,102,255,0.3)]">
                  Analyser
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Suggestions Dropdown */}
            <AnimatePresence>
              {isFocused && suggestions.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.98 }}
                  transition={{ duration: 0.2 }}
                  className="absolute top-[calc(100%+12px)] left-0 right-0 bg-white border border-border/60 rounded-2xl shadow-premium overflow-hidden z-50 backdrop-blur-xl bg-white/90"
                >
                  <div className="p-2">
                    {suggestions.map((s, idx) => (
                      <button
                        key={`${s.hs_code}-${idx}`}
                        type="button"
                        onMouseDown={() => handleSelect(s.label, s.hs_code)}
                        className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm text-text-secondary hover:bg-secondary/80 hover:text-text-primary transition-all group"
                      >
                        <span className="font-medium group-hover:translate-x-1 transition-transform">{s.label}</span>
                        <span className="text-xs font-mono bg-secondary px-2 py-1.5 rounded-md text-text-muted group-hover:bg-white group-hover:shadow-sm transition-all border border-transparent group-hover:border-border/50">HS {s.hs_code}</span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </form>

          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-3 mt-6">
            <span className="text-xs font-bold text-text-muted uppercase tracking-widest mr-2">Produits Phares :</span>
            {HS_CATALOGUE.slice(0, 4).map((p) => (
              <button 
                key={`badge-${p.hs_code}`} 
                onClick={() => handleSelect(p.label, p.hs_code)}
                className="text-[13px] font-semibold text-text-secondary bg-white shadow-sm border border-border/80 px-4 py-1.5 rounded-full hover:border-primary/40 hover:text-primary hover:shadow-md transition-all active:scale-95"
              >
                {p.label}
              </button>
            ))}
          </div>
        </motion.div>
      </motion.section>

      {/* Features Grid */}
      <motion.section 
        className="grid lg:grid-cols-3 gap-6 mb-24"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={containerVariants}
      >
        {FEATURES.map((f, idx) => (
          <motion.div 
            key={f.title} 
            variants={itemVariants}
            className="relative bg-white border border-border/60 rounded-3xl p-8 hover:shadow-premium-hover hover:-translate-y-1 transition-all duration-300 group overflow-hidden z-10"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${f.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10`} />
            <div className="flex flex-col h-full">
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-8 shadow-lg ${f.iconBg} transform group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
                <f.icon className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-text-primary mb-3 tracking-tight group-hover:text-primary transition-colors">{f.title}</h3>
              <p className="text-text-secondary text-[15px] leading-relaxed font-medium">
                {f.desc}
              </p>
            </div>
          </motion.div>
        ))}
      </motion.section>

      {/* Social Proof / Stats */}
      <motion.section 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-card border border-border/60 rounded-[3rem] p-12 lg:p-20 text-center relative overflow-hidden shadow-premium"
      >
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(#0066FF 2px, transparent 0)', backgroundSize: '40px 40px' }} />
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-[100px] -mr-20 -mt-20 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-400/5 rounded-full blur-[100px] -ml-20 -mb-20 pointer-events-none" />
        </div>
        
        <div className="relative z-10">
          <h2 className="text-3xl lg:text-4xl font-extrabold text-text-primary mb-5 tracking-tight">
            Des données fiables pour une croissance fulgurante
          </h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto mb-16 font-medium">
            MaroTrade Intelligence agrège et filtre les sources les plus complexes pour garantir la précision absolue de vos stratégies d'expansion.
          </p>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-10">
            {[
              { label: 'Indicateurs IA', value: '15' },
              { label: 'Marchés analysés', value: '40+' },
              { label: 'Précisions Forecast', value: '94%' },
              { label: 'Mise à jour Data', value: '24h' },
            ].map((stat, idx) => (
              <motion.div 
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                className="flex flex-col items-center justify-center p-6 rounded-2xl bg-white/50 border border-border/30 backdrop-blur-sm"
              >
                <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-primary to-blue-500 mb-2">{stat.value}</div>
                <div className="text-xs font-bold text-text-secondary uppercase tracking-widest">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Final CTA */}
      <motion.section 
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="mt-24 text-center pb-12 relative"
      >
        <Link 
          href="/analyze" 
          className="group relative inline-flex items-center justify-center gap-3 bg-text-primary text-white font-bold px-12 py-5 rounded-2xl hover:bg-gray-800 transition-all duration-300 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] hover:shadow-[0_20px_50px_-15px_rgba(0,0,0,0.6)] hover:-translate-y-1 active:scale-[0.98]"
        >
          <span className="relative z-10 flex items-center gap-2">
            Lancer votre analyse gratuite
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </span>
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent opacity-0 group-hover:opacity-100 rounded-2xl transition-opacity duration-300" />
        </Link>
        <p className="mt-6 text-sm font-semibold text-text-muted flex items-center justify-center gap-2">
          <span>Aucun engagement</span>
          <span className="w-1 h-1 rounded-full bg-border" />
          <span>Rapports générés en moins de 60s</span>
        </p>
      </motion.section>
    </div>
  )
}
