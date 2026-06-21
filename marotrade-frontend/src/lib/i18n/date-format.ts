import type { Locale } from './messages'
import { parseAlertDate } from '@/lib/regulations/alert-date'

export function formatLocalizedDate(
  value: string | Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions,
): string {
  const rawText = typeof value === 'string' ? value.trim() : ''
  const date = parseAlertDate(value)
  if (!date) return rawText

  return new Intl.DateTimeFormat(
    locale === 'fr' ? 'fr-FR' : 'en-US',
    options ?? { day: '2-digit', month: 'short', year: 'numeric' },
  ).format(date)
}
