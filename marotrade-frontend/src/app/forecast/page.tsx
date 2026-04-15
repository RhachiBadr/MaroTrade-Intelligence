'use client'
import { useState } from 'react'
import { ForecastChart } from '@/components/organisms/ForecastChart'
import { TrendArrow } from '@/components/atoms/TrendArrow'
import { MOCK_RESULTS, MOCK_FORECAST } from '@/lib/mock-data'
import { cn } from '@/lib/utils'
import { TrendingUp, Globe, Target } from 'lucide-react'

export default function ForecastPage() {
  const [selectedIdx, setSelectedIdx] = useState(0)
  const result = MOCK_RESULTS[selectedIdx]

  return (
    <div className="max-w-5xl mx-auto space-y-10 py-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-6 pb-6 border-b border-border">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary-50 dark:bg-primary-900/30 rounded-xl">
              <TrendingUp className="w-6 h-6 text-primary-600" />
            </div>
            <h1 className="text-3xl font-extrabold text-text-primary tracking-tight">Prévisions de Marché</h1>
          </div>
          <p className="text-sm font-medium text-text-muted">
            Modélisation <span className="text-text-secondary font-bold">Comet/Prophet</span> · Données UN Comtrade · Confiance 80%
          </p>
        </div>
      </div>

      {/* Country selector */}
      <div className="flex flex-wrap gap-2 animate-in fade-in duration-500">
        {MOCK_RESULTS.map((r, i) => (
          <button key={r.country.code} onClick={() => setSelectedIdx(i)}
            className={cn(
              "flex items-center gap-3 px-5 py-2.5 rounded-2xl border-2 transition-all font-bold text-sm",
              i === selectedIdx
                ? "bg-primary-600 text-white border-primary-600 shadow-lg shadow-primary-600/20 dark:shadow-none"
                : "bg-surface border-border text-text-secondary hover:border-text-muted"
            )}>
            <span className="text-xl">{r.country.flag}</span>
            <span>{r.country.name}</span>
          </button>
        ))}
      </div>

      {/* Forecast summary */}
      {
        result.forecast && (
          <div className="grid sm:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {[
              { label: 'CAGR Prévu', value: <TrendArrow cagr={result.forecast.cagr_prevu} className="text-xl" />, icon: <TrendingUp className="w-4 h-4" /> },
              { label: 'Potentiel 2026', value: <span className="text-xl font-black text-text-primary">{result.forecast.valeur_2026.toFixed(1)}M USD</span>, icon: <Globe className="w-4 h-4" /> },
              { label: 'Score Stratégique', value: <span className="text-xl font-black text-primary">{result.score_final}/100</span>, icon: <Target className="w-4 h-4" /> },
            ].map(({ label, value, icon }) => (
              <div key={label} className="bg-surface rounded-3xl border border-border p-6 shadow-sm flex flex-col items-center text-center">
                <div className="p-2 bg-background rounded-xl mb-3 text-text-muted">{icon}</div>
                <p className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-2">{label}</p>
                {value}
              </div>
            ))}
          </div>
        )
      }

      {/* Chart */}
      <div className="bg-surface rounded-[2.5rem] border border-border p-10 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-xl font-bold text-text-primary">Projection de la demande importatrice</h2>
          <div className="flex items-center gap-4 text-[10px] font-black text-text-muted uppercase tracking-widest">
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-primary" /> Historique</div>
            <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-primary/20" /> Prévisions</div>
          </div>
        </div>
        <ForecastChart data={MOCK_FORECAST} countryName={result.country.name} />
      </div>

      {/* Ranking comparison */}
      <div className="bg-surface rounded-[2.5rem] border border-border p-10 shadow-sm animate-in fade-in slide-in-from-bottom-6 duration-1000">
        <h2 className="text-xl font-bold text-text-primary mb-8">Classement vs Potentiel 2026</h2>
        <div className="space-y-6">
          {MOCK_RESULTS.map((r) => (
            <div key={r.country.code} className="flex items-center gap-4 group">
              <span className="w-8 text-[10px] font-black text-text-muted uppercase tracking-widest">#{r.rank}</span>
              <div className="text-3xl p-1 bg-secondary rounded-xl group-hover:scale-110 transition-transform">{r.country.flag}</div>
              <span className="text-sm font-bold text-text-primary w-32 truncate">{r.country.name}</span>
              <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full" style={{ width: `${r.score_final}%` }} />
              </div>
              <div className="w-16 text-right">
                <span className="text-xs font-bold text-text-primary font-mono">{r.score_final}/100</span>
              </div>
              <div className="w-20 flex justify-end">
                {r.forecast && <TrendArrow cagr={r.forecast.cagr_prevu} className="text-xs font-bold" />}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div >
  )
}
