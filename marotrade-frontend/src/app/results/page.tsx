'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useAnalysisStore } from '@/store/analysis'
import { MarketCard } from '@/components/molecules/MarketCard'
import { RadarComparison } from '@/components/organisms/RadarComparison'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { MOCK_RESULTS } from '@/lib/mock-data'
import { cn } from '@/lib/utils'
import { Database, ShieldCheck, Globe, Sparkles, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts'
import { PageContainer } from '@/components/ui/page-shell'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const LEVEL_COLORS = ['#0d9488', '#14b8a6', '#d97706', '#ea580c', '#dc2626']
const formatInteger = (value: number) =>
  Math.round(value)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')

export default function ResultsPage() {
  const { results: storeResults, params, expertMode, toggleExpertMode } = useAnalysisStore()
  const results = storeResults.length ? storeResults : MOCK_RESULTS
  const productName = params?.product_name ?? "Huile d'argan bio"
  const hsCode = params?.hs_code ?? '151590'
  const topMarket = results[0]
  const usesV6 = topMarket?.scoring_method === 'v6_market_attractiveness'
  const topImports =
    typeof topMarket?.v6_feature_snapshot?.import_value_usd === 'number'
      ? `${(topMarket.v6_feature_snapshot.import_value_usd / 1_000_000).toFixed(1)}M USD`
      : 'N/A'

  const [tab, setTab] = useState<'cards' | 'radar' | 'table'>('cards')

  const barData = results.map((r) => ({
    name: `${r.country.flag} ${r.country.name}`,
    score: r.score_final,
  }))

  const tabs = [
    { id: 'cards' as const, label: 'Fiches' },
    { id: 'radar' as const, label: 'Radar' },
    { id: 'table' as const, label: 'Tableau' },
  ]

  return (
    <PageContainer className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-end sm:justify-between">
        <div className="min-w-0">
          <nav className="mb-2 flex flex-wrap items-center gap-1.5 text-xs font-medium text-text-muted">
            <Link href="/dashboard" className="hover:text-primary-600">
              Tableau de bord
            </Link>
            <span className="text-text-muted/50">/</span>
            <Link href="/analyze" className="hover:text-primary-600">
              Analyse
            </Link>
            <span className="text-text-muted/50">/</span>
            <span className="text-text-secondary">Résultats</span>
          </nav>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">
            {results.length} marchés — <span className="text-primary-600">{productName}</span>
          </h1>
          <p className="mt-1 font-mono text-xs text-text-muted">HS {hsCode}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button type="button" variant={expertMode ? 'default' : 'secondary'} size="sm" onClick={toggleExpertMode}>
            {expertMode ? 'Mode expert' : 'Mode simple'}
          </Button>
          <Link
            href="/regulations"
            className="inline-flex h-8 items-center gap-2 rounded-lg border border-border bg-surface px-3 text-sm font-medium text-text-secondary transition-colors hover:bg-secondary"
          >
            <ShieldCheck className="h-4 w-4" />
            Réglementation
          </Link>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-2xl border border-primary-100 bg-gradient-to-br from-primary-50 via-surface to-emerald-50/60 p-5 shadow-sm dark:border-primary-900 dark:from-primary-950/30 dark:via-surface dark:to-emerald-950/20 sm:p-6">
        <div className="pointer-events-none absolute -right-12 -top-16 h-40 w-40 rounded-full bg-primary-500/10 blur-3xl" />
        <div className="grid gap-4 md:grid-cols-4">
          {[
            { label: 'Meilleur marché', value: topMarket?.country.name ?? 'N/A', icon: Sparkles },
            { label: 'Score recommandé', value: topMarket ? `${Math.round(topMarket.score_final)}/100` : 'N/A', icon: TrendingUp },
            { label: 'Modèle', value: usesV6 ? 'V6 + PME' : 'Multi-critères', icon: ShieldCheck },
            { label: 'Demande import', value: topImports, icon: Database },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="relative rounded-xl border border-white/70 bg-white/60 px-4 py-3 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
                <Icon className="h-3.5 w-3.5 text-primary-600" />
                {label}
              </div>
              <p className="truncate text-sm font-semibold text-text-primary">{value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="-mx-1 flex gap-3 overflow-x-auto pb-1">
        {results.map((r) => (
          <Card key={r.country.code} className="min-w-[132px] flex-1 shrink-0 border-primary-100 shadow-none transition-colors hover:border-primary-200 dark:border-primary-900">
            <CardContent className="p-4 text-center">
              <div className="mb-2 text-2xl">{r.country.flag}</div>
              <p className="truncate text-xs font-semibold text-text-primary">{r.country.name}</p>
              <p className="mb-3 text-[10px] font-medium uppercase tracking-wide text-text-muted">Rang {r.rank}</p>
              <div className="flex justify-center">
                <ScoreBadge score={r.score_final} size="sm" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="border-b border-border">
        <div className="flex gap-1" role="tablist" aria-label="Vue des résultats">
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={cn(
                'relative px-4 py-2.5 text-sm font-medium transition-colors',
                tab === t.id
                  ? 'text-primary-600 after:absolute after:bottom-0 after:left-2 after:right-2 after:h-0.5 after:rounded-full after:bg-primary-600'
                  : 'text-text-muted hover:text-text-secondary'
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'cards' && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {results.map((r) => (
            <MarketCard key={r.country.code} result={r} expertMode={expertMode} />
          ))}
        </div>
      )}

      {tab === 'radar' && (
        <Card className="shadow-none">
          <CardContent className="space-y-8 p-6 lg:p-8">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-text-primary">Comparaison multi-dimensions</h2>
              <p className="flex items-center gap-2 text-xs font-medium text-text-muted">
                <Globe className="h-4 w-4" /> Top 5 pays
              </p>
            </div>
            <RadarComparison results={results.slice(0, 5)} />

            <div className="border-t border-border pt-8">
              <h3 className="mb-4 text-sm font-medium text-text-muted">Score global</h3>
              <div className="w-full">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={barData} layout="vertical" margin={{ left: 8 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={130}
                      tick={{ fontSize: 11, fontWeight: 500, fill: 'var(--color-text-secondary)' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      cursor={{ fill: 'var(--color-secondary)' }}
                      formatter={(v) => [`${Number(v)}/100`, 'Score']}
                      contentStyle={{
                        borderRadius: '8px',
                        border: '1px solid var(--color-border)',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="score" radius={[0, 6, 6, 0]} barSize={20}>
                      {barData.map((_, i) => (
                        <Cell key={i} fill={LEVEL_COLORS[i] || '#2563eb'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'table' && (
        <Card className="overflow-hidden shadow-none">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead>
                <tr className="border-b border-border bg-secondary/50 text-left text-xs font-medium uppercase tracking-wide text-text-muted">
                  {['Rang', 'Marché', 'Score', 'Accord', 'Droits', 'LPI', 'Distance'].map((h) => (
                    <th key={h} className="px-4 py-3 lg:px-6">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {results.map((r) => (
                  <tr key={r.country.code} className="hover:bg-secondary/40">
                    <td className="px-4 py-3 font-medium text-text-muted lg:px-6">#{r.rank}</td>
                    <td className="px-4 py-3 lg:px-6">
                      <Link href={`/results/${r.country.code.toLowerCase()}`} className="flex items-center gap-2 font-semibold text-text-primary hover:text-primary-600">
                        <span className="text-lg">{r.country.flag}</span>
                        {r.country.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 lg:px-6">
                      <ScoreBadge score={r.score_final} size="sm" />
                    </td>
                    <td className="max-w-[200px] px-4 py-3 lg:px-6">
                      <p className="truncate text-xs font-medium text-text-secondary">{r.accord_info.accord}</p>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-text-primary lg:px-6">{r.accord_info.droits}%</td>
                    <td className="px-4 py-3 lg:px-6">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-14 overflow-hidden rounded-full bg-secondary">
                          <div className="h-full rounded-full bg-primary-600" style={{ width: `${(r.logistique.lpi / 5) * 100}%` }} />
                        </div>
                        <span className="text-xs text-text-muted">{r.logistique.lpi.toFixed(2)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-text-muted lg:px-6">{formatInteger(r.logistique.distance_km)} km</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </PageContainer>
  )
}
