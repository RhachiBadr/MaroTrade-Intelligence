// ─── Types MaroTrade Intelligence ────────────────────────────────────────────

export type AlertLevel = 'CRITIQUE' | 'ATTENTION' | 'INFO'
export type AccordType = 'ALE' | 'PREF' | 'NPF'

export interface Country {
  code:  string
  name:  string
  flag:  string
}

export interface Dimension {
  nom:            string
  score:          number   // 0–100
  poids:          number
  contribution:   number
  detail:         Record<string, string>
  interpretation: string
}

export interface MarketResult {
  rank:           number
  country:        Country
  score_final:    number
  score_weighted: number
  score_xgboost:  number
  score_ml_v6?:   number | null
  scoring_method?: string
  v6_features_used?: string[]
  v6_explanation?: string
  v6_strengths?: string[]
  v6_risks?: string[]
  v6_feature_snapshot?: Record<string, number | boolean | string>
  data_freshness?: Record<string, string>
  dimensions:     Dimension[]
  shap_values:    Record<string, number>
  top_atouts:     string[]
  top_risques:    string[]
  accord_info:    { accord: string; droits: number; type: AccordType }
  logistique:     { distance_km: number; lpi: number; cout_conteneur: number }
  forecast?:      ForecastSummary
}

export interface ForecastSummary {
  cagr_prevu:  number
  valeur_2026: number
  tendance:    'haussse' | 'stable' | 'baisse'
}

export interface ForecastPoint {
  ds:     string   // date YYYY-MM-DD
  yhat:   number
  yhat_lower: number
  yhat_upper: number
  y?:     number   // valeur réelle historique
}

export interface RegulatoryAlert {
  id:          string
  titre:       string
  niveau:      AlertLevel
  source:      string
  pays:        string
  pays_nom:    string
  date:        string
  resume:      string
  action:      string
  url:         string
  score_impact: number
  delai_jours?:number
  llm_enhanced: boolean
  confidence?: number
  impact_score?: number
  entities?: Record<string, unknown> | Array<Record<string, unknown>>
  keywords?: string[]
  reasoning?: string
  resume_fr?: string
  brief_executif?: string
  nlp_enhanced?: boolean
  raw_nlp_level?: AlertLevel | string
  calibration_reason?: string
  category?: string
  classification?: string
  origin?: string
  relevance?: number
  product_match?: boolean
}

export interface AnalysisParams {
  product_name: string
  hs_code:      string
  top_n:        number
}

export interface HSProduct {
  label:   string
  hs_code: string
}
