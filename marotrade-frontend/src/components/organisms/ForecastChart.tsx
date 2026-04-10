'use client'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import type { ForecastPoint } from '@/types'

interface Props {
  data:          ForecastPoint[]
  countryName?:  string
  className?:    string
}

/** Prophet forecast chart with shaded 80% confidence interval */
export function ForecastChart({ data }: Props) {
  const formatted = data.map((d) => ({
    year:  d.ds.slice(0, 4),
    yhat:  Math.round(d.yhat / 1e6 * 10) / 10,
    lower: Math.round(d.yhat_lower / 1e6 * 10) / 10,
    upper: Math.round(d.yhat_upper / 1e6 * 10) / 10,
    actual: d.y ? Math.round(d.y / 1e6 * 10) / 10 : undefined,
  }))

  const forecastStart = formatted.find((d) => d.actual === undefined)?.year ?? '2023'

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={formatted} margin={{ top: 20, right: 30, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#2563EB" stopOpacity={0.1} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0.01} />
            </linearGradient>
            <linearGradient id="ciGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#2563EB" stopOpacity={0.05} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="6 6" vertical={false} stroke="#E5E7EB" />
          <XAxis 
            dataKey="year" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 10, fontWeight: 800, fill: '#94A3B8' }}
            dy={15}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tickFormatter={(v) => `${v}M`} 
            tick={{ fontSize: 10, fontWeight: 800, fill: '#94A3B8' }}
          />
          <Tooltip 
            contentStyle={{ borderRadius: '16px', border: '1px solid #E5E7EB', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', padding: '12px' }}
            itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
            labelStyle={{ fontSize: '10px', fontWeight: 'black', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px', color: '#94A3B8' }}
            formatter={(v) => [`${Number(v)}M USD`, 'Valeur']} 
            labelFormatter={(l) => `Année ${l}`} 
          />
          <ReferenceLine 
            x={forecastStart} 
            stroke="#2563EB" 
            strokeWidth={1}
            strokeDasharray="4 4" 
            label={{ value: 'PRÉVISIONS', position: 'insideTopRight', fontSize: 9, fontWeight: 900, fill: '#2563EB', letterSpacing: '0.1em' }} 
          />
          
          {/* Confidence interval area */}
          <Area type="monotone" dataKey="upper" stroke="none" fill="url(#ciGrad)" name="Intervalle sup." />
          <Area type="monotone" dataKey="lower" stroke="none" fill="#FFFFFF" fillOpacity={1} name="Intervalle inf." />
          
          {/* Base Area for yhat */}
          <Area type="monotone" dataKey="yhat" stroke="none" fill="url(#areaGrad)" />

          {/* Actual line */}
          <Area 
            type="monotone" 
            dataKey="actual" 
            stroke="#2563EB" 
            strokeWidth={3} 
            fill="none" 
            dot={{ r: 4, fill: '#2563EB', strokeWidth: 2, stroke: '#FFFFFF' }} 
            activeDot={{ r: 6, strokeWidth: 0 }}
            name="Historique" 
          />
          
          {/* Forecast line */}
          <Area 
            type="monotone" 
            dataKey="yhat" 
            stroke="#2563EB" 
            strokeWidth={3} 
            strokeDasharray="8 4" 
            fill="none" 
            activeDot={{ r: 6, strokeWidth: 0 }}
            name="Prévision" 
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="flex items-center justify-center gap-4 mt-6">
        <div className="flex items-center gap-2 text-[10px] font-black text-text-muted uppercase tracking-widest">
          <div className="w-3 h-0.5 bg-primary" /> Historique (Données réelles)
        </div>
        <div className="flex items-center gap-2 text-[10px] font-black text-text-muted uppercase tracking-widest">
          <div className="w-3 h-0.5 border-t-2 border-primary border-dashed" /> Prédictions IA
        </div>
      </div>
    </div>
  )
}
