'use client'

import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { messages, type Locale } from './messages'
import { formatLocalizedDate } from './date-format'

const STORAGE_KEY = 'marotrade-locale'
type Variables = Record<string, string | number>

interface I18nValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string, variables?: Variables) => string
  formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string
  formatDate: (value: string | Date, options?: Intl.DateTimeFormatOptions) => string
}

const I18nContext = createContext<I18nValue | null>(null)

function resolve(locale: Locale, key: string): string | undefined {
  return key.split('.').reduce<unknown>((value, part) => {
    if (!value || typeof value !== 'object') return undefined
    return (value as Record<string, unknown>)[part]
  }, messages[locale]) as string | undefined
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>('fr')

  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEY) === 'en') setLocale('en')
  }, [])

  useEffect(() => {
    document.documentElement.lang = locale
    localStorage.setItem(STORAGE_KEY, locale)
  }, [locale])

  const value = useMemo<I18nValue>(() => ({
    locale,
    setLocale,
    t: (key, variables) => {
      const message = resolve(locale, key) ?? resolve('fr', key) ?? key
      return Object.entries(variables ?? {}).reduce(
        (text, [name, replacement]) => text.replaceAll(`{{${name}}}`, String(replacement)),
        message,
      )
    },
    formatNumber: (number, options) => new Intl.NumberFormat(locale === 'fr' ? 'fr-FR' : 'en-US', options).format(number),
    formatDate: (date, options) => formatLocalizedDate(date, locale, options),
  }), [locale])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const context = useContext(I18nContext)
  if (!context) throw new Error('useI18n must be used inside I18nProvider')
  return context
}

export function getStoredLocale(): Locale {
  if (typeof window === 'undefined') return 'fr'
  return localStorage.getItem(STORAGE_KEY) === 'en' ? 'en' : 'fr'
}
