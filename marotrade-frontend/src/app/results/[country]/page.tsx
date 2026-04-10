'use client'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useAnalysisStore } from '@/store/analysis'
import { MOCK_RESULTS, MOCK_FORECAST } from '@/lib/mock-data'
import { ScoreBadge } from '@/components/atoms/ScoreBadge'
import { DimensionBar } from '@/components/molecules/DimensionBar'
import { ShapWaterfall } from '@/components/organisms/ShapWaterfall'
import { ForecastChart } from '@/components/organisms/ForecastChart'
import { ChevronRight, Globe, ShieldCheck, Ship, Box, Target, Info, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function CountryDetailPage() {
  const { country: countryParam } = useParams<{ country: string }>()
  const { results: storeResults, expertMode } = useAnalysisStore()
  const results = storeResults.length ? storeResults : MOCK_RESULTS
  const result = results.find(r => r.country.code.toLowerCase() === countryParam) ?? results[0]

  if (!result) return <div className="p-20 text-center text-text-muted font-bold">Pays non trouvé.</div>

  const { country, score_final, dimensions, shap_values, top_atouts, top_risques, accord_info, logistique, forecast } = result

  return (
    <div className="max-w-6xl mx-auto space-y-10 py-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-text-muted">
        <Link href="/" className="hover:text-primary transition-colors">Accueil</Link>
        <ChevronRight className="w-3 h-3 opacity-30" />
        <Link href="/results" className="hover:text-primary transition-colors">Résultats d'Analyse</Link>
        <ChevronRight className="w-3 h-3 opacity-30" />
        <span className="text-text-primary">{country.name}</span>
      </nav>

      {/* Hero Header */}
      <div className="relative overflow-hidden bg-white border border-border rounded-[2.5rem] p-10 shadow-[0_8px_30px_rgb(0,0,0,0.02)] group">
        <div className="absolute top-0 right-0 p-10 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity">
          <Globe className="w-64 h-64 text-primary" />
        </div>
        
        <div className="relative flex flex-wrap items-center gap-10">
          <div className="text-8xl p-4 bg-secondary/50 rounded-3xl group-hover:scale-110 transition-transform duration-500">
            {country.flag}
          </div>
          
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <h1 className="text-5xl font-extrabold text-text-primary tracking-tighter">{country.name}</h1>
              <div className="px-3 py-1 bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest rounded-full">
                Marché Prioritaire
              </div>
            </div>
            
            <p className="text-xl font-medium text-text-secondary max-w-2xl leading-relaxed">
              {accord_info.accord} — <span className="text-primary font-bold">Droits à l'import : {accord_info.droits}%</span>
            </p>
            
            {forecast && (
              <div className="flex items-center gap-6 pt-2">
                <div className="flex items-center gap-2 text-sm font-bold text-success">
                  <TrendingUp className="w-4 h-4" />
                  +{(forecast.cagr_prevu).toFixed(1)}%/an (CAGR)
                </div>
                <div className="h-4 w-px bg-border" />
                <div className="text-sm font-bold text-text-muted">
                  Prévision 2026 : <span className="text-text-primary">{(forecast.valeur_2026).toFixed(1)}M USD</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex flex-col items-center gap-2">
            <ScoreBadge score={score_final} size="lg" className="text-4xl w-32 h-32 rounded-[2rem] shadow-xl shadow-primary/10" />
            <span className="text-[10px] font-black text-text-muted uppercase tracking-widest">Score Final IA</span>
          </div>
        </div>
      </div>

      {/* Strategic Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Dimensions & Logistics */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Facts */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Export Potential', value: 'High', icon: <Target className="w-4 h-4" />, color: 'primary' },
              { label: 'Logistique (LPI)', value: `${logistique.lpi.toFixed(2)}/5`, icon: <Box className="w-4 h-4" />, color: 'secondary' },
              { label: 'Distance Mer', value: `${logistique.distance_km.toLocaleString()} km`, icon: <Ship className="w-4 h-4" />, color: 'secondary' },
              { label: 'Risque Pays', value: 'Low', icon: <ShieldCheck className="w-4 h-4" />, color: 'success' },
            ].map((fact) => (
              <div key={fact.label} className="bg-white border border-border transition-all hover:border-primary/30 p-5 rounded-3xl shadow-sm">
                <div className="flex items-center gap-2 text-text-muted mb-3">
                  {fact.icon}
                  <span className="text-[9px] font-black uppercase tracking-widest">{fact.label}</span>
                </div>
                <p className="text-lg font-black text-text-primary">{fact.value}</p>
              </div>
            ))}
          </div>

          {/* Scores Detail */}
          <div className="bg-white border border-border rounded-[2.5rem] p-10 shadow-sm space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-text-primary flex items-center gap-3">
                <Target className="w-5 h-5 text-primary" />
                Détail des Performances
              </h2>
              <span className="text-[10px] font-black text-text-muted uppercase tracking-widest">6 Dimensions Stratégiques</span>
            </div>
            <div className="grid gap-6">
              {dimensions.map((d) => (
                <DimensionBar key={d.nom} nom={d.nom} score={d.score} interpretation={d.interpretation} />
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Context */}
        <div className="space-y-8">
          {/* Atouts */}
          <div className="bg-white border border-success/20 rounded-[2.5rem] p-8 shadow-sm">
            <h3 className="text-sm font-black text-success uppercase tracking-[0.15em] mb-6 flex items-center gap-2">
              <CheckCircle size={16} className="text-success" />
              Atouts Compétitifs
            </h3>
            <ul className="space-y-4">
              {top_atouts.map((a, i) => (
                <li key={i} className="flex gap-3 text-sm font-bold text-text-secondary leading-tight animate-in slide-in-from-right duration-500" style={{ animationDelay: `${i*100}ms` }}>
                  <div className="w-1.5 h-1.5 rounded-full bg-success mt-1.5 flex-shrink-0" />
                  {a}
                </li>
              ))}
            </ul>
          </div>

          {/* Risques */}
          {top_risques.length > 0 && (
            <div className="bg-white border border-warning/20 rounded-[2.5rem] p-8 shadow-sm">
              <h3 className="text-sm font-black text-warning uppercase tracking-[0.15em] mb-6 flex items-center gap-2">
                <AlertTriangle size={16} className="text-warning" />
                Vigilance Requise
              </h3>
              <ul className="space-y-4">
                {top_risques.map((r, i) => (
                  <li key={i} className="flex gap-3 text-sm font-bold text-text-secondary leading-tight" style={{ animationDelay: `${i*100}ms` }}>
                    <div className="w-1.5 h-1.5 rounded-full bg-warning mt-1.5 flex-shrink-0" />
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Expert Mode Banner */}
          {!expertMode && (
            <div className="bg-secondary/30 rounded-[2rem] p-8 text-center border-2 border-dashed border-border/50">
              <Sparkles className="w-8 h-8 text-primary mx-auto mb-4 animate-pulse" />
              <p className="text-xs font-black text-text-secondary uppercase tracking-widest mb-2">Vues Avancées</p>
              <p className="text-sm font-medium text-text-muted leading-relaxed">
                Activez le <strong>Mode Expert</strong> pour débloquer les contributions SHAP et les prévisions Prophet.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Expert Section */}
      {expertMode && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-10 duration-1000">
          <div className="bg-white border border-border rounded-[2.5rem] p-10 shadow-sm">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold text-text-primary flex items-center gap-3">
                <Info className="w-5 h-5 text-primary" />
                Explicabilité SHAP
              </h2>
              <span className="text-[10px] font-black text-text-muted uppercase tracking-widest">Impact sur le score</span>
            </div>
            <ShapWaterfall shapValues={shap_values} />
          </div>
          
          <div className="bg-white border border-border rounded-[2.5rem] p-10 shadow-sm">
            <h2 className="text-xl font-bold text-text-primary mb-8 flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-primary" />
              Projection Prophet
            </h2>
            <ForecastChart data={MOCK_FORECAST} />
          </div>
        </div>
      )}
    </div>
  )
}

function CheckCircle({ size, className }: { size?: number, className?: string }) {
  return (
    <svg width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
