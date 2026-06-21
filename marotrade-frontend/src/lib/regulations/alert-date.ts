const ISO_DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/
const COMPACT_DATE = /^(\d{4})(\d{2})(\d{2})$/

export type AlertPeriod = 'all' | 'today' | 'week' | 'month' | 'custom'

export function parseAlertDate(value: string | Date | null | undefined): Date | null {
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value
  const raw = String(value ?? '').trim()
  if (!raw) return null

  const compact = raw.match(COMPACT_DATE)
  const normalized = compact
    ? `${compact[1]}-${compact[2]}-${compact[3]}T12:00:00`
    : ISO_DATE_ONLY.test(raw)
      ? `${raw}T12:00:00`
      : raw
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function endOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
}

export function getAlertPeriodRange(
  period: AlertPeriod,
  customStart = '',
  customEnd = '',
  now = new Date(),
): { start: Date | null; end: Date | null } {
  if (period === 'today') return { start: startOfDay(now), end: endOfDay(now) }
  if (period === 'week') {
    const start = startOfDay(now)
    const day = start.getDay()
    start.setDate(start.getDate() - (day === 0 ? 6 : day - 1))
    return { start, end: endOfDay(now) }
  }
  if (period === 'month') {
    return { start: new Date(now.getFullYear(), now.getMonth(), 1), end: endOfDay(now) }
  }
  if (period === 'custom') {
    const start = parseAlertDate(customStart)
    const end = parseAlertDate(customEnd)
    return { start: start ? startOfDay(start) : null, end: end ? endOfDay(end) : null }
  }
  return { start: null, end: null }
}

export function isAlertInPeriod(
  value: string | Date | null | undefined,
  period: AlertPeriod,
  customStart = '',
  customEnd = '',
  now = new Date(),
) {
  if (period === 'all') return true
  const date = parseAlertDate(value)
  if (!date) return false
  const { start, end } = getAlertPeriodRange(period, customStart, customEnd, now)
  return (!start || date >= start) && (!end || date <= end)
}
