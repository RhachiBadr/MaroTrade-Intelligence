'use client'
import { useState } from 'react'
import { AlertCard } from '@/components/molecules/AlertCard'
import { MOCK_ALERTS } from '@/lib/mock-data'
import type { AlertLevel } from '@/types'
import { Download, ShieldCheck, Sparkles, Filter } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { Button } from '@/components/ui/button'

const LEVELS: AlertLevel[] = ['CRITIQUE', 'ATTENTION', 'INFO']

export default function RegulationsPage() {
  const [levelFilter, setLevelFilter] = useState<AlertLevel[]>(['CRITIQUE', 'ATTENTION', 'INFO'])

  const filtered = MOCK_ALERTS.filter(a => levelFilter.includes(a.niveau))
  const critique = filtered.filter(a => a.niveau === 'CRITIQUE')
  const attention = filtered.filter(a => a.niveau === 'ATTENTION')
  const info = filtered.filter(a => a.niveau === 'INFO')

  const toggleLevel = (l: AlertLevel) =>
    setLevelFilter(prev => prev.includes(l) ? prev.filter(x => x !== l) : [...prev, l])

  const llmAlerts = MOCK_ALERTS.filter(a => a.llm_enhanced)

  function exportCSV() {
    const rows = [['Niveau', 'Titre', 'Source', 'Date', 'Impact', 'Action']]
    MOCK_ALERTS.forEach(a => rows.push([a.niveau, a.titre, a.source, a.date, String(a.score_impact), a.action]))
    const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'alertes_reglementaires_marotrade.csv'; a.click()
  }

  return (
    <PageContainer className="max-w-5xl space-y-10 py-2">
      <PageHeader
        title="Veille réglementaire"
        description="Sources : EUR-Lex, RASFF, OMC, FDA — filtrez par niveau de criticité."
        actions={
          <Button type="button" variant="secondary" onClick={exportCSV} className="gap-2">
            <Download className="h-4 w-4" />
            Exporter CSV
          </Button>
        }
      />

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
                Brief Exécutif IA
              </div>
              <span className="text-xs font-medium text-text-muted">Analyse assistée (Claude / pipeline)</span>
            </div>

            <p className="text-base font-normal leading-relaxed text-text-secondary">
              <span className="font-semibold text-text-primary">Priorité stratégique :</span> La certification Halal SFDA (impact 95/100) bloque toute exportation alimentaire vers l&apos;Arabie Saoudite — à traiter en premier.
              Le règlement EUDR anti-déforestation nécessite une traçabilité géographique des parcelles avant janvier 2025.
              Côté USA, l&apos;enregistrement FDA (FSMA) est obligatoire et gratuit — à effectuer dès maintenant pour sécuriser vos flux.
            </p>
          </div>
        </div>
      )}

      {/* Filters & Content */}
      <div className="space-y-8">
        <div className="flex flex-wrap items-center gap-4">
          <div className="mr-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-text-muted">
            <Filter className="w-3 h-3" />
            Filtrer par sévérité :
          </div>
          <div className="flex gap-2">
            {LEVELS.map(l => (
              <button key={l} onClick={() => toggleLevel(l)}
                className={cn(
                  'rounded-full border px-4 py-2 text-[10px] font-semibold uppercase tracking-wide transition-all',
                  levelFilter.includes(l)
                    ? l === 'CRITIQUE' ? 'bg-danger-600 text-white border-danger-600 shadow-lg shadow-danger-600/20'
                      : l === 'ATTENTION' ? 'bg-warning-600 text-white border-warning-600 shadow-lg shadow-warning-600/20'
                        : 'bg-primary-600 text-white border-primary-600 shadow-lg shadow-primary-600/20'
                    : 'bg-surface border-border text-text-muted hover:border-text-secondary'
                )}>
                {l} ({MOCK_ALERTS.filter(a => a.niveau === l).length})
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border bg-surface py-16 text-center">
            <div className="w-16 h-16 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheck className="w-8 h-8 text-accent-600" />
            </div>
            <p className="text-lg font-semibold text-text-primary">Aucune alerte</p>
            <p className="text-sm text-text-muted font-medium">Aucune alerte détectée pour vos critères actuels.</p>
          </div>
        ) : (
          <div className="space-y-12">
            {critique.length > 0 && (
              <section className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-danger-600">
                    <span className="w-2 h-2 rounded-full bg-danger animate-pulse" />
                    Critiques — action immédiate
                  </h2>
                  <div className="h-px flex-1 bg-danger/10" />
                </div>
                <div className="grid gap-4">
                  {critique.map(a => <AlertCard key={a.id} alert={a} />)}
                </div>
              </section>
            )}

            {attention.length > 0 && (
              <section className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-warning-600">
                    <span className="w-2 h-2 rounded-full bg-warning" />
                    Attention — risques à suivre
                  </h2>
                  <div className="h-px flex-1 bg-warning/10" />
                </div>
                <div className="grid gap-4">
                  {attention.map(a => <AlertCard key={a.id} alert={a} />)}
                </div>
              </section>
            )}

            {info.length > 0 && (
              <section className="animate-in fade-in slide-in-from-bottom-6 duration-1000">
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-primary-600">
                    <span className="w-2 h-2 rounded-full bg-primary-600" />
                    Informations
                  </h2>
                  <div className="h-px flex-1 bg-primary-600/10" />
                </div>
                <div className="grid gap-4">
                  {info.map(a => <AlertCard key={a.id} alert={a} />)}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </PageContainer>
  )
}
