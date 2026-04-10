'use client'
import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAnalysisStore } from '@/store/analysis'
import { HS_CATALOGUE, searchHS } from '@/lib/hs-catalogue'
import { MOCK_RESULTS } from '@/lib/mock-data'
import { fetchScore } from '@/lib/api'
import { cn } from '@/lib/utils'

const STEPS = [
  'Chargement des données commerciales…',
  'Construction de la matrice de features…',
  'Calcul du score pondéré multi-critères…',
  'Entraînement XGBoost & prédiction…',
  'Calcul SHAP — explications générées ✓',
]

function AnalyzeForm() {
  const router = useRouter()
  const params = useSearchParams()
  const { setResults, setParams } = useAnalysisStore()

  const [product, setProduct] = useState(params.get('product') ?? '')
  const [hsCode,  setHsCode]  = useState(params.get('hs') ?? '')
  const [topN,    setTopN]    = useState(5)
  const [loading, setLoading] = useState(false)
  const [step,    setStep]    = useState(0)
  const [suggestions, setSugg] = useState<typeof HS_CATALOGUE>([])

  function handleProductInput(v: string) {
    setProduct(v)
    setSugg(v.length >= 2 ? searchHS(v) : [])
  }

  function pickSuggestion(label: string, hs: string) {
    setProduct(label.replace(/^[^ ]+ /, ''))
    setHsCode(hs)
    setSugg([])
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!product) return
    setLoading(true)
    setStep(0)

    // Simulate pipeline steps
    for (let i = 0; i < STEPS.length; i++) {
      await new Promise(r => setTimeout(r, 700))
      setStep(i + 1)
    }

    // Use live API call
    try {
      const liveResults = await fetchScore({ hs_code: hsCode || '151590', product_name: product, top_n: topN })
      setParams({ product_name: product, hs_code: hsCode || '151590', top_n: topN })
      setResults(liveResults)
    } catch (err) {
      console.error(err)
    }

    await new Promise(r => setTimeout(r, 300))
    router.push('/results')
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-text-primary mb-4 tracking-tight">
          Lancer une <span className="text-primary">Analyse de Marché</span>
        </h1>
        <p className="text-lg text-text-secondary font-medium">
          Notre IA identifie et classe vos marchés d'export en moins de 60 secondes.
        </p>
      </div>

      <div className="relative">
        {!loading ? (
          <form onSubmit={handleSubmit} className="bg-white rounded-[2.5rem] border border-border shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-10 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Product */}
            <div className="relative group">
              <label className="block text-xs font-black text-text-muted uppercase tracking-widest mb-3 ml-1">
                Quel produit exportez-vous ? *
              </label>
              <div className="relative flex items-center bg-secondary/50 border border-border rounded-2xl p-1 focus-within:bg-white focus-within:border-primary/30 focus-within:ring-4 focus-within:ring-primary/5 transition-all">
                <input
                  type="text" required value={product}
                  onChange={e => handleProductInput(e.target.value)}
                  placeholder="ex : Huile d'Argan, Safran, Tapis..."
                  className="w-full px-5 py-4 bg-transparent outline-none text-text-primary font-medium"
                />
              </div>
              {suggestions.length > 0 && (
                <ul className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] border border-border z-50 overflow-hidden animate-in fade-in slide-in-from-top-2">
                  {suggestions.map(s => (
                    <li key={s.hs_code}>
                      <button type="button" onClick={() => pickSuggestion(s.label, s.hs_code)}
                        className="w-full flex justify-between items-center px-6 py-4 text-sm hover:bg-secondary text-left group transition-colors">
                        <span className="font-bold text-text-secondary group-hover:text-primary transition-colors">{s.label}</span>
                        <span className="text-[10px] font-black bg-secondary px-2 py-1 rounded text-text-muted uppercase tracking-widest">HS {s.hs_code}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* HS Code */}
            <div>
              <label className="block text-xs font-black text-text-muted uppercase tracking-widest mb-3 ml-1">
                Code Douanier (HS Code)
              </label>
              <div className="relative flex items-center bg-secondary/50 border border-border rounded-2xl p-1 focus-within:bg-white focus-within:border-primary/30 focus-within:ring-4 focus-within:ring-primary/5 transition-all">
                <input
                  type="text" value={hsCode} onChange={e => setHsCode(e.target.value)}
                  placeholder="ex : 151590"
                  className="w-full px-5 py-4 bg-transparent outline-none text-text-primary font-mono font-bold"
                />
                <div className="pr-4 text-[10px] font-black text-text-muted uppercase tracking-tighter opacity-50">Facultatif</div>
              </div>
            </div>

            {/* Top N */}
            <div>
              <div className="flex justify-between items-end mb-4 ml-1">
                <label className="text-xs font-black text-text-muted uppercase tracking-widest">
                  Périmètre de l'analyse
                </label>
                <span className="text-sm font-bold text-primary bg-primary/5 px-2 py-0.5 rounded-lg border border-primary/10">
                  Top {topN} marchés
                </span>
              </div>
              <div className="px-2">
                <input type="range" min={3} max={10} value={topN} onChange={e => setTopN(+e.target.value)}
                  className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary transition-all" />
                <div className="flex justify-between text-[10px] font-black text-text-muted mt-3 uppercase tracking-widest opacity-50">
                  <span>Précision cible</span><span>Vue globale</span>
                </div>
              </div>
            </div>

            <button type="submit"
              className="w-full bg-text-primary text-white font-bold py-5 rounded-[1.25rem] hover:scale-[1.02] active:scale-95 transition-all text-lg shadow-xl shadow-gray-200 flex items-center justify-center gap-3">
              Générer l'Analyse Stratégique
              <span className="text-white/50">→</span>
            </button>
          </form>
        ) : (
          /* Loading state */
          <div className="bg-white rounded-[2.5rem] border border-border shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-12 space-y-8 text-center animate-in zoom-in-95 duration-500">
            <div className="relative flex justify-center mb-4">
              <div className="w-20 h-20 rounded-full border-4 border-secondary border-t-primary animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold text-primary">{Math.round((step/STEPS.length)*100)}%</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-2xl font-extrabold text-text-primary tracking-tight">Analyse IA en cours</h2>
              <p className="text-text-muted text-sm font-medium italic">Traitement des flux douaniers mondiaux...</p>
            </div>

            <div className="bg-secondary/30 rounded-3xl p-6 space-y-4 max-w-sm mx-auto text-left">
              {STEPS.map((s, i) => (
                <div key={i} className={cn('flex items-center gap-4 transition-all duration-500', i < step ? 'text-success' : i === step - 1 ? 'text-primary scale-105' : 'text-text-muted/40')}>
                  <div className={cn('w-5 h-5 rounded-full flex items-center justify-center text-[10px] border-2 transition-colors', i < step ? 'bg-success/10 border-success' : i === step - 1 ? 'border-primary' : 'border-border')}>
                    {i < step ? '✓' : ''}
                  </div>
                  <span className={cn('text-xs font-bold tracking-tight', i === step - 1 && 'animate-pulse')}>{s}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decorative elements */}
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-primary/5 rounded-full blur-[80px] -z-10" />
        <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-success/5 rounded-full blur-[80px] -z-10" />
      </div>
    </div>
  )
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="w-10 h-10 rounded-full border-4 border-secondary border-t-primary animate-spin" /></div>}>
      <AnalyzeForm />
    </Suspense>
  )
}
