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
    <div className={cn('rounded-3xl border border-border bg-white shadow-sm hover:shadow-xl hover:border-primary/20 transition-all duration-300 p-6 flex flex-col', className)}>
      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-4">
          <div className="text-4xl bg-secondary/50 p-2 rounded-2xl">{country.flag}</div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-black text-text-muted uppercase tracking-widest bg-secondary px-1.5 py-0.5 rounded">Rank #{rank}</span>
            </div>
            <h3 className="font-bold text-lg text-text-primary tracking-tight leading-tight">{country.name}</h3>
            <p className="text-xs font-bold text-text-muted mt-0.5">{accord_info.accord}</p>
          </div>
        </div>
        <ScoreBadge score={score_final} size="lg" />
      </div>

      {/* Forecast mini */}
      {forecast && (
        <div className="flex items-center gap-3 mb-5 px-4 py-3 rounded-2xl bg-secondary/50 border border-border/50">
          <TrendArrow cagr={forecast.cagr_prevu} />
          <span className="text-xs font-bold text-text-secondary leading-tight">
            Tendance 2026 : <span className="text-text-primary">{(forecast.valeur_2026 / 1e6).toFixed(1)}M USD</span>
          </span>
        </div>
      )}

      {/* Dimensions (expert mode) */}
      {expertMode && (
        <div className="space-y-3 mb-5 bg-secondary/30 p-4 rounded-2xl">
          <p className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-1">Détails du Score</p>
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
              <div key={i} className="flex items-center gap-2 text-xs font-bold text-success">
                <div className="w-1.5 h-1.5 rounded-full bg-success" />
                {a}
              </div>
            ))}
          </div>
        )}

        {/* Risques */}
        {top_risques.length > 0 && (
          <div className="space-y-1.5 mb-6">
            {top_risques.slice(0, 1).map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-bold text-warning">
                <div className="w-1.5 h-1.5 rounded-full bg-warning" />
                {r}
              </div>
            ))}
          </div>
        )}
      </div>

      <Link
        href={`/results/${country.code.toLowerCase()}`}
        className="w-full py-3 bg-secondary hover:bg-primary hover:text-white text-text-primary text-xs font-bold rounded-xl transition-all text-center"
      >
        Analyser le marché pays →
      </Link>
    </div>
  )
}
