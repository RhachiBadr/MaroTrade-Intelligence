'use client'

import { useState } from 'react'
import { ForecastChart } from '@/components/organisms/ForecastChart'
import { TrendArrow } from '@/components/atoms/TrendArrow'
import { MOCK_RESULTS, MOCK_FORECAST } from '@/lib/mock-data'
import { cn } from '@/lib/utils'
import { TrendingUp, Globe, Target } from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { Card, CardContent } from '@/components/ui/card'

export default function ForecastPage() {
  const [selectedIdx, setSelectedIdx] = useState(0)
  const result = MOCK_RESULTS[selectedIdx]

  return (
    <PageContainer className="max-w-5xl space-y-8 py-2">
      <PageHeader
        title="Prévisions de marché"
        description="Modélisation Prophet · données UN Comtrade · intervalle de confiance affiché sur le graphique."
      />

      <div className="flex flex-wrap gap-2">
        {MOCK_RESULTS.map((r, i) => (
          <button
            key={r.country.code}
            type="button"
            onClick={() => setSelectedIdx(i)}
            className={cn(
              'flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-all',
              i === selectedIdx
                ? 'border-primary-600 bg-primary-600 text-white shadow-sm'
                : 'border-border bg-surface text-text-secondary hover:border-text-muted'
            )}
          >
            <span className="text-lg leading-none">{r.country.flag}</span>
            <span>{r.country.name}</span>
          </button>
        ))}
      </div>

      {result.forecast && (
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            {
              label: 'CAGR prévu',
              value: <TrendArrow cagr={result.forecast.cagr_prevu} className="text-lg" />,
              icon: <TrendingUp className="h-4 w-4" />,
            },
            {
              label: 'Potentiel 2026',
              value: (
                <span className="text-xl font-semibold text-text-primary">
                  {result.forecast.valeur_2026.toFixed(1)}M USD
                </span>
              ),
              icon: <Globe className="h-4 w-4" />,
            },
            {
              label: 'Score stratégique',
              value: (
                <span className="text-xl font-semibold text-primary-600">{result.score_final}/100</span>
              ),
              icon: <Target className="h-4 w-4" />,
            },
          ].map(({ label, value, icon }) => (
            <Card key={label} className="shadow-none">
              <CardContent className="flex flex-col items-center p-5 text-center">
                <div className="mb-2 rounded-lg bg-secondary p-2 text-text-muted">{icon}</div>
                <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-text-muted">{label}</p>
                {value}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card className="shadow-none">
        <CardContent className="space-y-6 p-6 sm:p-8">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-lg font-semibold text-text-primary">Demande importatrice</h2>
            <div className="flex items-center gap-4 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-primary-600" /> Historique
              </div>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-primary-200 dark:bg-primary-800" /> Prévisions
              </div>
            </div>
          </div>
          <ForecastChart data={MOCK_FORECAST} countryName={result.country.name} />
        </CardContent>
      </Card>

      <Card className="shadow-none">
        <CardContent className="space-y-6 p-6 sm:p-8">
          <h2 className="text-lg font-semibold text-text-primary">Classement vs potentiel 2026</h2>
          <div className="space-y-4">
            {MOCK_RESULTS.map((r) => (
              <div key={r.country.code} className="flex items-center gap-3 sm:gap-4">
                <span className="w-8 shrink-0 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
                  #{r.rank}
                </span>
                <div className="shrink-0 rounded-lg bg-secondary p-1 text-2xl">{r.country.flag}</div>
                <span className="w-28 shrink-0 truncate text-sm font-medium text-text-primary sm:w-32">
                  {r.country.name}
                </span>
                <div className="hidden min-w-0 flex-1 sm:block">
                  <div className="h-2 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full rounded-full bg-primary-600"
                      style={{ width: `${r.score_final}%` }}
                    />
                  </div>
                </div>
                <span className="ml-auto shrink-0 font-mono text-xs font-semibold text-text-primary">
                  {r.score_final}/100
                </span>
                <div className="hidden w-20 shrink-0 justify-end sm:flex">
                  {r.forecast && <TrendArrow cagr={r.forecast.cagr_prevu} className="text-xs font-medium" />}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  )
}
