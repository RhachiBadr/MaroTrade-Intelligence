import { cn, levelColor } from '@/lib/utils'
import type { AlertLevel } from '@/types'

interface Props {
  level: AlertLevel
  className?: string
}

const ICONS: Record<AlertLevel, string> = {
  CRITIQUE: '🔴',
  ATTENTION: '🟡',
  INFO: '🟢',
}

/** Alert level badge (CRITIQUE / ATTENTION / INFO) */
export function LevelBadge({ level, className }: Props) {
  const { text } = levelColor(level)
  return (
    <span className={cn('inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border', levelColor(level).border, levelColor(level).bg, text, className)}>
      {ICONS[level]} {level}
    </span>
  )
}
