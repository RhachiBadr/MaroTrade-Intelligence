'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAnalysisStore } from '@/store/analysis'
import { HS_CATALOGUE, searchHS } from '@/lib/hs-catalogue'
import { fetchScore } from '@/lib/api'
import { cn } from '@/lib/utils'
import { ChevronRight, ChevronLeft, Check, Search, Box, Globe, Shield, RefreshCw, BarChart, TrendingUp, ArrowRight } from 'lucide-react'

const PERIMETERS = [
  { id: 3, label: 'Top 3 marchés', desc: 'Précision maximale' },
  { id: 5, label: 'Top 5 marchés', desc: 'Recommandé' },
  { id: 10, label: 'Top 10 marchés', desc: 'Vue élargie' },
  { id: 0, label: 'Analyse globale', desc: 'Tous les marchés (plus lent)' },
]

export default function AnalyzePage() {
  const router = useRouter()
  const { setResults, setParams, addToHistory } = useAnalysisStore()

  const [step, setStep] = useState(1)
  const [product, setProduct] = useState('')
  const [hsCode, setHsCode] = useState('')
  const [sugg, setSugg] = useState<typeof HS_CATALOGUE>([])

  const [topN, setTopN] = useState<number>(5)
  const [criteria, setCriteria] = useState({ importVol: true, growth: true, regulations: false, culture: false })

  const [loading, setLoading] = useState(false)

  // Step 1 Functions
  function handleProduct(val: string) {
    setProduct(val)
    setSugg(val.length >= 2 ? searchHS(val) : [])
  }
  function pickSugg(label: string, hs: string) {
    setProduct(label.replace(/^[^ ]+ /, ''))
    setHsCode(hs)
    setSugg([])
  }

  // Submit
  async function handleSubmit() {
    setLoading(true)
    try {
      const perimN = topN === 0 ? 50 : topN // 50 mock for global
      const r = await fetchScore({ hs_code: hsCode || '151590', product_name: product, top_n: perimN })
      const analysisParams = { product_name: product, hs_code: hsCode || '151590', top_n: perimN }
      setParams(analysisParams)
      setResults(r)
      addToHistory({ params: analysisParams, results: r, topScore: r[0]?.ai_score || 0 })
      router.push('/results')
    } catch {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary tracking-tight">Nouvelle analyse de marché</h1>
        <p className="text-sm text-text-muted mt-1">Configurez les paramètres pour identifier les meilleures opportunités d&apos;export.</p>
      </div>

      {/* Stepper Header */}
      <div className="bg-surface border border-border rounded-lg p-6 shadow-sm overflow-hidden text-center relative">
        <div className="flex items-center justify-between mx-auto max-w-xl relative">
          {/* Connecting Line */}
          <div className="absolute top-4 left-4 right-4 h-[2px] bg-border -z-10" />
          <div className="absolute top-4 left-4 h-[2px] bg-primary-600 -z-10 transition-all duration-500" style={{ width: step === 1 ? '0%' : step === 2 ? '50%' : '100%' }} />

          {[
            { num: 1, title: 'Produit' },
            { num: 2, title: 'Périmètre' },
            { num: 3, title: 'Confirmation' }
          ].map((s) => {
            const active = step >= s.num
            const current = step === s.num
            return (
              <div key={s.num} className="flex flex-col items-center gap-2 bg-surface px-2">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors border-2",
                  active ? "bg-primary-600 text-white border-primary-600" : "bg-background text-text-muted border-border",
                  current && "ring-4 ring-primary-100 dark:ring-primary-900/30"
                )}>
                  {step > s.num ? <Check className="w-4 h-4" /> : s.num}
                </div>
                <span className={cn("text-xs font-semibold uppercase tracking-wider", active ? "text-primary-600" : "text-text-muted")}>
                  {s.title}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Forms Content */}
      <div className="bg-surface border border-border rounded-lg shadow-sm p-6 lg:p-8 min-h-[400px] flex flex-col relative">

        {loading ? (
          /* Loading State skeleton */
          <div className="flex-1 flex flex-col items-center justify-center space-y-6 py-12 animate-in fade-in zoom-in-95 duration-500">
            <div className="w-16 h-16 bg-surface rounded-2xl shadow-lg border border-border flex items-center justify-center">
              <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
            </div>
            <div className="text-center space-y-2">
              <h3 className="text-lg font-bold text-text-primary">Génération en cours...</h3>
              <p className="text-sm text-text-muted">L&apos;IA analyse des millions de flux douaniers mondiaux.</p>
            </div>
            <div className="w-64 space-y-3">
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary-600 w-1/2 animate-shimmer" style={{ backgroundSize: '200% 100%', backgroundImage: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)' }} />
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* STEP 1: Produit */}
            {step === 1 && (
              <div className="flex-1 space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
                <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2"><Box className="w-5 h-5 text-text-muted" /> Définition du produit</h2>

                <div className="space-y-4">
                  <div className="relative group z-20">
                    <label className="block text-sm font-semibold text-text-primary mb-1.5">Quel produit exportez-vous ?</label>
                    <div className="relative flex items-center relative">
                      <Search className="w-4 h-4 text-text-muted absolute left-3" />
                      <input
                        type="text" autoFocus value={product} onChange={e => handleProduct(e.target.value)}
                        placeholder="Ex: Huile d'Argan, Safran..."
                        className="w-full bg-background border border-border rounded-md pl-9 pr-4 py-2.5 text-sm text-text-primary font-medium focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all"
                      />
                    </div>
                    {sugg.length > 0 && (
                      <ul className="absolute top-full left-0 right-0 mt-1 bg-surface border border-border rounded-md shadow-lg max-h-60 overflow-y-auto no-scrollbar">
                        {sugg.map((s, i) => (
                          <li key={i}>
                            <button onClick={() => pickSugg(s.label, s.hs_code)} className="w-full flex items-center justify-between px-4 py-2 hover:bg-background text-left transition-colors">
                              <span className="text-sm font-semibold text-text-primary">{s.label}</span>
                              <span className="text-[10px] bg-secondary text-text-secondary px-2 py-0.5 rounded font-bold uppercase">HS {s.hs_code}</span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div className="z-10">
                    <label className="flex items-center justify-between text-sm font-semibold text-text-primary mb-1.5">
                      Code Douanier (HS Code)
                      <span className="text-[10px] font-bold bg-background text-text-muted px-2 py-0.5 rounded-full uppercase tracking-wider">Facultatif</span>
                    </label>
                    <input
                      type="text" value={hsCode} onChange={e => setHsCode(e.target.value)}
                      placeholder="Ex: 151590"
                      className="w-full bg-background border border-border rounded-md px-4 py-2.5 text-sm text-text-primary font-mono focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* STEP 2: Périmètre */}
            {step === 2 && (
              <div className="flex-1 space-y-8 animate-in slide-in-from-right-4 fade-in duration-300">
                <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2"><Globe className="w-5 h-5 text-text-muted" /> Périmètre & Critères</h2>

                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-3">Sélectionnez la portée de l&apos;analyse</label>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    {PERIMETERS.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => setTopN(p.id)}
                        className={cn(
                          "p-4 rounded-lg border text-left transition-all",
                          topN === p.id ? "bg-primary-50 border-primary-600 dark:bg-primary-900/20" : "bg-background border-border hover:border-text-muted"
                        )}
                      >
                        <p className={cn("text-sm font-bold", topN === p.id ? "text-primary-600" : "text-text-primary")}>{p.label}</p>
                        <p className={cn("text-[10px] mt-1 font-medium", topN === p.id ? "text-primary-700 dark:text-primary-500" : "text-text-muted")}>{p.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-3">Critères de pondération</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {[
                      { key: 'importVol', label: "Volume d'importation", icon: BarChart },
                      { key: 'growth', label: "Croissance du marché", icon: TrendingUp },
                      { key: 'regulations', label: "Barrières douanières", icon: Shield },
                      { key: 'culture', label: "Proximité culturelle", icon: Globe },
                    ].map((c) => (
                      <label key={c.key} className={cn("flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors", criteria[c.key as keyof typeof criteria] ? 'bg-background border-border' : 'bg-surface border-border opacity-60 hover:opacity-100')}>
                        <input type="checkbox" checked={criteria[c.key as keyof typeof criteria]} onChange={(e) => setCriteria({ ...criteria, [c.key]: e.target.checked })} className="w-4 h-4 text-primary-600 rounded border-border focus:ring-primary-600 accent-primary-600" />
                        <span className="text-sm font-semibold text-text-primary flex items-center gap-2"><c.icon className="w-4 h-4 text-text-muted" /> {c.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* STEP 3: Confirmation */}
            {step === 3 && (
              <div className="flex-1 space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
                <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2"><Check className="w-5 h-5 text-success" /> Résumé de l&apos;analyse</h2>

                <div className="bg-background border border-border rounded-lg p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Produit</p>
                      <p className="text-sm font-bold text-text-primary mt-1">{product || 'Non spécifié'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">HS Code (Optionnel)</p>
                      <p className="text-sm font-mono font-bold text-text-primary mt-1">{hsCode || 'Auto'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Portée globale</p>
                      <p className="text-sm font-bold text-text-primary mt-1">{topN === 0 ? 'Tous les marchés' : `Top ${topN}`}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Estimation</p>
                      <p className="text-sm font-bold text-text-primary mt-1">~{topN === 0 ? '45' : '12'} secondes</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Footer Navigation */}
            <div className="mt-auto pt-6 flex items-center justify-between border-t border-border">
              <button
                onClick={() => setStep(step - 1)}
                disabled={step === 1}
                className={cn("px-4 py-2 rounded-md text-sm font-semibold transition-colors flex items-center gap-2", step === 1 ? "opacity-0 pointer-events-none" : "text-text-secondary hover:text-text-primary hover:bg-background")}
              >
                <ChevronLeft className="w-4 h-4" /> Retour
              </button>

              {step < 3 ? (
                <button
                  onClick={() => setStep(step + 1)}
                  disabled={step === 1 && !product}
                  className="px-6 py-2 bg-text-primary text-surface hover:bg-text-secondary rounded-md text-sm font-semibold transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  Suivant <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md text-sm font-semibold transition-colors shadow-sm flex items-center gap-2 active:scale-95"
                >
                  Générer l&apos;analyse <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
