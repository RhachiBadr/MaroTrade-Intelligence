import { cn, scoreColor } from '@/lib/utils'

interface Props {
  score: number
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

/** Coloured badge displaying a 0–100 score */
export function ScoreBadge({ score, size = 'md', className }: Props) {
  const sizes = { sm: 'px-2 py-0.5 text-xs', md: 'px-3 py-1 text-sm font-semibold', lg: 'px-4 py-2 text-lg font-bold' }
  return (
    <span className={cn('rounded-full tabular-nums', scoreColor(score), sizes[size], className)}>
      {Math.round(score)}<span className="opacity-70 text-[0.7em]">/100</span>
    </span>
  )
}
