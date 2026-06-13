'use client'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useAnalysisStore } from '@/store/analysis'
import { MOCK_RESULTS, MOCK_FORECAST } from '@/lib/mock-data'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { DimensionBar } from '@/components/molecules/DimensionBar'
import { ShapWaterfall } from '@/components/organisms/ShapWaterfall'
import { ForecastChart } from '@/components/organisms/ForecastChart'
import { ChevronRight, Globe, ShieldCheck, Ship, Box, Target, Info, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react'

const formatInteger = (value: number) =>
  Math.round(value)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')

export default function CountryDetailPage() {
  const { country: countryParam } = useParams<{ country: string }>()
  const { results: storeResults, expertMode } = useAnalysisStore()
  const results = storeResults.length ? storeResults : MOCK_RESULTS
  const result = results.find((r) => r.country.code.toLowerCase() === countryParam) ?? results[0]

  if (!result) return <div className="p-20 text-center font-bold text-text-muted">Pays non trouvé.</div>

  const { country, score_final, dimensions, shap_values, accord_info, logistique, forecast } = result
  const usesV6 = result.scoring_method === 'v6_market_attractiveness'
  const strengths = result.v6_strengths?.length ? result.v6_strengths : result.top_atouts
  const risks = result.v6_risks?.length ? result.v6_risks : result.top_risques
  const explanation = result.v6_explanation || 'Ce marché est recommandé selon les signaux commerciaux disponibles.'
  const snapshot = result.v6_feature_snapshot ?? {}

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-2">
      <nav className="flex flex-wrap items-center gap-2 text-xs font-medium text-text-muted">
        <Link href="/dashboard" className="transition-colors hover:text-primary">
          Tableau de bord
        </Link>
        <ChevronRight className="h-3 w-3 opacity-30" />
        <Link href="/results" className="transition-colors hover:text-primary">
          Résultats d'analyse
        </Link>
        <ChevronRight className="h-3 w-3 opacity-30" />
        <span className="text-text-primary">{country.name}</span>
      </nav>

      <div className="group relative overflow-hidden rounded-xl border border-border bg-surface p-6 shadow-sm sm:p-8 lg:p-10">
        <div className="pointer-events-none absolute right-0 top-0 p-8 opacity-[0.04] transition-opacity group-hover:opacity-[0.07]">
          <Globe className="h-48 w-48 text-primary-600" />
        </div>

        <div className="relative flex flex-wrap items-center gap-8">
          <div className="rounded-xl bg-secondary/70 p-4 text-6xl transition-transform duration-300 group-hover:scale-[1.02] sm:text-7xl">
            {country.flag}
          </div>

          <div className="min-w-0 flex-1 space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-semibold tracking-tight text-text-primary sm:text-4xl">{country.name}</h1>
              <span className="rounded-full bg-primary-50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-primary-700 dark:bg-primary-950/50 dark:text-primary-300">
                Marché prioritaire
              </span>
            </div>

            <p className="max-w-2xl text-base leading-relaxed text-text-secondary sm:text-lg">
              {accord_info.accord} — <span className="font-bold text-primary">Droits à l'import : {accord_info.droits}%</span>
            </p>

            {forecast && (
              <div className="flex flex-wrap items-center gap-4 pt-1 sm:gap-6">
                <div className="flex items-center gap-2 text-sm font-medium text-success">
                  <TrendingUp className="h-4 w-4" />
                  +{forecast.cagr_prevu.toFixed(1)}%/an (CAGR)
                </div>
                <div className="h-4 w-px bg-border" />
                <div className="text-sm font-medium text-text-muted">
                  Prévision 2026 : <span className="text-text-primary">{forecast.valeur_2026.toFixed(1)}M USD</span>
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col items-center gap-2">
            <ScoreBadge score={score_final} size="lg" className="h-28 w-28 rounded-2xl text-3xl shadow-md shadow-primary-600/10 sm:h-32 sm:w-32 sm:text-4xl" />
            <span className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">Score final</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-8 lg:col-span-2">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { label: 'Potentiel export', value: 'Élevé', icon: <Target className="h-4 w-4" /> },
              { label: 'Logistique (LPI)', value: `${logistique.lpi.toFixed(2)}/5`, icon: <Box className="h-4 w-4" /> },
              { label: 'Distance maritime', value: `${formatInteger(logistique.distance_km)} km`, icon: <Ship className="h-4 w-4" /> },
              { label: 'Risque pays', value: 'Faible', icon: <ShieldCheck className="h-4 w-4" /> },
            ].map((fact) => (
              <div key={fact.label} className="rounded-xl border border-border bg-surface p-4 shadow-sm transition-colors hover:border-primary-200 dark:hover:border-primary-800 sm:p-5">
                <div className="mb-2 flex items-center gap-2 text-text-muted">
                  {fact.icon}
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">{fact.label}</span>
                </div>
                <p className="text-lg font-semibold text-text-primary">{fact.value}</p>
              </div>
            ))}
          </div>

          <div className="space-y-6 rounded-xl border border-border bg-surface p-6 shadow-sm sm:p-8 lg:p-10">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
                <Target className="h-5 w-5 text-primary-600" />
                Performances
              </h2>
              <span className="text-xs font-medium text-text-muted">6 dimensions</span>
            </div>
            <div className="grid gap-6">
              {dimensions.map((d) => (
                <DimensionBar key={d.nom} nom={d.nom} score={d.score} interpretation={d.interpretation} />
              ))}
            </div>
          </div>

          {usesV6 && (
            <div className="space-y-5 rounded-xl border border-primary-200 bg-primary-50/40 p-6 shadow-sm dark:border-primary-800 dark:bg-primary-950/20 sm:p-8">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wide text-primary-600">Explication modèle v6</p>
                <h2 className="mt-1 text-lg font-semibold text-text-primary">Pourquoi ce marché est recommandé</h2>
              </div>
              <p className="text-sm leading-relaxed text-text-secondary">{explanation}</p>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {[
                  ['Imports', snapshot.import_value_usd ? `${(Number(snapshot.import_value_usd) / 1e6).toFixed(1)}M USD` : 'N/A'],
                  ['Croissance', snapshot.growth_lag1_pct !== undefined ? `${Number(snapshot.growth_lag1_pct).toFixed(1)}%` : 'N/A'],
                  ['Droits', snapshot.droits_pct !== undefined ? `${Number(snapshot.droits_pct).toFixed(1)}%` : 'N/A'],
                  ['Distance', snapshot.distance_km !== undefined ? `${formatInteger(Number(snapshot.distance_km))} km` : 'N/A'],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-lg border border-primary-100 bg-surface/80 p-3 dark:border-primary-900">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">{label}</p>
                    <p className="mt-1 text-sm font-semibold text-text-primary">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-8">
          <div className="rounded-xl border border-success/30 bg-success-muted/40 p-6 shadow-sm dark:bg-success-muted/20 sm:p-8">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-success">
              <CheckCircle size={16} className="text-success" />
              Atouts
            </h3>
            <ul className="space-y-4">
              {strengths.map((a, i) => (
                <li key={i} className="flex gap-3 text-sm font-medium leading-snug text-text-secondary">
                  <div className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-success" />
                  {a}
                </li>
              ))}
            </ul>
          </div>

          {risks.length > 0 && (
            <div className="rounded-xl border border-warning-500/25 bg-warning-50/50 p-6 shadow-sm dark:bg-warning-600/10 sm:p-8">
              <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-warning-600">
                <AlertTriangle size={16} className="text-warning" />
                Points de vigilance
              </h3>
              <ul className="space-y-4">
                {risks.map((r, i) => (
                  <li key={i} className="flex gap-3 text-sm font-medium leading-snug text-text-secondary">
                    <div className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-warning" />
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {!expertMode && (
            <div className="rounded-xl border border-dashed border-border bg-secondary/40 p-6 text-center sm:p-8">
              <Sparkles className="mx-auto mb-3 h-8 w-8 text-primary-600" />
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-secondary">Vues avancées</p>
              <p className="text-sm leading-relaxed text-text-muted">
                Activez le <strong>mode expert</strong> pour débloquer les contributions SHAP et les prévisions Prophet.
              </p>
            </div>
          )}
        </div>
      </div>

      {expertMode && (
        <div className="grid grid-cols-1 gap-8 animate-in fade-in slide-in-from-bottom-10 duration-1000 lg:grid-cols-2">
          <div className="rounded-xl border border-border bg-surface p-6 shadow-sm sm:p-8 lg:p-10">
            <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
                <Info className="h-5 w-5 text-primary-600" />
                Explicabilité SHAP
              </h2>
              <span className="text-xs font-medium text-text-muted">Impact sur le score</span>
            </div>
            <ShapWaterfall shapValues={shap_values} />
          </div>

          <div className="rounded-xl border border-border bg-surface p-6 shadow-sm sm:p-8 lg:p-10">
            <h2 className="mb-6 flex items-center gap-2 text-lg font-semibold text-text-primary">
              <TrendingUp className="h-5 w-5 text-primary-600" />
              Projection Prophet
            </h2>
            <ForecastChart data={MOCK_FORECAST} />
          </div>
        </div>
      )}
    </div>
  )
}

function CheckCircle({ size, className }: { size?: number; className?: string }) {
  return (
    <svg width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
