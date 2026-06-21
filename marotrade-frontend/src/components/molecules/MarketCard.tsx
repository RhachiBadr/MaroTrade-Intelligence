'use client'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { TrendArrow } from '@/components/atoms/TrendArrow'
import { DimensionBar } from '@/components/molecules/DimensionBar'
import type { MarketResult } from '@/types'
import { AlertTriangle, ArrowUpRight, BarChart3, CheckCircle2, Info, Route, ShieldCheck, TrendingUp } from 'lucide-react'
import { useI18n } from '@/lib/i18n'

interface Props {
  result: MarketResult
  expertMode?: boolean
  className?: string
}

/** Card displaying a single market result with key indicators. */
export function MarketCard({ result, expertMode = false, className }: Props) {
  const { t, formatNumber } = useI18n()
  const { country, score_final, rank, accord_info, dimensions, forecast } = result
  const usesV6 = result.scoring_method === 'v6_market_attractiveness'
  const strengths = result.v6_strengths?.length ? result.v6_strengths : result.top_atouts
  const risks = result.v6_risks?.length ? result.v6_risks : result.top_risques
  const methodLabel = usesV6 ? 'V6 + PME' : t('analysis.model')
  const snapshot = result.v6_feature_snapshot ?? {}
  const importValue = typeof snapshot.import_value_usd === 'number' ? snapshot.import_value_usd : null
  const growth = typeof snapshot.growth_lag1_pct === 'number' ? snapshot.growth_lag1_pct : null
  const distance = typeof snapshot.distance_km === 'number' ? snapshot.distance_km : result.logistique.distance_km
  const droits = typeof snapshot.droits_pct === 'number' ? snapshot.droits_pct : accord_info.droits
  const marketValue = importValue ? `${(importValue / 1_000_000).toFixed(1)}M USD` : 'N/A'
  const priority =
    score_final >= 85
      ? 'Priorite forte'
      : score_final >= 70
        ? 'Potentiel interessant'
        : score_final >= 50
          ? 'A valider'
          : 'Secondaire'
  const priorityTone =
    score_final >= 85
      ? 'border-emerald-500/30 bg-emerald-100 text-slate-950 shadow-sm shadow-emerald-600/10 dark:border-emerald-400/30 dark:bg-emerald-500/20 dark:text-white'
      : score_final >= 70
        ? 'border-amber-200 bg-amber-50 text-slate-950 dark:border-amber-800 dark:bg-amber-950/30 dark:text-white'
        : 'border-border bg-secondary text-text-secondary'
  const scoreMeaning =
    score_final >= 85
      ? 'Marche prioritaire pour une premiere prospection.'
      : score_final >= 70
        ? 'Marche prometteur, a confirmer commercialement.'
        : 'Marche utile en veille ou en analyse secondaire.'
  const scoreTone =
    score_final >= 85
      ? 'from-emerald-500/20 via-teal-500/10 to-primary-500/10'
      : score_final >= 70
        ? 'from-amber-500/20 via-orange-500/10 to-primary-500/10'
        : 'from-slate-500/10 via-primary-500/5 to-transparent'
  const chips = [
    {
      label: 'Demande import',
      value: marketValue,
      icon: BarChart3,
      help: 'Valeur annuelle estimee des importations du marche pour le produit ou sa famille HS.',
      tone: 'text-text-primary',
    },
    {
      label: 'Croissance',
      value: growth !== null ? `${growth.toFixed(1)}%` : 'N/A',
      icon: TrendingUp,
      help: 'Evolution recente de la demande. Positive = marche en progression.',
      tone: growth !== null && growth < 0 ? 'text-warning-700 dark:text-warning-300' : 'text-success',
    },
    {
      label: 'Droits',
      value: `${Number(droits).toFixed(1)}%`,
      icon: ShieldCheck,
      help: 'Droits de douane appliques. Plus ils sont faibles, plus le marche est accessible.',
      tone: Number(droits) <= 0 ? 'text-success' : 'text-warning-700 dark:text-warning-300',
    },
    {
      label: 'Distance',
      value: `${formatNumber(Number(distance), { maximumFractionDigits: 0 })} km`,
      icon: Route,
      help: 'Distance logistique approximative depuis le Maroc.',
      tone: 'text-text-primary',
    },
  ]

  return (
    <div
      className={cn(
        'group relative flex min-h-[460px] flex-col overflow-hidden rounded-2xl border border-border/80 bg-surface shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-600/10',
        className
      )}
    >
      <div className={cn('pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-br opacity-80 transition-opacity group-hover:opacity-100', scoreTone)} />
      <div className="pointer-events-none absolute -right-10 -top-12 h-32 w-32 rounded-full bg-primary-500/10 blur-3xl transition-transform group-hover:scale-125" />

      <div className="relative border-b border-border/60 p-5 pb-4 sm:p-6 sm:pb-4">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-border/70 bg-surface/85 text-lg font-semibold text-text-primary shadow-sm">
              {country.code}
            </div>
            <div className="min-w-0">
              <div className="mb-0.5">
                <span className="inline-block rounded-full bg-surface/80 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-text-muted ring-1 ring-border/70">
                  {t('analysis.rank')} {rank}
                </span>
              </div>
              <h3 className="truncate text-base font-semibold tracking-tight text-text-primary">{country.name}</h3>
              <p className="mt-0.5 truncate text-xs font-medium text-text-muted">{accord_info.accord}</p>
              <p className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-primary-600">{methodLabel}</p>
            </div>
          </div>
          <ScoreBadge score={score_final} size="lg" />
        </div>
        <div className={cn('inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold', priorityTone)}>
          <Info className="h-3.5 w-3.5" />
          {priority}
        </div>
        <p className="mt-2 text-xs leading-relaxed text-text-secondary">{scoreMeaning}</p>
      </div>

      <div className="relative grid grid-cols-2 gap-2 p-5 pb-4 sm:p-6 sm:pb-4">
        {chips.map(({ label, value, icon: Icon, help, tone }) => (
          <div key={label} title={help} className="rounded-xl border border-border/70 bg-secondary/35 px-3 py-2.5">
            <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
              <Icon className="h-3 w-3" />
              {label}
            </div>
            <p className={cn('truncate text-sm font-semibold', tone)}>{value}</p>
          </div>
        ))}
      </div>

      {forecast && (
        <div className="mx-5 mb-4 flex items-center gap-3 rounded-lg border border-border bg-secondary/50 px-3 py-2.5 sm:mx-6">
          <TrendArrow cagr={forecast.cagr_prevu} />
          <span className="text-xs font-bold leading-tight text-text-secondary">
            Tendance 2026 : <span className="text-text-primary">{(forecast.valeur_2026 / 1e6).toFixed(1)}M USD</span>
          </span>
        </div>
      )}

      {expertMode && (
        <div className="mx-5 mb-4 space-y-2 rounded-lg border border-border bg-secondary/40 p-3 sm:mx-6">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">Score — détail</p>
          {dimensions.slice(0, 3).map((d) => (
            <DimensionBar key={d.nom} nom={d.nom} score={d.score} />
          ))}
        </div>
      )}

      <div className="flex-1 px-5 pb-5 sm:px-6">
        {strengths.length > 0 && (
          <div className="mb-4 rounded-xl border border-success/15 bg-success/5 p-3">
            <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wide text-success">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Pourquoi ce marche ?
            </div>
            <div className="space-y-2">
              {strengths.slice(0, 2).map((a, i) => (
                <div key={i} className="flex gap-2 text-xs font-medium leading-snug text-success">
                  <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-success" />
                  {a}
                </div>
              ))}
            </div>
          </div>
        )}

        {risks.length > 0 && (
          <div className="mb-6 space-y-2 rounded-xl border border-warning-500/20 bg-warning-50/50 px-3 py-2.5 dark:bg-warning-600/10">
            <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wide text-warning-700 dark:text-warning-300">
              <AlertTriangle className="h-3.5 w-3.5" />
              Point de vigilance
            </div>
            {risks.slice(0, 1).map((r, i) => (
              <div key={i} className="flex gap-2 text-xs font-medium leading-snug text-warning-700 dark:text-warning-300">
                <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-warning-500" />
                {r}
              </div>
            ))}
          </div>
        )}
      </div>

      <Link
        href={`/results/${country.code.toLowerCase()}`}
        className="mx-5 mb-5 mt-auto inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-border bg-secondary text-xs font-semibold text-text-primary transition-all hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700 dark:hover:bg-primary-950/30 sm:mx-6"
      >
        <ArrowUpRight className="h-3.5 w-3.5" />
        {t('analysis.analyzeCountry')}
      </Link>
    </div>
  )
}
