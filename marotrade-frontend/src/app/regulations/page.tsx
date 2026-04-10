'use client'
import { useState } from 'react'
import { AlertCard } from '@/components/molecules/AlertCard'
import { MOCK_ALERTS } from '@/lib/mock-data'
import type { AlertLevel } from '@/types'
import { Download, ShieldCheck, Sparkles, Filter } from 'lucide-react'
import { cn } from '@/lib/utils'

const LEVELS: AlertLevel[] = ['CRITIQUE', 'ATTENTION', 'INFO']

export default function RegulationsPage() {
  const [levelFilter, setLevelFilter] = useState<AlertLevel[]>(['CRITIQUE','ATTENTION','INFO'])

  const filtered = MOCK_ALERTS.filter(a => levelFilter.includes(a.niveau))
  const critique  = filtered.filter(a => a.niveau === 'CRITIQUE')
  const attention = filtered.filter(a => a.niveau === 'ATTENTION')
  const info      = filtered.filter(a => a.niveau === 'INFO')

  const toggleLevel = (l: AlertLevel) =>
    setLevelFilter(prev => prev.includes(l) ? prev.filter(x => x !== l) : [...prev, l])

  const llmAlerts = MOCK_ALERTS.filter(a => a.llm_enhanced)

  function exportCSV() {
    const rows = [['Niveau','Titre','Source','Date','Impact','Action']]
    MOCK_ALERTS.forEach(a => rows.push([a.niveau, a.titre, a.source, a.date, String(a.score_impact), a.action]))
    const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'alertes_reglementaires_marotrade.csv'; a.click()
  }

  return (
    <div className="max-w-5xl mx-auto space-y-10 py-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-6 pb-6 border-b border-border">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary/10 rounded-xl">
              <ShieldCheck className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-3xl font-extrabold text-text-primary tracking-tight">Veille Réglementaire</h1>
          </div>
          <p className="text-sm font-medium text-text-muted">
            Intelligence en temps réel : <span className="text-text-secondary">EUR-Lex · RASFF · WTO · FDA</span>
          </p>
        </div>
        <button 
          onClick={exportCSV} 
          className="flex items-center gap-2 px-5 py-2.5 bg-white border border-border rounded-xl text-sm font-bold text-text-secondary hover:border-primary/30 transition-all shadow-sm"
        >
          <Download className="w-4 h-4" />
          Exporter CSV
        </button>
      </div>

      {/* LLM Brief */}
      {llmAlerts.length > 0 && (
        <div className="relative overflow-hidden bg-white border border-border rounded-[2rem] p-8 shadow-sm group">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
            <Sparkles className="w-32 h-32 text-primary" />
          </div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                <Sparkles className="w-3 h-3" />
                Brief Exécutif IA
              </div>
              <span className="text-xs font-bold text-text-muted">Analyse par Claude 3.5 Haiku</span>
            </div>
            
            <p className="text-base text-text-secondary leading-relaxed font-medium">
              <span className="text-text-primary font-bold decoration-primary/30 underline decoration-2 underline-offset-4">Priorité stratégique :</span> La certification Halal SFDA (impact 95/100) bloque toute exportation alimentaire vers l'Arabie Saoudite — à traiter en premier.
              Le règlement EUDR anti-déforestation nécessite une traçabilité géographique des parcelles avant janvier 2025.
              Côté USA, l'enregistrement FDA (FSMA) est obligatoire et gratuit — à effectuer dès maintenant pour sécuriser vos flux.
            </p>
          </div>
        </div>
      )}

      {/* Filters & Content */}
      <div className="space-y-8">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-black text-text-muted uppercase tracking-widest mr-2">
            <Filter className="w-3 h-3" />
            Filtrer par sévérité :
          </div>
          <div className="flex gap-2">
            {LEVELS.map(l => (
              <button key={l} onClick={() => toggleLevel(l)}
                className={cn(
                  "text-[10px] px-4 py-2 rounded-full border font-black uppercase tracking-widest transition-all",
                  levelFilter.includes(l)
                    ? l === 'CRITIQUE' ? 'bg-danger text-white border-danger shadow-lg shadow-danger/20'
                      : l === 'ATTENTION' ? 'bg-warning text-white border-warning shadow-lg shadow-warning/20'
                      : 'bg-success text-white border-success shadow-lg shadow-success/20'
                    : 'bg-white border-border text-text-muted hover:border-text-secondary'
                )}>
                {l} ({MOCK_ALERTS.filter(a => a.niveau === l).length})
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="bg-white border border-border border-dashed rounded-[2rem] py-20 text-center animate-in fade-in duration-500">
            <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheck className="w-8 h-8 text-success" />
            </div>
            <p className="text-lg font-bold text-text-primary">Conformité Totale</p>
            <p className="text-sm text-text-muted font-medium">Aucune alerte détectée pour vos critères actuels.</p>
          </div>
        ) : (
          <div className="space-y-12">
            {critique.length > 0 && (
              <section className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="text-xs font-black text-danger uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-danger animate-pulse" />
                    Critiques — Action Immédiate Required
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
                  <h2 className="text-xs font-black text-warning uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-warning" />
                    Attention — Risques Potentiels
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
                  <h2 className="text-xs font-black text-success uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-success" />
                    Informations & Veille Active
                  </h2>
                  <div className="h-px flex-1 bg-success/10" />
                </div>
                <div className="grid gap-4">
                  {info.map(a => <AlertCard key={a.id} alert={a} />)}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
