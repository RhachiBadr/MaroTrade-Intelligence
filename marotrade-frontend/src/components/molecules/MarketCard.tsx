'use client'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { TrendArrow } from '@/components/atoms/TrendArrow'
import { DimensionBar } from '@/components/molecules/DimensionBar'
import type { MarketResult } from '@/types'

interface Props {
  result:      MarketResult
  expertMode?: boolean
  className?:  string
}

/** Card displaying a single market result with key indicators */
export function MarketCard({ result, expertMode = false, className }: Props) {
  const { country, score_final, rank, accord_info, top_atouts, top_risques, dimensions, forecast } = result
  return (
    <div className={cn('flex flex-col rounded-xl border border-border bg-surface p-5 shadow-sm transition-shadow hover:shadow-md sm:p-6', className)}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex shrink-0 rounded-lg bg-secondary/80 p-2 text-3xl">{country.flag}</div>
          <div className="min-w-0">
            <div className="mb-0.5">
              <span className="inline-block rounded bg-secondary px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
                Rang {rank}
              </span>
            </div>
            <h3 className="truncate text-base font-semibold tracking-tight text-text-primary">{country.name}</h3>
            <p className="mt-0.5 truncate text-xs font-medium text-text-muted">{accord_info.accord}</p>
          </div>
        </div>
        <ScoreBadge score={score_final} size="lg" />
      </div>

      {/* Forecast mini */}
      {forecast && (
        <div className="mb-4 flex items-center gap-3 rounded-lg border border-border bg-secondary/50 px-3 py-2.5">
          <TrendArrow cagr={forecast.cagr_prevu} />
          <span className="text-xs font-bold text-text-secondary leading-tight">
            Tendance 2026 : <span className="text-text-primary">{(forecast.valeur_2026 / 1e6).toFixed(1)}M USD</span>
          </span>
        </div>
      )}

      {/* Dimensions (expert mode) */}
      {expertMode && (
        <div className="mb-4 space-y-2 rounded-lg border border-border bg-secondary/40 p-3">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">Score — détail</p>
          {dimensions.slice(0, 3).map((d) => (
            <DimensionBar key={d.nom} nom={d.nom} score={d.score} />
          ))}
        </div>
      )}

      <div className="flex-1">
        {/* Atouts */}
        {top_atouts.length > 0 && (
          <div className="space-y-1.5 mb-4">
            {top_atouts.slice(0, 2).map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-medium text-success">
                <div className="h-1 w-1 shrink-0 rounded-full bg-success" />
                {a}
              </div>
            ))}
          </div>
        )}

        {/* Risques */}
        {top_risques.length > 0 && (
          <div className="space-y-1.5 mb-6">
            {top_risques.slice(0, 1).map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-medium text-warning-600">
                <div className="h-1 w-1 shrink-0 rounded-full bg-warning-500" />
                {r}
              </div>
            ))}
          </div>
        )}
      </div>

      <Link
        href={`/results/${country.code.toLowerCase()}`}
        className="mt-auto block w-full rounded-lg border border-border bg-secondary py-2.5 text-center text-xs font-semibold text-text-primary transition-colors hover:border-primary-300 hover:bg-primary-50 dark:hover:bg-primary-950/30"
      >
        Analyser le marché pays →
      </Link>
    </div>
  )
}
