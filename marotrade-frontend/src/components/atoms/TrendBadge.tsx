import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface TrendBadgeProps {
    value: number
    isPositive?: boolean // can override the value > 0 logic
}

export function TrendBadge({ value, isPositive }: TrendBadgeProps) {
    const isUp = isPositive ?? value > 0

    return (
        <span className={cn(
            'inline-flex items-center gap-1 px-1.5 py-0.5 rounded textxs font-semibold',
            isUp ? 'text-success bg-success/10' : 'text-danger-600 bg-danger-50'
        )}>
            {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {Math.abs(value)}%
        </span>
    )
}
