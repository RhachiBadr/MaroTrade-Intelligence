import { cn } from '@/lib/utils'

interface Props {
  cagr: number
  className?: string
}

/** Arrow indicator showing CAGR trend */
export function TrendArrow({ cagr, className }: Props) {
  const positive = cagr >= 0
  return (
    <span className={cn('inline-flex items-center gap-1 text-sm font-medium', positive ? 'text-export-500' : 'text-red-500', className)}>
      <span>{positive ? '↑' : '↓'}</span>
      <span>{Math.abs(cagr).toFixed(1)}%/an</span>
    </span>
  )
}
