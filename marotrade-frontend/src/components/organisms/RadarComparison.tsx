'use client'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { MarketResult } from '@/types'

const COLORS = ['#2563EB', '#16A34A', '#8B5CF6', '#F59E0B', '#DC2626']

interface Props {
  results:   MarketResult[]
  className?: string
}

/** Radar chart comparing 6 dimensions across top-5 markets */
export function RadarComparison({ results }: Props) {
  const dims = results[0]?.dimensions.map((d) => d.nom) ?? []

  const chartData = dims.map((nom) => {
    const row: Record<string, string | number> = { subject: nom.replace('Potentiel de marché', 'Marché').replace('Facilité des affaires', 'Business').replace('Stabilité & risque pays', 'Stabilité').replace('Diaspora marocaine (MRE)', 'Diaspora').replace('Logistique & transport', 'Logistique') }
    results.forEach((r) => {
      const dim = r.dimensions.find((d) => d.nom === nom)
      row[r.country.name] = dim?.score ?? 0
    })
    return row
  })

  return (
    <ResponsiveContainer width="100%" height={340}>
      <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid className="stroke-border" radialLines={false} />
        <PolarAngleAxis 
          dataKey="subject" 
          tick={{ fontSize: 10, fill: '#64748B', fontWeight: 600, letterSpacing: '0.05em' }} 
        />
        <PolarRadiusAxis 
          angle={90} 
          domain={[0, 100]} 
          tick={{ fontSize: 9, fill: '#94A3B8' }} 
          axisLine={false} 
          tickLine={false} 
        />
        {results.map((r, i) => (
          <Radar
            key={r.country.code}
            name={`${r.country.flag} ${r.country.name}`}
            dataKey={r.country.name}
            stroke={COLORS[i]}
            fill={COLORS[i]}
            fillOpacity={0.06}
            strokeWidth={3}
          />
        ))}
        <Legend 
          iconType="circle" 
          iconSize={6} 
          wrapperStyle={{ fontSize: '11px', fontWeight: 700, paddingTop: '20px', color: '#475569' }} 
        />
        <Tooltip 
          contentStyle={{ borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
