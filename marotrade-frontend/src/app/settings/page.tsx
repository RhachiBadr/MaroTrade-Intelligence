'use client'

import { PageTransition } from '@/components/motion/PageTransition'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useTheme } from '@/app/providers'
import { Bell, Globe, Key, Moon, Shield, User } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useI18n } from '@/lib/i18n'
import { LanguageSwitcher } from '@/components/i18n/LanguageSwitcher'

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const { t } = useI18n()
  const sections = [
    { id: 'profile', label: t('settings.profile'), icon: User },
    { id: 'notifications', label: t('settings.notifications'), icon: Bell },
    { id: 'security', label: t('settings.security'), icon: Shield },
    { id: 'api', label: 'API', icon: Key },
  ]

  return (
    <PageTransition>
      <PageContainer className="space-y-8 pb-8">
        <PageHeader
          title={t('settings.title')}
          description={t('settings.subtitle')}
        />

        <div className="grid gap-8 lg:grid-cols-[220px_1fr]">
          <nav className="flex flex-row gap-1 overflow-x-auto lg:flex-col lg:overflow-visible">
            {sections.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                className={cn(
                  'flex shrink-0 items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                  id === 'profile'
                    ? 'bg-primary-500/15 text-primary-300'
                    : 'text-text-secondary hover:bg-white/5 hover:text-text-primary'
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </nav>

          <div className="space-y-6">
            <GlassCard>
              <GlassCardContent className="space-y-5">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold text-text-primary">{t('settings.companyProfile')}</h2>
                  <Badge variant="default">Démo</Badge>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-text-secondary">{t('settings.company')}</label>
                    <Input defaultValue="Coopérative Argan du Souss" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-text-secondary">Email</label>
                    <Input defaultValue="export@argan.ma" type="email" />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <label className="text-sm font-medium text-text-secondary">{t('settings.sector')}</label>
                    <Input defaultValue="Agroalimentaire — Terroir premium" />
                  </div>
                </div>
                <Button>{t('common.save')}</Button>
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardContent className="space-y-5">
                <h2 className="text-base font-semibold text-text-primary">{t('settings.appearance')}</h2>
                <div className="flex items-center justify-between rounded-xl border border-border p-4">
                  <div className="flex items-center gap-3">
                    <Moon className="h-5 w-5 text-text-muted" />
                    <div>
                      <p className="text-sm font-medium text-text-primary">{t('settings.theme')}</p>
                      <p className="text-xs text-text-muted">{t('settings.darkRecommended')}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setTheme('dark')}
                      className={cn(
                        'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                        theme === 'dark' ? 'bg-primary-500/20 text-primary-300' : 'text-text-muted hover:bg-white/5'
                      )}
                    >
                      {t('settings.dark')}
                    </button>
                    <button
                      type="button"
                      onClick={() => setTheme('light')}
                      className={cn(
                        'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                        theme === 'light' ? 'bg-primary-500/20 text-primary-300' : 'text-text-muted hover:bg-white/5'
                      )}
                    >
                      {t('settings.light')}
                    </button>
                  </div>
                </div>
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardContent className="flex items-center justify-between gap-4">
                <div><h2 className="text-base font-semibold text-text-primary">{t('common.language')}</h2>
                  <p className="text-xs text-text-muted">{t('common.french')} / {t('common.english')}</p></div>
                <LanguageSwitcher />
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardContent className="space-y-5">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary-400" />
                  <h2 className="text-base font-semibold text-text-primary">{t('settings.apiKey')}</h2>
                  <Badge variant="warning">Pro</Badge>
                </div>
                <p className="text-sm text-text-muted">
                  {t('settings.apiDescription')}
                </p>
                <Input readOnly value="mt_live_••••••••••••••••" className="font-mono text-xs" />
                <Button variant="secondary">{t('settings.requestApi')}</Button>
              </GlassCardContent>
            </GlassCard>
          </div>
        </div>
      </PageContainer>
    </PageTransition>
  )
}
