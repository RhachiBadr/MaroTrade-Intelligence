import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

const variants = {
  default: 'bg-surface-elevated text-text-secondary border-border',
  primary: 'bg-primary-500/10 text-primary-400 border-primary-500/20',
  success: 'bg-success-muted text-success border-success/20',
  warning: 'bg-warning/10 text-warning border-warning/20',
  danger: 'bg-danger/10 text-danger border-danger/20',
}

export function Badge({
  className,
  variant = 'default',
  ...props
}: HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className
      )}
      {...props}
    />
  )
}
