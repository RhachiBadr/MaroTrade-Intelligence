'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAnalysisStore } from '@/store/analysis'
import { HS_CATALOGUE, searchHS } from '@/lib/hs-catalogue'
import { fetchScore } from '@/lib/api'
import { cn } from '@/lib/utils'
import {
  ChevronRight,
  ChevronLeft,
  Check,
  Search,
  Box,
  Globe,
  Shield,
  RefreshCw,
  BarChart,
  TrendingUp,
  ArrowRight,
} from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

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
  const [criteria, setCriteria] = useState({
    importVol: true,
    growth: true,
    regulations: false,
    culture: false,
  })

  const [loading, setLoading] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  function handleProduct(val: string) {
    setProduct(val)
    setSugg(val.length >= 2 ? searchHS(val) : [])
  }

  function pickSugg(label: string, hs: string) {
    setProduct(label.replace(/^[^ ]+ /, ''))
    setHsCode(hs)
    setSugg([])
  }

  async function handleSubmit() {
    setSubmitError(null)
    setLoading(true)
    try {
      const perimN = topN === 0 ? 50 : topN
      const r = await fetchScore({ hs_code: hsCode || '151590', product_name: product, top_n: perimN })
      const analysisParams = { product_name: product, hs_code: hsCode || '151590', top_n: perimN }
      setParams(analysisParams)
      setResults(r)
      addToHistory({ params: analysisParams, results: r, topScore: r[0]?.score_final ?? 0 })
      router.push('/results')
    } catch {
      setLoading(false)
      setSubmitError("Impossible de finaliser l'analyse. Vérifiez la connexion ou réessayez.")
    }
  }

  return (
    <PageContainer className="max-w-3xl space-y-6">
      <PageHeader
        title="Nouvelle analyse de marché"
        description="Définissez le produit et le périmètre pour classer les marchés les plus pertinents."
      />

      {submitError && (
        <div
          className="rounded-lg border border-danger-500/30 bg-danger-50 px-4 py-3 text-sm text-danger-700 dark:bg-danger-950/30 dark:text-danger-200"
          role="alert"
        >
          {submitError}
        </div>
      )}

      <Card className="overflow-hidden shadow-none">
        <CardContent className="p-6">
          <div className="relative mx-auto flex max-w-xl items-center justify-between text-center">
            <div className="absolute left-4 right-4 top-4 -z-10 h-0.5 bg-border" />
            <div
              className="absolute left-4 top-4 -z-10 h-0.5 bg-primary-600 transition-all duration-500"
              style={{ width: step === 1 ? '0%' : step === 2 ? '50%' : '100%' }}
            />
            {[
              { num: 1, title: 'Produit' },
              { num: 2, title: 'Périmètre' },
              { num: 3, title: 'Validation' },
            ].map((s) => {
              const active = step >= s.num
              const current = step === s.num
              return (
                <div key={s.num} className="flex flex-col items-center gap-2 bg-surface px-2">
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors',
                      active
                        ? 'border-primary-600 bg-primary-600 text-white'
                        : 'border-border bg-background text-text-muted',
                      current && 'ring-4 ring-primary-100 dark:ring-primary-900/30'
                    )}
                  >
                    {step > s.num ? <Check className="h-4 w-4" /> : s.num}
                  </div>
                  <span
                    className={cn(
                      'text-xs font-medium uppercase tracking-wide',
                      active ? 'text-primary-600' : 'text-text-muted'
                    )}
                  >
                    {s.title}
                  </span>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <Card className="flex min-h-[400px] flex-col">
        <CardContent className="flex flex-1 flex-col p-6 lg:p-8">
          {loading ? (
            <div className="flex flex-1 flex-col items-center justify-center space-y-6 py-12">
              <div className="flex h-16 w-16 items-center justify-center rounded-xl border border-border bg-surface shadow-sm">
                <RefreshCw className="h-8 w-8 animate-spin text-primary-600" />
              </div>
              <div className="space-y-2 text-center">
                <h3 className="text-lg font-semibold text-text-primary">Analyse en cours</h3>
                <p className="text-sm text-text-muted">
                  Agrégation des données commerciales et calcul des scores.
                </p>
              </div>
              <div className="h-2 w-64 overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full w-1/2 animate-shimmer bg-primary-600"
                  style={{
                    backgroundSize: '200% 100%',
                    backgroundImage:
                      'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.35) 50%, transparent 100%)',
                  }}
                />
              </div>
            </div>
          ) : (
            <>
              {step === 1 && (
                <div className="flex-1 space-y-6">
                  <h2 className="mb-4 flex items-center gap-2 text-base font-semibold text-text-primary">
                    <Box className="h-5 w-5 text-text-muted" aria-hidden />
                    Produit
                  </h2>

                  <div className="relative z-20 space-y-4">
                    <div>
                      <label htmlFor="product-input" className="mb-1.5 block text-sm font-medium text-text-primary">
                        Quel produit exportez-vous ?
                      </label>
                      <div className="relative">
                        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
                        <input
                          id="product-input"
                          type="text"
                          autoFocus
                          value={product}
                          onChange={(e) => handleProduct(e.target.value)}
                          placeholder="Ex. huile d'argan, safran…"
                          className="w-full rounded-lg border border-border bg-background py-2.5 pl-9 pr-4 text-sm font-medium text-text-primary transition-colors placeholder:text-text-muted focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                        />
                      </div>
                      {sugg.length > 0 && (
                        <ul
                          className="absolute left-0 right-0 z-30 mt-1 max-h-60 overflow-y-auto rounded-lg border border-border bg-surface shadow-lg"
                          role="listbox"
                        >
                          {sugg.map((s, i) => (
                            <li key={i}>
                              <button
                                type="button"
                                onClick={() => pickSugg(s.label, s.hs_code)}
                                className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm transition-colors hover:bg-secondary"
                              >
                                <span className="font-medium text-text-primary">{s.label}</span>
                                <span className="rounded bg-secondary px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-text-secondary">
                                  HS {s.hs_code}
                                </span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>

                    <div>
                      <label
                        htmlFor="hs-input"
                        className="mb-1.5 flex items-center justify-between text-sm font-medium text-text-primary"
                      >
                        Code HS
                        <span className="rounded-full bg-secondary px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-text-muted">
                          Facultatif
                        </span>
                      </label>
                      <input
                        id="hs-input"
                        type="text"
                        value={hsCode}
                        onChange={(e) => setHsCode(e.target.value)}
                        placeholder="Ex. 151590"
                        className="w-full rounded-lg border border-border bg-background px-4 py-2.5 font-mono text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="flex-1 space-y-8">
                  <h2 className="mb-4 flex items-center gap-2 text-base font-semibold text-text-primary">
                    <Globe className="h-5 w-5 text-text-muted" aria-hidden />
                    Périmètre
                  </h2>

                  <div>
                    <p className="mb-3 text-sm font-medium text-text-primary">Portée de l&apos;analyse</p>
                    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                      {PERIMETERS.map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => setTopN(p.id)}
                          className={cn(
                            'rounded-lg border p-4 text-left transition-all',
                            topN === p.id
                              ? 'border-primary-600 bg-primary-50 dark:bg-primary-950/25'
                              : 'border-border bg-background hover:border-text-muted'
                          )}
                        >
                          <p
                            className={cn(
                              'text-sm font-semibold',
                              topN === p.id ? 'text-primary-700 dark:text-primary-300' : 'text-text-primary'
                            )}
                          >
                            {p.label}
                          </p>
                          <p
                            className={cn(
                              'mt-1 text-xs',
                              topN === p.id ? 'text-primary-600/90' : 'text-text-muted'
                            )}
                          >
                            {p.desc}
                          </p>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="mb-2 text-sm font-medium text-text-primary">Critères (affichage)</p>
                    <p className="mb-3 text-xs text-text-muted">
                      La pondération métier est gérée côté moteur ; ces cases préparent l&apos;interface
                      d&apos;affinage futur.
                    </p>
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                      {[
                        { key: 'importVol' as const, label: "Volume d'importation", icon: BarChart },
                        { key: 'growth' as const, label: 'Croissance du marché', icon: TrendingUp },
                        { key: 'regulations' as const, label: 'Barrières douanières', icon: Shield },
                        { key: 'culture' as const, label: 'Proximité culturelle', icon: Globe },
                      ].map((c) => (
                        <label
                          key={c.key}
                          className={cn(
                            'flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors',
                            criteria[c.key]
                              ? 'border-primary-200 bg-primary-50/50 dark:border-primary-900 dark:bg-primary-950/20'
                              : 'border-border bg-surface opacity-80 hover:opacity-100'
                          )}
                        >
                          <input
                            type="checkbox"
                            checked={criteria[c.key]}
                            onChange={(e) => setCriteria({ ...criteria, [c.key]: e.target.checked })}
                            className="h-4 w-4 rounded border-border text-primary-600 focus:ring-primary-500"
                          />
                          <span className="flex items-center gap-2 text-sm font-medium text-text-primary">
                            <c.icon className="h-4 w-4 text-text-muted" />
                            {c.label}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="flex-1 space-y-6">
                  <h2 className="mb-4 flex items-center gap-2 text-base font-semibold text-text-primary">
                    <Check className="h-5 w-5 text-success" aria-hidden />
                    Résumé
                  </h2>

                  <div className="space-y-4 rounded-lg border border-border bg-secondary/40 p-5">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Produit</p>
                        <p className="mt-1 text-sm font-semibold text-text-primary">{product || 'Non spécifié'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Code HS</p>
                        <p className="mt-1 font-mono text-sm font-semibold text-text-primary">{hsCode || 'Auto'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Portée</p>
                        <p className="mt-1 text-sm font-semibold text-text-primary">
                          {topN === 0 ? 'Tous les marchés' : `Top ${topN}`}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Durée estimée</p>
                        <p className="mt-1 text-sm font-semibold text-text-primary">
                          ~{topN === 0 ? '45' : '12'} secondes
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-auto flex items-center justify-between border-t border-border pt-6">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setStep(step - 1)}
                  disabled={step === 1}
                  className={step === 1 ? 'pointer-events-none opacity-0' : ''}
                >
                  <ChevronLeft className="h-4 w-4" /> Retour
                </Button>

                {step < 3 ? (
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => setStep(step + 1)}
                    disabled={step === 1 && !product}
                  >
                    Suivant <ChevronRight className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button type="button" onClick={handleSubmit}>
                    Lancer l&apos;analyse <ArrowRight className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  )
}
