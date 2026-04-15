import { cn } from '@/lib/utils'

export type AlertSeverity = 'critical' | 'warning' | 'info'

interface AlertBadgeProps {
    severity: AlertSeverity
    label: string
}

const variants = {
    critical: 'text-danger-600 bg-danger-50 border-danger-200 dark:bg-danger-500/10 dark:border-danger-500/20 dark:text-danger-500',
    warning: 'text-warning-600 bg-warning-50 border-warning-200 dark:bg-warning-500/10 dark:border-warning-500/20 dark:text-warning-500',
    info: 'text-primary-600 bg-primary-50 border-primary-200 dark:bg-primary-500/10 dark:border-primary-500/20 dark:text-primary-500',
}

const dots = {
    critical: 'bg-danger-600 dark:bg-danger-500',
    warning: 'bg-warning-500 dark:bg-warning-400',
    info: 'bg-primary-600 dark:bg-primary-500',
}

export function AlertBadge({ severity, label }: AlertBadgeProps) {
    return (
        <span className={cn('inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold border', variants[severity])}>
            <span className={cn('w-1.5 h-1.5 rounded-full', dots[severity])} />
            {label}
        </span>
    )
}
