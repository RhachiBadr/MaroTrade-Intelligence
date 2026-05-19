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
import { cn } from '@/lib/utils'

export default function CountryDetailPage() {
  const { country: countryParam } = useParams<{ country: string }>()
  const { results: storeResults, expertMode } = useAnalysisStore()
  const results = storeResults.length ? storeResults : MOCK_RESULTS
  const result = results.find(r => r.country.code.toLowerCase() === countryParam) ?? results[0]

  if (!result) return <div className="p-20 text-center text-text-muted font-bold">Pays non trouvé.</div>

  const { country, score_final, dimensions, shap_values, top_atouts, top_risques, accord_info, logistique, forecast } = result

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-2">
      <nav className="flex flex-wrap items-center gap-2 text-xs font-medium text-text-muted">
        <Link href="/dashboard" className="hover:text-primary transition-colors">Tableau de bord</Link>
        <ChevronRight className="w-3 h-3 opacity-30" />
        <Link href="/results" className="hover:text-primary transition-colors">Résultats d'Analyse</Link>
        <ChevronRight className="w-3 h-3 opacity-30" />
        <span className="text-text-primary">{country.name}</span>
      </nav>

      {/* Hero Header */}
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
              {accord_info.accord} — <span className="text-primary font-bold">Droits à l'import : {accord_info.droits}%</span>
            </p>
            
            {forecast && (
              <div className="flex flex-wrap items-center gap-4 pt-1 sm:gap-6">
                <div className="flex items-center gap-2 text-sm font-medium text-success">
                  <TrendingUp className="w-4 h-4" />
                  +{(forecast.cagr_prevu).toFixed(1)}%/an (CAGR)
                </div>
                <div className="h-4 w-px bg-border" />
                <div className="text-sm font-medium text-text-muted">
                  Prévision 2026 : <span className="text-text-primary">{(forecast.valeur_2026).toFixed(1)}M USD</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex flex-col items-center gap-2">
            <ScoreBadge
              score={score_final}
              size="lg"
              className="h-28 w-28 rounded-2xl text-3xl shadow-md shadow-primary-600/10 sm:h-32 sm:w-32 sm:text-4xl"
            />
            <span className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">Score final</span>
          </div>
        </div>
      </div>

      {/* Strategic Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Dimensions & Logistics */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Facts */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Export Potential', value: 'High', icon: <Target className="w-4 h-4" />, color: 'primary' },
              { label: 'Logistique (LPI)', value: `${logistique.lpi.toFixed(2)}/5`, icon: <Box className="w-4 h-4" />, color: 'secondary' },
              { label: 'Distance Mer', value: `${logistique.distance_km.toLocaleString()} km`, icon: <Ship className="w-4 h-4" />, color: 'secondary' },
              { label: 'Risque Pays', value: 'Low', icon: <ShieldCheck className="w-4 h-4" />, color: 'success' },
            ].map((fact) => (
              <div
                key={fact.label}
                className="rounded-xl border border-border bg-surface p-4 shadow-sm transition-colors hover:border-primary-200 dark:hover:border-primary-800 sm:p-5"
              >
                <div className="mb-2 flex items-center gap-2 text-text-muted">
                  {fact.icon}
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">{fact.label}</span>
                </div>
                <p className="text-lg font-semibold text-text-primary">{fact.value}</p>
              </div>
            ))}
          </div>

          {/* Scores Detail */}
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
        </div>

        {/* Sidebar Context */}
        <div className="space-y-8">
          {/* Atouts */}
          <div className="rounded-xl border border-success/30 bg-success-muted/40 p-6 shadow-sm dark:bg-success-muted/20 sm:p-8">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-success">
              <CheckCircle size={16} className="text-success" />
              Atouts
            </h3>
            <ul className="space-y-4">
              {top_atouts.map((a, i) => (
                <li
                  key={i}
                  className="flex gap-3 text-sm font-medium leading-snug text-text-secondary"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-success mt-1.5 flex-shrink-0" />
                  {a}
                </li>
              ))}
            </ul>
          </div>

          {/* Risques */}
          {top_risques.length > 0 && (
            <div className="rounded-xl border border-warning-500/25 bg-warning-50/50 p-6 shadow-sm dark:bg-warning-600/10 sm:p-8">
              <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-warning-600">
                <AlertTriangle size={16} className="text-warning" />
                Points de vigilance
              </h3>
              <ul className="space-y-4">
                {top_risques.map((r, i) => (
                  <li key={i} className="flex gap-3 text-sm font-medium leading-snug text-text-secondary">
                    <div className="w-1.5 h-1.5 rounded-full bg-warning mt-1.5 flex-shrink-0" />
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Expert Mode Banner */}
          {!expertMode && (
            <div className="rounded-xl border border-dashed border-border bg-secondary/40 p-6 text-center sm:p-8">
              <Sparkles className="mx-auto mb-3 h-8 w-8 text-primary-600" />
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-secondary">Vues avancées</p>
              <p className="text-sm leading-relaxed text-text-muted">
                Activez le <strong>Mode Expert</strong> pour débloquer les contributions SHAP et les prévisions Prophet.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Expert Section */}
      {expertMode && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-10 duration-1000">
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

function CheckCircle({ size, className }: { size?: number, className?: string }) {
  return (
    <svg width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
