import { useQuery, useMutation } from '@tanstack/react-query'
import type { MarketResult, RegulatoryAlert, ForecastPoint } from '@/types'
import { MOCK_RESULTS, MOCK_ALERTS, MOCK_FORECAST } from './mock-data'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// --- API Fetchers ---

export async function fetchScore(payload: { hs_code: string; product_name: string; top_n: number }): Promise<MarketResult[]> {
  try {
    const res = await fetch(`${API_URL}/api/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('API Error')
    return await res.json()
  } catch (err) {
    console.warn("API injoignable, utilisation des données MOCK.", err)
    return MOCK_RESULTS.slice(0, payload.top_n)
  }
}

export async function fetchAlerts(hs_code: string, product_name: string, target_countries: string[]): Promise<RegulatoryAlert[]> {
  try {
    const res = await fetch(`${API_URL}/api/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hs_code, product_name, target_countries })
    })
    if (!res.ok) throw new Error('API Error')
    return await res.json()
  } catch (err) {
    console.warn("API injoignable, utilisation des données MOCK.", err)
    return MOCK_ALERTS
  }
}

export async function fetchForecast(hs_code: string, country: string): Promise<ForecastPoint[]> {
  try {
    const res = await fetch(`${API_URL}/api/forecast?hs_code=${hs_code}&country=${country}`)
    if (!res.ok) throw new Error('API Error')
    const data = await res.json()
    return data.points
  } catch (err) {
    console.warn("API injoignable, utilisation des données MOCK.", err)
    return MOCK_FORECAST
  }
}

// --- React Query Hooks ---

export function useMarketScore() {
  return useMutation({ mutationFn: fetchScore })
}

export function useRegulatoryAlerts(hs_code: string, product_name: string, target_countries: string[]) {
  return useQuery({
    queryKey: ['alerts', hs_code, target_countries.join(',')],
    queryFn: () => fetchAlerts(hs_code, product_name, target_countries),
    enabled: target_countries.length > 0
  })
}

export function useMarketForecast(hs_code: string, country: string) {
  return useQuery({
    queryKey: ['forecast', hs_code, country],
    queryFn: () => fetchForecast(hs_code, country),
    enabled: !!country && !!hs_code
  })
}
