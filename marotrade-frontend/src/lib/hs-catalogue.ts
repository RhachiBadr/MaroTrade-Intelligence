import type { HSProduct } from '@/types'

export const HS_CATALOGUE: HSProduct[] = [
  { label: "Huile d'argan",        hs_code: '151590' },
  { label: 'Sardines en conserve', hs_code: '160413' },
  { label: 'Dattes fraiches',      hs_code: '080410' },
  { label: 'Safran',               hs_code: '09102010' },
  { label: 'Cumin',                hs_code: '090920' },
  { label: 'Tapis berbere',        hs_code: '570110' },
  { label: 'Zellige',              hs_code: '691010' },
  { label: 'Articles en cuir',     hs_code: '4205' },
]

/** Search HS products by label or code */
export function searchHS(query: string): HSProduct[] {
  const q = query.toLowerCase()
  return HS_CATALOGUE.filter(
    (product) => product.label.toLowerCase().includes(q) || product.hs_code.includes(q)
  )
}

/** Quick map: product name fragment -> hs_code */
export const HS_NAME_MAP: Record<string, string> = {
  argan: '151590',
  sardine: '160413',
  datte: '080410',
  safran: '09102010',
  cumin: '090920',
  tapis: '570110',
  zellige: '691010',
  cuir: '4205',
  leather: '4205',
}
