import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: Parameters<typeof clsx>) {
  return twMerge(clsx(inputs))
}

export function formatScore(score: number): string {
  return score.toFixed(0)
}

export function formatCurrency(value: number, currency = 'USD'): string {
  return new Intl.NumberFormat('fr-MA', { style: 'currency', currency, maximumFractionDigits: 0 }).format(value)
}

export function scoreColor(score: number): string {
  if (score >= 70) return 'bg-success/10 text-success border border-success/20'
  if (score >= 50) return 'bg-warning/10 text-warning border border-warning/20'
  return 'bg-danger/10 text-danger border border-danger/20'
}

export function scoreTextColor(score: number): string {
  if (score >= 70) return 'text-success'
  if (score >= 50) return 'text-warning'
  return 'text-danger'
}

export function levelColor(level: string) {
  const map: Record<string, { border: string; bg: string; text: string }> = {
    CRITIQUE:  { border: 'border-danger/30',  bg: 'bg-danger/5',  text: 'text-danger font-bold'  },
    ATTENTION: { border: 'border-warning/30', bg: 'bg-warning/5', text: 'text-warning font-bold' },
    INFO:      { border: 'border-primary/30', bg: 'bg-primary/5', text: 'text-primary font-bold' },
  }
  return map[level] ?? map['INFO']
}
