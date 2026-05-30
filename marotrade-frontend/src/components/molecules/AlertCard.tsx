'use client'
import { cn } from '@/lib/utils'
import type { RegulatoryAlert } from '@/types'
import {
  Calendar,
  AlertCircle,
  Info,
  AlertTriangle,
  ExternalLink,
  CheckCircle2,
  BrainCircuit,
  Gauge,
  Tags,
} from 'lucide-react'

interface Props {
  alert: RegulatoryAlert
  className?: string
}

/** Card for a single regulatory alert */
export function AlertCard({ alert, className }: Props) {
  const {
    titre,
    niveau,
    source,
    date,
    resume,
    action,
    url,
    score_impact,
    delai_jours,
    llm_enhanced,
    confidence,
    impact_score,
    keywords,
    reasoning,
    resume_fr,
    nlp_enhanced,
    raw_nlp_level,
    calibration_reason,
    category,
    classification,
    origin,
    relevance,
    product_match,
  } = alert
  const displayedImpact = Math.round(impact_score ?? score_impact ?? 0)
  const displayedConfidence = typeof confidence === 'number' ? Math.round(confidence * 100) : null
  const displayedSummary = resume_fr || resume
  const displayedKeywords = Array.isArray(keywords) ? keywords.filter(Boolean).slice(0, 4) : []
  const displayedDelay = typeof delai_jours === 'number' ? delai_jours : Number(delai_jours || 0)
  const hasAdjustedLevel = raw_nlp_level && raw_nlp_level !== niveau
  const analysisInsight = (() => {
    const calibration = (calibration_reason || '').toLowerCase()
    if (product_match === false && calibration.includes('hors produit')) {
      return 'Priorité ajustée : alerte sanitaire détectée, mais le produit surveillé est hors périmètre.'
    }
    if (calibration.includes('faible pertinence')) {
      return 'Priorité ajustée : impact limité pour ce produit et ces marchés.'
    }
    if (calibration.includes('notification informative')) {
      return 'Priorité ajustée : notification informative à surveiller sans action immédiate.'
    }
    if (hasAdjustedLevel) {
      return `Priorité ajustée : le modèle a proposé ${raw_nlp_level}, corrigé en ${niveau} selon la pertinence export.`
    }
    if (reasoning) {
      return 'Analyse IA confirmée par les métadonnées réglementaires et le contexte export.'
    }
    return ''
  })()

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

        {(llm_enhanced || nlp_enhanced) && (
          <div className="px-3 py-1 rounded-full bg-secondary text-[10px] font-black text-text-muted uppercase tracking-widest flex items-center gap-2">
            <BrainCircuit className="h-3 w-3" />
            NLP enrichi
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
        {displayedSummary}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-border/50">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Impact Score</span>
            <span className="text-sm font-black text-text-primary">{displayedImpact}/100</span>
          </div>

          {displayedConfidence !== null && (
            <div className="flex flex-col border-l border-border pl-4">
              <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Confiance NLP</span>
              <span className="flex items-center gap-1 text-sm font-black text-text-primary">
                <Gauge className="h-3.5 w-3.5 text-primary" />
                {displayedConfidence}%
              </span>
            </div>
          )}

          {displayedKeywords.length > 0 && (
            <div className="hidden flex-col border-l border-border pl-4 sm:flex">
              <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Signaux</span>
              <span className="flex items-center gap-1 text-xs font-bold text-text-secondary">
                <Tags className="h-3.5 w-3.5 text-text-muted" />
                {displayedKeywords.join(', ')}
              </span>
            </div>
          )}

          {typeof relevance === 'number' && relevance > 0 && (
            <div className="flex flex-col border-l border-border pl-4">
              <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Pertinence</span>
              <span className="text-sm font-black text-text-primary">{Math.round(relevance)}/100</span>
            </div>
          )}

          {displayedDelay > 0 && (
            <div className="flex flex-col border-l border-border pl-4">
              <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter mb-0.5">Délai estimé</span>
              <span className="text-sm font-black text-warning flex items-center gap-1">
                {displayedDelay} jours
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

      {analysisInsight && (
        <div className="mt-4 rounded-lg border border-primary/15 bg-primary/5 p-4">
          <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-primary">Analyse IA</span>
          <p className="text-xs font-medium leading-normal text-text-secondary">{analysisInsight}</p>
        </div>
      )}

      {(category || classification || origin || raw_nlp_level || calibration_reason || typeof product_match === 'boolean') && (
        <div className="mt-4 grid gap-2 rounded-lg border border-border bg-background/60 p-4 text-xs text-text-secondary sm:grid-cols-2">
          {category && <span><strong className="text-text-primary">Catégorie :</strong> {category}</span>}
          {classification && <span><strong className="text-text-primary">Notification :</strong> {classification}</span>}
          {origin && <span><strong className="text-text-primary">Origine :</strong> {origin}</span>}
          {typeof product_match === 'boolean' && (
            <span><strong className="text-text-primary">Produit :</strong> {product_match ? 'correspondant' : 'hors périmètre'}</span>
          )}
          {hasAdjustedLevel && (
            <span><strong className="text-text-primary">NLP brut :</strong> {raw_nlp_level}</span>
          )}
        </div>
      )}
    </div>
  )
}
