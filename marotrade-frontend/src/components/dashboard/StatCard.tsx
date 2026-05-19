'use client'

import { cn } from '@/lib/utils'
import type { Card } from '@/components/ui/card'

type StatCardProps = {
  label: string
  value: string
  change?: number
  trend?: number[]
  className?: string
}

export function StatCard({ label, value, change, trend, className }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0

  return (
    <div
      className={cn(
        'glass group rounded-xl p-5 transition-all duration-300 hover:border-white/15 hover:shadow-lg',
        className
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wider text-text-muted">{label}</p>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div>
          <p className="text-3xl font-semibold tracking-tight text-text-primary">{value}</p>
          {change !== undefined && (
            <p className={cn('mt-1 text-xs font-medium', isPositive ? 'text-success' : 'text-danger')}>
              {isPositive ? '+' : ''}
              {change}% vs mois dernier
            </p>
          )}
        </div>
        {trend && (
          <div className="flex h-10 w-16 items-end justify-between opacity-40 transition-opacity group-hover:opacity-100">
            {trend.map((val, idx) => (
              <div
                key={idx}
                className="w-1.5 rounded-t-sm bg-gradient-to-t from-primary-600 to-primary-400"
                style={{ height: `${(val / Math.max(...trend)) * 100}%` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
