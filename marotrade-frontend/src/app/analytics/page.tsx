'use client'

import { PageTransition } from '@/components/motion/PageTransition'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { StatCard } from '@/components/dashboard/StatCard'
import { ChartCard } from '@/components/dashboard/ChartCard'
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'

const MONTHLY_ANALYSES = [
  { month: 'Jan', count: 12 },
  { month: 'Fév', count: 18 },
  { month: 'Mar', count: 15 },
  { month: 'Avr', count: 24 },
  { month: 'Mai', count: 31 },
  { month: 'Jun', count: 28 },
]

const MARKET_SCORES = [
  { market: 'FRA', score: 87 },
  { market: 'USA', score: 84 },
  { market: 'DEU', score: 81 },
  { market: 'ESP', score: 78 },
  { market: 'GBR', score: 76 },
  { market: 'ITA', score: 74 },
]

const TOP_PRODUCTS = [
  { product: "Huile d'argan", analyses: 24, avgScore: 86 },
  { product: 'Safran', analyses: 18, avgScore: 82 },
  { product: 'Dattes', analyses: 15, avgScore: 79 },
  { product: 'Sardines', analyses: 12, avgScore: 75 },
  { product: 'Tapis berbère', analyses: 9, avgScore: 71 },
]

export default function AnalyticsPage() {
  return (
    <PageTransition>
      <PageContainer className="space-y-8 pb-8">
        <PageHeader
          title="Analytics"
          description="Métriques d'utilisation, tendances de scoring et performance de la plateforme."
          actions={
            <Button variant="secondary">
              <Download className="h-4 w-4" />
              Exporter
            </Button>
          }
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Analyses ce mois" value="31" change={12} trend={[12, 18, 15, 24, 31]} />
          <StatCard label="Score moyen" value="79.4" change={4} trend={[72, 74, 76, 78, 79]} />
          <StatCard label="Marchés couverts" value="38" change={0} trend={[38, 38, 38, 38, 38]} />
          <StatCard label="Alertes actives" value="7" change={-15} trend={[12, 10, 9, 8, 7]} />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ChartCard
            title="Analyses mensuelles"
            description="Volume d'analyses lancées par mois"
            data={MONTHLY_ANALYSES}
            dataKey="count"
            xKey="month"
            type="area"
          />
          <ChartCard
            title="Scores par marché"
            description="Top 6 marchés — score moyen"
            data={MARKET_SCORES}
            dataKey="score"
            xKey="market"
            type="bar"
            color="#34d399"
          />
        </div>

        <GlassCard>
          <GlassCardContent>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-semibold text-text-primary">Produits les plus analysés</h2>
              <Badge variant="primary">30 derniers jours</Badge>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[480px] text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs font-medium uppercase tracking-wider text-text-muted">
                    <th className="pb-3 pr-4">Produit</th>
                    <th className="pb-3 pr-4">Analyses</th>
                    <th className="pb-3 pr-4">Score moyen</th>
                    <th className="pb-3">Tendance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {TOP_PRODUCTS.map((row) => (
                    <tr key={row.product} className="transition-colors hover:bg-white/[0.02]">
                      <td className="py-3.5 font-medium text-text-primary">{row.product}</td>
                      <td className="py-3.5 text-text-secondary">{row.analyses}</td>
                      <td className="py-3.5">
                        <span className="font-semibold text-text-primary">{row.avgScore}</span>
                      </td>
                      <td className="py-3.5">
                        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-primary-600 to-primary-400"
                            style={{ width: `${row.avgScore}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCardContent>
        </GlassCard>
      </PageContainer>
    </PageTransition>
  )
}
