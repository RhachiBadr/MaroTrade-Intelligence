import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { MarketResult, AnalysisParams } from '@/types'

export interface HistoryItem {
  id: string
  date: string
  params: AnalysisParams
  results: MarketResult[]
  topScore: number
}

interface AnalysisStore {
  params: AnalysisParams | null
  setParams: (p: AnalysisParams) => void
  results: MarketResult[]
  setResults: (r: MarketResult[]) => void
  clearResults: () => void

  history: HistoryItem[]
  addToHistory: (item: Omit<HistoryItem, 'id' | 'date'>) => void
  clearHistory: () => void
  deleteHistoryItem: (id: string) => void

  expertMode: boolean
  toggleExpertMode: () => void
  selectedCountry: string | null
  setSelectedCountry: (code: string | null) => void
}

export const useAnalysisStore = create<AnalysisStore>()(
  persist(
    (set) => ({
      params: null,
      setParams: (params) => set({ params }),
      results: [],
      setResults: (results) => set({ results }),
      clearResults: () => set({ results: [], params: null }),

      history: [],
      addToHistory: (item) => set((s) => ({
        history: [{ ...item, id: crypto.randomUUID(), date: new Date().toISOString() }, ...s.history]
      })),
      clearHistory: () => set({ history: [] }),
      deleteHistoryItem: (id) => set((s) => ({ history: s.history.filter(h => h.id !== id) })),

      expertMode: false,
      toggleExpertMode: () => set((s) => ({ expertMode: !s.expertMode })),
      selectedCountry: null,
      setSelectedCountry: (code) => set({ selectedCountry: code }),
    }),
    {
      name: 'marotrade-storage',
      partialize: (state) => ({
        params: state.params,
        results: state.results,
        history: state.history,
        expertMode: state.expertMode,
      }),
    }
  )
)
