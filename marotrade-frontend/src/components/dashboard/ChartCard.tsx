'use client'

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card'
import { cn } from '@/lib/utils'

type ChartCardProps = {
  title: string
  description?: string
  data: Record<string, unknown>[]
  type?: 'area' | 'bar'
  dataKey: string
  xKey: string
  color?: string
  className?: string
}

const tooltipStyle = {
  backgroundColor: 'rgba(10, 10, 15, 0.9)',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '10px',
  fontSize: '12px',
}

export function ChartCard({
  title,
  description,
  data,
  type = 'area',
  dataKey,
  xKey,
  color = '#818cf8',
  className,
}: ChartCardProps) {
  return (
    <GlassCard className={cn('overflow-hidden', className)}>
      <GlassCardHeader>
        <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        {description && <p className="mt-0.5 text-xs text-text-muted">{description}</p>}
      </GlassCardHeader>
      <GlassCardContent className="pt-2">
        <ResponsiveContainer width="100%" height={256}>
          {type === 'area' ? (
            <AreaChart data={data}>
              <defs>
                <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey={xKey} tick={{ fill: '#71717a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#71717a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area
                type="monotone"
                dataKey={dataKey}
                stroke={color}
                strokeWidth={2}
                fill={`url(#grad-${dataKey})`}
              />
            </AreaChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey={xKey} tick={{ fill: '#71717a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#71717a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} opacity={0.85} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </GlassCardContent>
    </GlassCard>
  )
}
