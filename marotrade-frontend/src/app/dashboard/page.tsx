'use client'

import Link from 'next/link'
import { Plus, MoreVertical, ArrowRight } from 'lucide-react'
import { PageTransition } from '@/components/motion/PageTransition'
import { TrendBadge } from '@/components/atoms/TrendBadge'
import { AlertBadge } from '@/components/atoms/AlertBadge'
import { CountryFlag } from '@/components/atoms/CountryFlag'
import { ScoreCard } from '@/components/atoms/ScoreCard'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card'
import { StatCard } from '@/components/dashboard/StatCard'
import { Button } from '@/components/ui/button'
import { AnimatedButton } from '@/components/ui/animated-button'
import { useI18n } from '@/lib/i18n'

export default function DashboardPage() {
  const { t } = useI18n()
  return (
    <PageTransition>
      <PageContainer className="space-y-8 pb-8">
        <PageHeader
          title={t('dashboard.title')}
          description={t('dashboard.subtitle')}
          actions={
            <>
              <Button variant="secondary" type="button" className="hidden sm:inline-flex">
                Exporter
              </Button>
              <AnimatedButton href="/analyze" size="sm">
                <Plus className="h-4 w-4" />
                Nouvelle analyse
              </AnimatedButton>
            </>
          }
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Marchés analysés" value="42" change={12} trend={[20, 30, 25, 40, 42]} />
          <StatCard label="Opportunités" value="18" change={3} trend={[5, 8, 12, 15, 18]} />
          <StatCard label="Alertes actives" value="3" change={-2} trend={[8, 7, 5, 4, 3]} />
          <StatCard label="Score moyen" value="76%" change={4} trend={[60, 65, 70, 72, 76]} />
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-text-primary">{t('dashboard.recentAnalyses')}</h2>
              <Link href="/history" className="text-sm font-medium text-primary-400 hover:text-primary-300">
                Historique
              </Link>
            </div>
            <GlassCard className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead className="border-b border-border text-xs font-medium uppercase tracking-wider text-text-muted">
                    <tr>
                      <th className="px-5 py-3">{t('analysis.product')}</th>
                      <th className="px-5 py-3">{t('analysis.market')}</th>
                      <th className="px-5 py-3">{t('analysis.score')}</th>
                      <th className="px-5 py-3">{t('analysis.growth')}</th>
                      <th className="px-5 py-3">Date</th>
                      <th className="px-5 py-3" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {[
                      { product: "Huile d'Argan", market: 'États-Unis', code: 'US', score: 88, trend: 5, date: 'il y a 2h' },
                      { product: 'Safran', market: 'Espagne', code: 'ES', score: 82, trend: 12, date: 'Hier' },
                      { product: 'Phosphates', market: 'Brésil', code: 'BR', score: 75, trend: -3, date: '12 avr.' },
                      { product: 'Tapis artisanaux', market: 'France', code: 'FR', score: 62, trend: -1, date: '10 avr.' },
                    ].map((row, i) => (
                      <tr key={i} className="transition-colors hover:bg-white/[0.02]">
                        <td className="px-5 py-3.5 font-medium text-text-primary">{row.product}</td>
                        <td className="px-5 py-3.5">
                          <div className="flex items-center gap-2">
                            <CountryFlag code={row.code} name={row.market} />
                            <span className="text-text-secondary">{row.market}</span>
                          </div>
                        </td>
                        <td className="px-5 py-3.5">
                          <div className="flex items-center gap-2">
                            <span
                              className={`h-2 w-2 rounded-full ${
                                row.score > 80 ? 'bg-success' : row.score > 70 ? 'bg-warning-500' : 'bg-danger-600'
                              }`}
                            />
                            <span className="font-semibold text-text-primary">{row.score}%</span>
                          </div>
                        </td>
                        <td className="px-5 py-3.5">
                          <TrendBadge value={row.trend} />
                        </td>
                        <td className="px-5 py-3.5 text-text-muted">{row.date}</td>
                        <td className="px-5 py-3.5 text-right">
                          <button type="button" className="rounded-lg p-1.5 text-text-muted hover:bg-white/5" aria-label="Actions">
                            <MoreVertical className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </GlassCard>
          </div>

          <div className="space-y-4">
            <h2 className="text-base font-semibold text-text-primary">{t('dashboard.regulatoryAlerts')}</h2>
            <GlassCard className="divide-y divide-border">
              {[
                { severity: 'critical' as const, title: 'Mesure douanière (USA)', time: 'il y a 4h', desc: '+5 % sur certaines huiles cosmétiques.' },
                { severity: 'warning' as const, title: 'Demande (FR)', time: 'il y a 1j', desc: 'Baisse des recherches import sur le safran.' },
                { severity: 'info' as const, title: 'Accord UK', time: '12 avr.', desc: 'Nouveau quota agrumes Maroc → UK.' },
              ].map((alert, i) => (
                <div key={i} className="p-4 transition-colors hover:bg-white/[0.02]">
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <AlertBadge severity={alert.severity} label={alert.severity === 'critical' ? 'Urgent' : alert.severity === 'warning' ? 'Attention' : 'Veille'} />
                    <span className="shrink-0 text-[11px] font-medium text-text-muted">{alert.time}</span>
                  </div>
                  <h3 className="text-sm font-semibold text-text-primary">{alert.title}</h3>
                  <p className="mt-1 text-xs leading-relaxed text-text-secondary">{alert.desc}</p>
                  <Link href="/regulations" className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary-400 hover:underline">
                    Détails <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>
              ))}
            </GlassCard>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-base font-semibold text-text-primary">{t('dashboard.recommendedMarkets')}</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {[
              { market: 'États-Unis', code: 'US', score: 88, desc: ['Demande en hausse', 'Cadre douanier stable'] },
              { market: 'Allemagne', code: 'DE', score: 84, desc: ['Achat B2B direct', 'Marge potentielle élevée'] },
              { market: 'Émirats', code: 'AE', score: 79, desc: ['Hub logistique régional', 'Fiscalité compétitive'] },
            ].map((market, i) => (
              <GlassCard key={i}>
                <GlassCardContent className="flex flex-col gap-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <CountryFlag code={market.code} name={market.market} />
                      <h3 className="font-semibold text-text-primary">{market.market}</h3>
                    </div>
                    <ScoreCard score={market.score} />
                  </div>
                  <ul className="space-y-2">
                    {market.desc.map((d, j) => (
                      <li key={j} className="flex items-start gap-2 text-xs font-medium text-text-secondary">
                        <span className="mt-0.5 text-accent-500">✓</span>
                        {d}
                      </li>
                    ))}
                  </ul>
                </GlassCardContent>
              </GlassCard>
            ))}
          </div>
        </div>
      </PageContainer>
    </PageTransition>
  )
}
