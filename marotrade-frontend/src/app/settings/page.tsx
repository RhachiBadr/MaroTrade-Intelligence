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

const SECTIONS = [
  { id: 'profile', label: 'Profil', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Sécurité', icon: Shield },
  { id: 'api', label: 'API', icon: Key },
]

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()

  return (
    <PageTransition>
      <PageContainer className="space-y-8 pb-8">
        <PageHeader
          title="Paramètres"
          description="Gérez votre compte, vos préférences et vos intégrations."
        />

        <div className="grid gap-8 lg:grid-cols-[220px_1fr]">
          <nav className="flex flex-row gap-1 overflow-x-auto lg:flex-col lg:overflow-visible">
            {SECTIONS.map(({ id, label, icon: Icon }) => (
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
                  <h2 className="text-base font-semibold text-text-primary">Profil entreprise</h2>
                  <Badge variant="default">Démo</Badge>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-text-secondary">Entreprise</label>
                    <Input defaultValue="Coopérative Argan du Souss" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-text-secondary">Email</label>
                    <Input defaultValue="export@argan.ma" type="email" />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <label className="text-sm font-medium text-text-secondary">Secteur</label>
                    <Input defaultValue="Agroalimentaire — Terroir premium" />
                  </div>
                </div>
                <Button>Enregistrer</Button>
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardContent className="space-y-5">
                <h2 className="text-base font-semibold text-text-primary">Apparence</h2>
                <div className="flex items-center justify-between rounded-xl border border-border p-4">
                  <div className="flex items-center gap-3">
                    <Moon className="h-5 w-5 text-text-muted" />
                    <div>
                      <p className="text-sm font-medium text-text-primary">Thème</p>
                      <p className="text-xs text-text-muted">Mode sombre recommandé</p>
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
                      Sombre
                    </button>
                    <button
                      type="button"
                      onClick={() => setTheme('light')}
                      className={cn(
                        'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                        theme === 'light' ? 'bg-primary-500/20 text-primary-300' : 'text-text-muted hover:bg-white/5'
                      )}
                    >
                      Clair
                    </button>
                  </div>
                </div>
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardContent className="space-y-5">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary-400" />
                  <h2 className="text-base font-semibold text-text-primary">Clé API</h2>
                  <Badge variant="warning">Pro</Badge>
                </div>
                <p className="text-sm text-text-muted">
                  Disponible avec le plan Pro. Intégrez MaroTrade à votre CRM ou portail client.
                </p>
                <Input readOnly value="mt_live_••••••••••••••••" className="font-mono text-xs" />
                <Button variant="secondary">Demander l&apos;accès API</Button>
              </GlassCardContent>
            </GlassCard>
          </div>
        </div>
      </PageContainer>
    </PageTransition>
  )
}
