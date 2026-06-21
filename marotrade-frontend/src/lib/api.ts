import { useQuery, useMutation } from '@tanstack/react-query'
import type { MarketResult, RegulatoryAlert, ForecastPoint } from '@/types'
import { MOCK_RESULTS, MOCK_ALERTS, MOCK_FORECAST } from './mock-data'
import { getStoredLocale } from './i18n'
import { localizeBackendPayload } from './i18n/backend-localization'
import { useI18n } from './i18n'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// --- API Fetchers ---

export async function fetchScore(payload: { hs_code: string; product_name: string; top_n: number; force_refresh?: boolean }): Promise<MarketResult[]> {
  try {
    const res = await fetch(`${API_URL}/api/score`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'Accept-Language': getStoredLocale() },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('API Error')
    return localizeBackendPayload(await res.json(), getStoredLocale())
  } catch (err) {
    console.warn("API injoignable, utilisation des données MOCK.", err)
    return MOCK_RESULTS.slice(0, payload.top_n)
  }
}

export async function fetchAlerts(
  hs_code: string,
  product_name: string,
  target_countries: string[],
  force_refresh = false
): Promise<RegulatoryAlert[]> {
  try {
    const res = await fetch(`${API_URL}/api/alerts`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'Accept-Language': getStoredLocale() },
      body: JSON.stringify({ hs_code, product_name, target_countries, force_refresh })
    })
    if (!res.ok) throw new Error('API Error')
    return localizeBackendPayload(await res.json(), getStoredLocale())
  } catch (err) {
    console.warn("API injoignable, utilisation des données MOCK.", err)
    const isDemoArgan = hs_code === '151590' || product_name.toLowerCase().includes('argan')
    return isDemoArgan ? MOCK_ALERTS : []
  }
}

export async function fetchForecast(hs_code: string, country: string): Promise<ForecastPoint[]> {
  try {
    const res = await fetch(`${API_URL}/api/forecast?hs_code=${hs_code}&country=${country}`, {
      credentials: 'include',
      headers: { 'Accept-Language': getStoredLocale() },
    })
    if (!res.ok) throw new Error('API Error')
    const data = await res.json()
    return localizeBackendPayload(data.points, getStoredLocale())
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
  const { locale } = useI18n()
  return useQuery({
    queryKey: ['alerts', hs_code, product_name, target_countries.join(','), locale],
    queryFn: () => fetchAlerts(hs_code, product_name, target_countries),
    enabled: target_countries.length > 0
  })
}

export function useMarketForecast(hs_code: string, country: string) {
  const { locale } = useI18n()
  return useQuery({
    queryKey: ['forecast', hs_code, country, locale],
    queryFn: () => fetchForecast(hs_code, country),
    enabled: !!country && !!hs_code
  })
}
