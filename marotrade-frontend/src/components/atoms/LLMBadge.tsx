import { cn } from '@/lib/utils'

interface Props { className?: string }

/** Purple badge indicating Claude 3.5 Haiku analysis */
export function LLMBadge({ className }: Props) {
  return (
    <span className={cn('inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300 border border-violet-200 dark:border-violet-700', className)}>
      🤖 Claude 3.5 Haiku
    </span>
  )
}
