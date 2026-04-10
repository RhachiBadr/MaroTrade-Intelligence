'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useAnalysisStore } from '@/store/analysis'
import { MarketCard } from '@/components/molecules/MarketCard'
import { RadarComparison } from '@/components/organisms/RadarComparison'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { MOCK_RESULTS } from '@/lib/mock-data'
import { cn } from '@/lib/utils'
import { ShieldCheck, Globe } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer,
} from 'recharts'

const LEVEL_COLORS = ['#1D9E75','#27BA87','#BA7517','#E24B4A','#991B1B']

export default function ResultsPage() {
  const { results: storeResults, params, expertMode, toggleExpertMode } = useAnalysisStore()
  const results = storeResults.length ? storeResults : MOCK_RESULTS
  const productName = params?.product_name ?? "Huile d'argan bio"
  const hsCode      = params?.hs_code      ?? '151590'

  const [tab, setTab] = useState<'cards'|'radar'|'table'>('cards')

  const barData = results.map((r) => ({ name: `${r.country.flag} ${r.country.name}`, score: r.score_final }))

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-10">
        <div>
          <nav className="flex items-center gap-2 text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            <Link href="/" className="hover:text-primary transition-colors">Accueil</Link>
            <span className="opacity-30">/</span>
            <Link href="/analyze" className="hover:text-primary transition-colors">Analyse</Link>
            <span className="opacity-30">/</span>
            <span className="text-text-secondary">Résultats</span>
          </nav>
          <h1 className="text-3xl font-extrabold text-text-primary tracking-tight">
            {results.length} marchés pour <span className="text-primary">{productName}</span>
            <span className="ml-3 px-2 py-0.5 bg-secondary text-text-muted text-xs font-mono rounded tracking-widest uppercase">HS {hsCode}</span>
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={toggleExpertMode}
            className={cn('text-sm font-bold px-4 py-2 rounded-xl border transition-all', expertMode ? 'bg-text-primary text-white border-text-primary' : 'bg-white border-border text-text-secondary hover:border-primary/30')}>
            {expertMode ? '🔍 Mode Expert' : '📊 Mode Simplifié'}
          </button>
          <Link href="/regulations" className="text-sm font-bold px-4 py-2 rounded-xl bg-white border border-border text-text-secondary hover:border-primary/30 transition-all flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Réglementations
          </Link>
        </div>
      </div>

      {/* Top 5 Summary Cards (Horizontal Scroll on mobile) */}
      <div className="flex gap-4 mb-10 overflow-x-auto pb-4 -mx-1 px-1 no-scrollbar">
        {results.map((r) => (
          <div key={r.country.code} className="min-w-[140px] flex-1 bg-white rounded-2xl border border-border p-4 text-center hover:border-primary/30 transition-all group">
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">{r.country.flag}</div>
            <p className="text-xs font-bold text-text-primary truncate mb-1">{r.country.name}</p>
            <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-3">Rang #{r.rank}</p>
            <div className="flex justify-center">
              <ScoreBadge score={r.score_final} size="sm" />
            </div>
          </div>
        ))}
      </div>

      {/* Modern Tabs (Notion style) */}
      <div className="flex gap-6 border-b border-border mb-8">
        {(['cards','radar','table'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={cn(
              'pb-3 text-sm font-bold transition-all relative', 
              tab === t 
                ? 'text-primary after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-0.5 after:bg-primary' 
                : 'text-text-muted hover:text-text-secondary'
            )}
          >
            {{ cards: 'Fiches détaillées', radar: 'Comparaison 6D', table: 'Vue Table' }[t]}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'cards' && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
          {results.map((r) => (
            <MarketCard key={r.country.code} result={r} expertMode={expertMode} />
          ))}
        </div>
      )}

      {tab === 'radar' && (
        <div className="bg-white rounded-[2rem] border border-border p-8 animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-sm">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-xl font-bold text-text-primary">Analyse Comparative Multi-Dimensions</h2>
            <div className="flex items-center gap-2 text-xs font-bold text-text-muted uppercase tracking-widest">
              <Globe className="w-4 h-4" /> Top 5 Pays
            </div>
          </div>
          <RadarComparison results={results.slice(0, 5)} />
          
          <div className="mt-12 pt-8 border-t border-border">
            <h3 className="text-sm font-bold text-text-muted uppercase tracking-widest mb-6">Score Global Pondéré</h3>
            <div className="h-[250px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} layout="vertical" margin={{ left: -10 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 12, fontWeight: 600, fill: '#475569' }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: '#F1F5F9' }} formatter={(v) => [`${Number(v)}/100`, 'Score']} contentStyle={{ borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="score" radius={[0, 8, 8, 0]} barSize={24}>
                    {barData.map((_, i) => <Cell key={i} fill={LEVEL_COLORS[i] || '#2563EB'} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {tab === 'table' && (
        <div className="bg-white rounded-[2rem] border border-border overflow-hidden animate-in fade-in duration-500 shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-secondary/30 border-b border-border">
                {['Rang','Marché','Score','Accord','Droits','Qualité Log.','Distance'].map((h) => (
                  <th key={h} className="px-6 py-4 text-left text-[10px] font-black text-text-muted uppercase tracking-widest">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {results.map((r) => (
                <tr key={r.country.code} className="hover:bg-secondary/30 transition-colors group">
                  <td className="px-6 py-4 font-bold text-text-muted">#{r.rank}</td>
                  <td className="px-6 py-4">
                    <Link href={`/results/${r.country.code.toLowerCase()}`} className="flex items-center gap-3 group-hover:text-primary transition-colors">
                      <span className="text-2xl">{r.country.flag}</span>
                      <span className="font-bold text-text-primary group-hover:text-primary">{r.country.name}</span>
                    </Link>
                  </td>
                  <td className="px-6 py-4"><ScoreBadge score={r.score_final} size="sm" /></td>
                  <td className="px-6 py-4 max-w-[180px]">
                    <p className="text-xs font-bold text-text-secondary truncate">{r.accord_info.accord}</p>
                  </td>
                  <td className="px-6 py-4 font-mono font-bold text-text-primary">{r.accord_info.droits}%</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${(r.logistique.lpi/5)*100}%` }} />
                      </div>
                      <span className="text-xs font-bold text-text-muted">{r.logistique.lpi.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs font-bold text-text-muted">{r.logistique.distance_km.toLocaleString()} km</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
