import { create } from 'zustand'
import type { MarketResult, AnalysisParams } from '@/types'

interface AnalysisStore {
  // Params
  params:          AnalysisParams | null
  setParams:       (p: AnalysisParams) => void

  // Results
  results:         MarketResult[]
  setResults:      (r: MarketResult[]) => void
  clearResults:    () => void

  // UI state
  expertMode:      boolean
  toggleExpertMode: () => void
  selectedCountry: string | null
  setSelectedCountry: (code: string | null) => void
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  params:          null,
  setParams:       (params) => set({ params }),

  results:         [],
  setResults:      (results) => set({ results }),
  clearResults:    () => set({ results: [], params: null }),

  expertMode:      false,
  toggleExpertMode: () => set((s) => ({ expertMode: !s.expertMode })),
  selectedCountry: null,
  setSelectedCountry: (code) => set({ selectedCountry: code }),
}))
