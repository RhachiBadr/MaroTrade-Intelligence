'use client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, CartesianGrid } from 'recharts'

interface Props {
  shapValues: Record<string, number>
  className?: string
}

/** SHAP waterfall bar chart (horizontal) */
export function ShapWaterfall({ shapValues }: Props) {
  const entries = Object.entries(shapValues)
    .map(([k, v]) => ({ feature: k, value: v }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

  return (
    <ResponsiveContainer width="100%" height={entries.length * 44 + 60}>
      <BarChart 
        data={entries} 
        layout="vertical" 
        margin={{ left: 10, right: 40, top: 20, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
        <XAxis 
          type="number" 
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}`} 
          tick={{ fontSize: 10, fontWeight: 800, fill: '#94A3B8' }} 
        />
        <YAxis 
          type="category" 
          dataKey="feature" 
          width={180} 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fontWeight: 700, fill: '#475569' }} 
        />
        <Tooltip 
          cursor={{ fill: '#F8FAFC' }}
          contentStyle={{ borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 10px 30px rgba(0,0,0,0.05)' }}
          itemStyle={{ fontSize: '11px', fontWeight: 'bold' }}
          labelStyle={{ fontSize: '10px', fontWeight: 'black', textTransform: 'uppercase', marginBottom: '4px', color: '#94A3B8' }}
          formatter={(v) => { const n = Number(v); return [`${n > 0 ? '+' : ''}${n.toFixed(2)}`, 'Impact Score'] }} 
        />
        <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={24}>
          {entries.map((e, i) => (
            <Cell key={i} fill={e.value >= 0 ? '#16A34A' : '#DC2626'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
