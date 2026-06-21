import type { Locale } from './messages'

const mojibake: Array<[RegExp, string]> = [
  [/marchÃ©/gi, 'marché'], [/rÃ©glement/gi, 'réglement'], [/prÃ©vision/gi, 'prévision'],
  [/donnÃ©e/gi, 'donnée'], [/Ã©levÃ©/gi, 'élevé'], [/Ã©conom/gi, 'économ'],
  [/dÃ©tectÃ©/gi, 'détecté'], [/basÃ©/gi, 'basé'], [/ProximitÃ©/gi, 'Proximité'],
  [/Ã‰tats-Unis/g, 'États-Unis'], [/Ã‰/g, 'É'], [/Ã©/g, 'é'], [/Ã¨/g, 'è'],
  [/Ã /g, 'à'], [/â€”/g, '—'], [/â†’/g, '→'],
]

const english: Array<[RegExp, string]> = [
  [/Demande import significative/gi, 'Significant import demand'],
  [/Marché encore limité en volume/gi, 'Market still limited in volume'],
  [/Dynamique récente favorable/gi, 'Favorable recent momentum'],
  [/Dynamique récente négative/gi, 'Negative recent momentum'],
  [/Tendance 3 ans positive/gi, 'Positive 3-year trend'],
  [/Tendance 3 ans en recul/gi, 'Declining 3-year trend'],
  [/Accord commercial favorable avec droits de douane nuls/gi, 'Favorable trade agreement with zero customs duties'],
  [/Droits de douane élevés/gi, 'High customs duties'],
  [/Risque pays faible selon le profil OCDE/gi, 'Low country risk according to the OECD profile'],
  [/Risque pays élevé selon le profil OCDE/gi, 'High country risk according to the OECD profile'],
  [/Proximité logistique favorable/gi, 'Favorable logistical proximity'],
  [/Distance logistique importante/gi, 'Significant logistical distance'],
  [/Certaines données macro récentes sont manquantes, score calculé avec fallback/gi, 'Some recent macroeconomic data is missing; fallback values were used'],
  [/Aucun frein majeur détecté par les indicateurs v6, à valider commercialement/gi, 'No major barrier detected by v6 indicators; commercial validation is recommended'],
  [/Potentiel de marché/gi, 'Market potential'], [/Accord commercial/gi, 'Trade agreement'],
  [/Facilité des affaires/gi, 'Ease of doing business'], [/Stabilité & risque pays/gi, 'Stability & country risk'],
  [/Logistique & transport/gi, 'Logistics & transport'], [/Tendance & demande/gi, 'Trend & demand'],
  [/Classification CRITIQUE basée sur analyse contextuelle du texte/gi, 'CRITICAL classification based on contextual text analysis'],
]

export function localizeBackendText(value: string, locale: Locale): string {
  const clean = mojibake.reduce((text, [pattern, replacement]) => text.replace(pattern, replacement), value)
  return locale === 'en' ? english.reduce((text, [pattern, replacement]) => text.replace(pattern, replacement), clean) : clean
}

export function localizeBackendPayload<T>(payload: T, locale: Locale): T {
  if (typeof payload === 'string') return localizeBackendText(payload, locale) as T
  if (Array.isArray(payload)) return payload.map(item => localizeBackendPayload(item, locale)) as T
  if (payload && typeof payload === 'object') {
    return Object.fromEntries(Object.entries(payload as Record<string, unknown>)
      .map(([key, value]) => [key, localizeBackendPayload(value, locale)])) as T
  }
  return payload
}
