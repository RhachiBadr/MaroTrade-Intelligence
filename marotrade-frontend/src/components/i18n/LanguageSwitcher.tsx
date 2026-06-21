'use client'

import { Globe2 } from 'lucide-react'
import { useI18n } from '@/lib/i18n'
import { cn } from '@/lib/utils'

export function LanguageSwitcher({ compact = false, className }: { compact?: boolean; className?: string }) {
  const { locale, setLocale, t } = useI18n()
  return (
    <div className={cn('inline-flex items-center gap-1 rounded-xl border border-border bg-surface-elevated p-1', className)} aria-label={t('common.language')}>
      {!compact && <Globe2 className="ml-1 h-3.5 w-3.5 text-text-muted" aria-hidden />}
      {(['fr', 'en'] as const).map(language => (
        <button key={language} type="button" onClick={() => setLocale(language)} aria-pressed={locale === language}
          title={t(language === 'fr' ? 'common.french' : 'common.english')}
          className={cn('min-w-8 rounded-lg px-2 py-1 text-[11px] font-semibold uppercase transition-colors',
            locale === language ? 'bg-primary-500 text-white shadow-sm' : 'text-text-muted hover:bg-surface hover:text-text-primary')}>
          {language}
        </button>
      ))}
    </div>
  )
}
