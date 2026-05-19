'use client'
import { cn } from '@/lib/utils'
import type { RegulatoryAlert } from '@/types'
import { Calendar, AlertCircle, Info, AlertTriangle, ExternalLink, CheckCircle2 } from 'lucide-react'

interface Props {
  alert: RegulatoryAlert
  className?: string
}

/** Card for a single regulatory alert */
export function AlertCard({ alert, className }: Props) {
  const { titre, niveau, source, date, resume, action, url, score_impact, delai_jours, llm_enhanced } = alert

  const iconMap = {
    CRITIQUE: <AlertCircle className="w-4 h-4 text-danger" />,
    ATTENTION: <AlertTriangle className="w-4 h-4 text-warning" />,
    INFO: <Info className="w-4 h-4 text-primary" />,
  }

  const borderStyles = {
    CRITIQUE: 'border-danger/20 hover:border-danger/40 shadow-danger/5',
    ATTENTION: 'border-warning/20 hover:border-warning/40 shadow-warning/5',
    INFO: 'border-primary/20 hover:border-primary/40 shadow-primary/5',
  }

  return (
    <div className={cn(
      'group rounded-xl border bg-surface p-6 shadow-sm transition-shadow hover:shadow-md',
      borderStyles[niveau],
      className
    )}>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className={cn(
          "px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2",
          niveau === 'CRITIQUE' ? 'bg-danger/10 text-danger' :
            niveau === 'ATTENTION' ? 'bg-warning/10 text-warning' :
              'bg-primary/10 text-primary'
        )}>
          {iconMap[niveau]}
          {niveau}
        </div>

        {llm_enhanced && (
          <div className="px-3 py-1 rounded-full bg-secondary text-[10px] font-black text-text-muted uppercase tracking-widest flex items-center gap-2">
            Enrichi IA
          </div>
        )}

        <div className="ml-auto flex items-center gap-4">
          <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">{source}</span>
          <div className="flex items-center gap-1.5 text-text-muted">
            <Calendar className="w-3 h-3" />
            <span className="text-[10px] font-bold uppercase tracking-widest">{date.slice(0, 10)}</span>
          </div>
        </div>
      </div>

      <h4 className="text-lg font-bold text-text-primary mb-2 group-hover:text-primary transition-colors leading-tight">
        {titre}
      </h4>

      <p className="text-sm text-text-secondary leading-relaxed mb-6 font-medium">
        {resume}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-border/50">
        <div className="flex items-center gap-4">
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Impact Score</span>
            <span className="text-sm font-black text-text-primary">{score_impact}/100</span>
          </div>

          {delai_jours && (
            <div className="flex flex-col border-l border-border pl-4">
              <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Délai estimé</span>
              <span className="text-sm font-black text-warning flex items-center gap-1">
                {delai_jours} jours
              </span>
            </div>
          )}
        </div>

        {url && (
          <a href={url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs font-bold text-text-muted hover:text-primary transition-colors">
            Source officielle
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      {action && (
        <div className="mt-6 flex items-start gap-3 rounded-lg border border-border bg-secondary/50 p-4">
          <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
          <div className="flex flex-col">
            <span className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-success">Recommandation</span>
            <p className="text-xs font-bold text-text-secondary leading-normal">{action}</p>
          </div>
        </div>
      )}
    </div>
  )
}
