'use client'
import { Plus, MoreVertical, FileText, ArrowRight } from 'lucide-react'
import { TrendBadge } from '@/components/atoms/TrendBadge'
import { AlertBadge } from '@/components/atoms/AlertBadge'
import { CountryFlag } from '@/components/atoms/CountryFlag'
import { ScoreCard } from '@/components/atoms/ScoreCard'
import Link from 'next/link'

export default function DashboardPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* 1. Greeting & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Bonjour, Admin 👋</h1>
          <p className="text-sm text-text-muted mt-1">14 Avril 2026 · Votre dernier rapport sur le <strong>Safran (Espagne)</strong> montre un score de 82%.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-surface border border-border hover:bg-background text-text-primary text-sm font-semibold rounded-md transition-colors shadow-sm">
            Rapport PDF
          </button>
          <button className="px-4 py-2 bg-surface border border-border hover:bg-background text-text-primary text-sm font-semibold rounded-md transition-colors shadow-sm">
            Voir mes marchés
          </button>
          <Link href="/analyze" className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-md transition-colors shadow-sm flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Lancer une analyse
          </Link>
        </div>
      </div>

      {/* 2. KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Marchés analysés', value: '42', trend: +12, sparkline: [20, 30, 25, 40, 35, 42] },
          { label: 'Opportunités détectées', value: '18', trend: +3, sparkline: [5, 8, 12, 10, 15, 18] },
          { label: 'Alertes réglementaires', value: '3', trend: -2, isNegativeGood: true, sparkline: [8, 7, 5, 5, 4, 3] },
          { label: 'Score moyen', value: '76%', trend: +4, sparkline: [60, 65, 70, 68, 72, 76] },
        ].map((kpi, i) => (
          <div key={i} className="bg-surface border border-border rounded-lg p-5 shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5 group">
            <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">{kpi.label}</p>
            <div className="flex items-end justify-between">
              <div className="flex flex-col gap-2">
                <span className="text-3xl font-bold text-text-primary">{kpi.value}</span>
                <TrendBadge value={kpi.trend} isPositive={kpi.isNegativeGood ? kpi.trend <= 0 : kpi.trend > 0} />
              </div>
              <div className="w-16 h-8 flex items-end justify-between opacity-40 group-hover:opacity-100 transition-opacity">
                {kpi.sparkline.map((val, idx) => (
                  <div key={idx} className="w-1.5 bg-primary-600 rounded-t-sm" style={{ height: `${(val / Math.max(...kpi.sparkline)) * 100}%` }} />
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 3. Analyses Récentes (Takes 2/3 width) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-text-primary">Analyses récentes</h2>
            <button className="text-sm font-semibold text-primary-600 hover:text-primary-700">Tout voir →</button>
          </div>
          <div className="bg-surface border border-border rounded-lg shadow-sm overflow-hidden">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-background text-xs text-text-muted font-semibold uppercase tracking-wider border-b border-border">
                <tr>
                  <th className="px-5 py-3">Produit</th>
                  <th className="px-5 py-3">Marché</th>
                  <th className="px-5 py-3">Score IA</th>
                  <th className="px-5 py-3">Tendance</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  { product: "Huile d'Argan", market: "États-Unis", code: "US", score: 88, trend: 5, date: "il y a 2h" },
                  { product: "Safran", market: "Espagne", code: "ES", score: 82, trend: 12, date: "Hier" },
                  { product: "Phosphates", market: "Brésil", code: "BR", score: 75, trend: -3, date: "12 Avr" },
                  { product: "Tapis artisanaux", market: "France", code: "FR", score: 62, trend: -1, date: "10 Avr" },
                  { product: "Agrumes", market: "Royaume-Uni", code: "GB", score: 91, trend: 8, date: "08 Avr" },
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-background/50 transition-colors">
                    <td className="px-5 py-4 font-semibold text-text-primary flex items-center gap-2">
                      {row.product}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <CountryFlag code={row.code} name={row.market} />
                        <span className="font-medium text-text-secondary">{row.market}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${row.score > 80 ? 'bg-success' : row.score > 70 ? 'bg-warning-500' : 'bg-danger-600'}`} />
                        <span className="font-bold text-text-primary">{row.score}%</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <TrendBadge value={row.trend} />
                    </td>
                    <td className="px-5 py-4 text-text-muted">{row.date}</td>
                    <td className="px-5 py-4 text-right">
                      <button className="p-1.5 text-text-muted hover:text-text-primary rounded-md hover:bg-border transition-colors">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 4. Alertes & Veille (Takes 1/3 width) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-text-primary">Alertes & Veille</h2>
          </div>
          <div className="bg-surface border border-border rounded-lg shadow-sm p-1 divide-y divide-border">
            {[
              { severity: 'critical', title: 'Nouvelle taxe douanière (USA)', time: 'il y a 4h', desc: '+5% sur les huiles cosmétiques.' },
              { severity: 'warning', title: 'Baisse de demande (FR)', time: 'il y a 1j', desc: 'Chute de 12% des requêtes import sur le safran.' },
              { severity: 'info', title: 'Accord de libre-échange (UK)', time: '12 Avr', desc: 'Nouveau quota pour les agrumes marocains.' },
            ].map((alert, i) => (
              <div key={i} className="p-4 hover:bg-background/50 transition-colors group">
                <div className="flex items-start justify-between mb-1">
                  <AlertBadge severity={alert.severity as 'critical' | 'warning' | 'info'} label={alert.severity === 'critical' ? 'Urgent' : alert.severity === 'warning' ? 'Attention' : 'Veille'} />
                  <span className="text-[10px] font-semibold text-text-muted">{alert.time}</span>
                </div>
                <h3 className="text-sm font-semibold text-text-primary mt-2">{alert.title}</h3>
                <p className="text-xs text-text-secondary mt-1">{alert.desc}</p>
                <button className="text-xs font-semibold text-primary-600 mt-3 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">Voir détails <ArrowRight className="w-3 h-3" /></button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 5. Top Marchés Recommandés */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-text-primary">Top Marchés Recommandés</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { market: 'États-Unis', code: 'US', score: 88, desc: ["Demande en hausse de 15%", "Faible barrière douanière"] },
            { market: 'Allemagne', code: 'DE', score: 84, desc: ["Achat direct B2B privilégié", "Forte marge potentielle"] },
            { market: 'Émirats (EAU)', code: 'AE', score: 79, desc: ["Hub régional logistique", "Exonération de TVA applicable"] },
          ].map((market, i) => (
            <div key={i} className="bg-surface border border-border rounded-lg p-5 shadow-sm hover:shadow-md transition-all flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <CountryFlag code={market.code} name={market.market} />
                  <h3 className="font-bold text-text-primary">{market.market}</h3>
                </div>
                <ScoreCard score={market.score} />
              </div>
              <ul className="space-y-2 mt-auto">
                {market.desc.map((d, j) => (
                  <li key={j} className="text-xs font-medium text-text-secondary flex items-start gap-2">
                    <span className="text-accent w-3 h-3 shrink-0">✓</span> {d}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
