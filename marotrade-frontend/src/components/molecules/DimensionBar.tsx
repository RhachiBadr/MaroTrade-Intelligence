'use client'
import { cn } from '@/lib/utils'

interface Props {
  nom:            string
  score:          number
  interpretation?: string
  className?:     string
}

/** Progress bar for a single scoring dimension */
export function DimensionBar({ nom, score, interpretation, className }: Props) {
  const pct = Math.round(score)
  
  const barColor = 
    score >= 70 ? 'bg-success shadow-[0_0_12px_rgba(22,163,74,0.15)]' : 
    score >= 50 ? 'bg-warning shadow-[0_0_12px_rgba(245,158,11,0.15)]' : 
    'bg-danger shadow-[0_0_12px_rgba(220,38,38,0.15)]'

  const textColor = 
    score >= 70 ? 'text-success' : 
    score >= 50 ? 'text-warning' : 
    'text-danger'

  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center justify-between text-xs font-black uppercase tracking-[0.1em]">
        <span className="text-text-primary">{nom}</span>
        <span className={cn('font-mono tabular-nums', textColor)}>{pct} / 100</span>
      </div>
      <div className="h-2 rounded-full bg-secondary overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-1000 ease-out',
            barColor
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {interpretation && (
        <p className="text-[11px] font-bold text-text-muted leading-tight pl-1 opacity-80 italic">
          {interpretation}
        </p>
      )}
    </div>
  )
}
