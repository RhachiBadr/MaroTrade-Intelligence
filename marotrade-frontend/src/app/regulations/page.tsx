'use client'
import { useMemo, useState } from 'react'
import { AlertCard } from '@/components/molecules/AlertCard'
import { fetchAlerts, useRegulatoryAlerts } from '@/lib/api'
import { MOCK_ALERTS } from '@/lib/mock-data'
import type { AlertLevel } from '@/types'
import { ArrowDownWideNarrow, CalendarDays, Download, ShieldCheck, Sparkles, Filter, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { Button } from '@/components/ui/button'
import { useAnalysisStore } from '@/store/analysis'
import { useQueryClient } from '@tanstack/react-query'
import { useI18n } from '@/lib/i18n'
import { isAlertInPeriod, parseAlertDate, type AlertPeriod } from '@/lib/regulations/alert-date'
import { useSearchParams } from 'next/navigation'

const LEVELS: AlertLevel[] = ['CRITIQUE', 'ATTENTION', 'INFO']

export default function RegulationsPage() {
  const { t, locale } = useI18n()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const params = useAnalysisStore((s) => s.params)
  const results = useAnalysisStore((s) => s.results)
  const [levelFilter, setLevelFilter] = useState<AlertLevel[]>(['CRITIQUE', 'ATTENTION', 'INFO'])
  const [isForceRefreshing, setIsForceRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [period, setPeriod] = useState<AlertPeriod>('all')
  const [customStart, setCustomStart] = useState('')
  const [customEnd, setCustomEnd] = useState('')

  const queryProductName = searchParams.get('product_name')?.trim()
  const queryHsCode = searchParams.get('hs_code')?.trim()
  const queryCountries = searchParams.get('countries')
    ?.split(',')
    .map((country) => country.trim().toUpperCase())
    .filter(Boolean)

  const hsCode = queryHsCode || params?.hs_code || '151590'
  const productName = queryProductName || params?.product_name || 'Huile argan'
  const targetCountries = queryCountries?.length
    ? queryCountries
    : results.length > 0
      ? results.slice(0, 5).map((r) => r.country.code)
      : ['FRA']

  const { data: liveAlerts, isFetching, isError } = useRegulatoryAlerts(hsCode, productName, targetCountries)
  const alertsQueryKey = ['alerts', hsCode, productName, targetCountries.join(','), locale]
  const alerts = Array.isArray(liveAlerts) ? liveAlerts : MOCK_ALERTS
  const chronologicalAlerts = useMemo(() => [...alerts].sort((a, b) => {
    const aTime = parseAlertDate(a.date)?.getTime() ?? Number.NEGATIVE_INFINITY
    const bTime = parseAlertDate(b.date)?.getTime() ?? Number.NEGATIVE_INFINITY
    return bTime - aTime
  }), [alerts])
  const periodAlerts = useMemo(
    () => chronologicalAlerts.filter(alert => isAlertInPeriod(alert.date, period, customStart, customEnd)),
    [chronologicalAlerts, period, customStart, customEnd],
  )
  const filtered = periodAlerts.filter(alert => levelFilter.includes(alert.niveau))

  const toggleLevel = (l: AlertLevel) =>
    setLevelFilter(prev => prev.includes(l) ? prev.filter(x => x !== l) : [...prev, l])

  const llmAlerts = filtered.filter(a => a.llm_enhanced || a.nlp_enhanced)
  const periodOptions: Array<{ id: AlertPeriod; label: string }> = [
    { id: 'all', label: t('regulations.allPeriods') },
    { id: 'today', label: t('regulations.today') },
    { id: 'week', label: t('regulations.thisWeek') },
    { id: 'month', label: t('regulations.thisMonth') },
    { id: 'custom', label: t('regulations.customPeriod') },
  ]

  async function forceRefreshAlerts() {
    setIsForceRefreshing(true)
    try {
      const freshAlerts = await fetchAlerts(hsCode, productName, targetCountries, true)
      queryClient.setQueryData(alertsQueryKey, freshAlerts)
      setLastRefresh(new Date())
    } finally {
      setIsForceRefreshing(false)
    }
  }

  function exportCSV() {
    const rows = [['Niveau', 'Titre', 'Source', 'Date', 'Impact', 'Confiance', 'NLP', 'Action']]
    filtered.forEach(a => rows.push([
      a.niveau,
      a.titre,
      a.source,
      a.date,
      String(a.impact_score ?? a.score_impact),
      String(a.confidence ?? ''),
      String(Boolean(a.nlp_enhanced)),
      a.action,
    ]))
    const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'alertes_reglementaires_marotrade.csv'; a.click()
  }

  return (
    <PageContainer className="max-w-5xl space-y-10 py-2">
      <PageHeader
        title={t('regulations.title')}
        description={t('regulations.subtitle')}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" onClick={forceRefreshAlerts} className="gap-2" disabled={isFetching || isForceRefreshing}>
              <RefreshCw className={cn('h-4 w-4', (isFetching || isForceRefreshing) && 'animate-spin')} />
              {t('common.refresh')}
            </Button>
            <Button type="button" variant="secondary" onClick={exportCSV} className="gap-2">
              <Download className="h-4 w-4" />
              {t('common.exportCsv')}
            </Button>
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3 text-xs font-medium text-text-muted">
        <span className="font-semibold text-text-primary">{filtered.length} / {alerts.length} {t('regulations.visibleAlerts')}</span>
        <span>Produit : {productName}</span>
        <span>HS {hsCode}</span>
        <span className="inline-flex items-center gap-1 text-primary-600">
          <ArrowDownWideNarrow className="h-3.5 w-3.5" />
          {t('regulations.newestFirst')}
        </span>
        <span>Marchés : {targetCountries.join(', ')}</span>
        {isFetching && <span className="text-primary">Lecture du cache Redis...</span>}
        {isForceRefreshing && <span className="text-primary">Actualisation temps réel en cours...</span>}
        {!isFetching && !isForceRefreshing && <span>Cache Redis actif</span>}
        {lastRefresh && <span>Dernière actualisation : {lastRefresh.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>}
        {isError && <span className="text-warning">API indisponible, données de démonstration affichées.</span>}
      </div>

      {/* LLM Brief */}
      {llmAlerts.length > 0 && (
        <div className="group relative overflow-hidden rounded-xl border border-border bg-surface p-6 shadow-sm sm:p-8">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
            <Sparkles className="w-32 h-32 text-primary" />
          </div>

          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-wide text-primary-700 dark:bg-primary-950/40 dark:text-primary-300">
                <Sparkles className="w-3 h-3" />
                {t('regulations.executiveBrief')}
              </div>
              <span className="text-xs font-medium text-text-muted">{t('regulations.assistedAnalysis')}</span>
            </div>

            <p className="text-base font-normal leading-relaxed text-text-secondary">
              <span className="font-semibold text-text-primary">Priorité stratégique :</span> {llmAlerts[0]?.brief_executif || llmAlerts[0]?.reasoning || llmAlerts[0]?.resume_fr || 'Les alertes critiques sont enrichies par le modèle NLP local avec score d’impact, confiance et recommandations actionnables.'}
            </p>
          </div>
        </div>
      )}

      {/* Filters & Content */}
      <div className="space-y-8">
        <div className="space-y-4 rounded-xl border border-border bg-surface p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="mr-1 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-text-muted">
              <CalendarDays className="h-3.5 w-3.5" />
              {t('regulations.filterByPeriod')}
            </div>
            <div className="flex flex-wrap gap-2">
              {periodOptions.map(option => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => setPeriod(option.id)}
                  className={cn(
                    'rounded-lg border px-3 py-2 text-xs font-semibold transition-colors',
                    period === option.id
                      ? 'border-primary-600 bg-primary-600 text-white shadow-sm'
                      : 'border-border bg-background text-text-secondary hover:border-primary-300 hover:text-primary-600',
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {period === 'custom' && (
            <div className="grid gap-3 border-t border-border pt-4 sm:max-w-xl sm:grid-cols-2">
              <label className="space-y-1.5 text-xs font-medium text-text-secondary">
                <span>{t('regulations.startDate')}</span>
                <input
                  type="date"
                  value={customStart}
                  max={customEnd || undefined}
                  onChange={event => setCustomStart(event.target.value)}
                  className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none"
                />
              </label>
              <label className="space-y-1.5 text-xs font-medium text-text-secondary">
                <span>{t('regulations.endDate')}</span>
                <input
                  type="date"
                  value={customEnd}
                  min={customStart || undefined}
                  onChange={event => setCustomEnd(event.target.value)}
                  className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none"
                />
              </label>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
            <div className="mr-1 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-text-muted">
              <Filter className="h-3.5 w-3.5" />
              {t('regulations.filterBySeverity')}
            </div>
            <div className="flex flex-wrap gap-2">
              {LEVELS.map(level => (
                <button
                  key={level}
                  type="button"
                  onClick={() => toggleLevel(level)}
                  className={cn(
                    'rounded-full border px-4 py-2 text-[10px] font-semibold uppercase tracking-wide transition-all',
                    levelFilter.includes(level)
                      ? level === 'CRITIQUE' ? 'border-danger-600 bg-danger-600 text-white shadow-lg shadow-danger-600/20'
                        : level === 'ATTENTION' ? 'border-warning-600 bg-warning-600 text-white shadow-lg shadow-warning-600/20'
                          : 'border-primary-600 bg-primary-600 text-white shadow-lg shadow-primary-600/20'
                      : 'border-border bg-surface text-text-muted hover:border-text-secondary',
                  )}
                >
                  {level} ({periodAlerts.filter(alert => alert.niveau === level).length})
                </button>
              ))}
            </div>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border bg-surface py-16 text-center">
            <div className="w-16 h-16 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheck className="w-8 h-8 text-accent-600" />
            </div>
            <p className="text-lg font-semibold text-text-primary">{t('common.noData')}</p>
            <p className="text-sm text-text-muted font-medium">{t('regulations.noAlertsForPeriod')}</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filtered.map(alert => <AlertCard key={alert.id} alert={alert} />)}
          </div>
        )}
      </div>
    </PageContainer>
  )
}
