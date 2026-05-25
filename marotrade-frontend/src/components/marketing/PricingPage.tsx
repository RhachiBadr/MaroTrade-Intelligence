'use client'

import { Check, HelpCircle, Sparkles } from 'lucide-react'
import { FadeIn } from '@/components/motion/FadeIn'
import { AnimatedButton } from '@/components/ui/animated-button'
import { GlassCard } from '@/components/ui/glass-card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const PLANS = [
  {
    name: 'Starter',
    price: '0',
    currency: 'MAD',
    period: '/ mois',
    description: 'Pour découvrir la plateforme et lancer vos premières analyses.',
    features: [
      '5 analyses marchés / mois',
      'Veille réglementaire de base',
      'Historique local navigateur',
      'Export PDF basique',
      'Support communautaire',
    ],
    cta: { label: 'Commencer gratuitement', href: '/analyze' },
    highlight: false,
  },
  {
    name: 'Pro',
    price: 'Sur devis',
    currency: '',
    period: '',
    description: 'Pour les équipes export qui industrialisent leurs décisions.',
    features: [
      'Analyses illimitées',
      'API REST & webhooks',
      'Veille avancée + alertes email',
      'Prévisions Prophet étendues',
      'Support prioritaire',
      'SLA données 99.5%',
    ],
    cta: { label: 'Demander un devis', href: 'mailto:contact@marotrade.ma?subject=MaroTrade%20Pro' },
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Sur mesure',
    currency: '',
    period: '',
    description: 'Déploiement dédié pour groupes et institutions.',
    features: [
      'Infrastructure dédiée',
      'SSO & gouvernance des données',
      'Formation équipes sur site',
      'Intégrations CRM/ERP custom',
      'Account manager dédié',
      'Roadmap produit partagée',
    ],
    cta: { label: 'Contacter les ventes', href: 'mailto:contact@marotrade.ma?subject=MaroTrade%20Enterprise' },
    highlight: false,
  },
]

const FAQ = [
  {
    q: 'Puis-je changer de plan à tout moment ?',
    a: 'Oui, vous pouvez upgrader ou downgrader à tout moment. Les changements prennent effet immédiatement.',
  },
  {
    q: 'Les données sont-elles sécurisées ?',
    a: 'Oui. Chiffrement TLS, hébergement conforme RGPD, et aucune revente de données.',
  },
  {
    q: 'Proposez-vous un essai Pro ?',
    a: 'Contactez-nous pour un essai Pro de 14 jours avec accès API complet.',
  },
]

export function PricingPage() {
  return (
    <div className="relative overflow-hidden py-20 sm:py-28">
      <div className="aurora-field pointer-events-none absolute inset-x-0 top-0 h-[620px] opacity-55" aria-hidden />
      <div className="light-grid pointer-events-none absolute inset-0 opacity-30" aria-hidden />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <FadeIn className="mx-auto max-w-2xl text-center">
          <Badge variant="primary" className="mb-4">Tarifs</Badge>
          <h1 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-6xl">
            Des plans pour chaque étape
          </h1>
          <p className="mt-5 text-lg leading-8 text-text-secondary">
            Commencez gratuitement, scalez quand votre activité export décolle.
          </p>
        </FadeIn>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {PLANS.map((plan, idx) => (
            <FadeIn key={plan.name} delay={idx * 0.1}>
              <GlassCard
                tilt
                className={cn(
                  'flex h-full flex-col p-8',
                  plan.highlight && 'scale-[1.02] border-primary-400/30 bg-primary-500/10 shadow-[0_0_100px_rgba(99,102,241,0.28)]'
                )}
                glow={plan.highlight}
              >
                {plan.highlight && <Badge variant="primary" className="mb-4 w-fit">Recommandé</Badge>}
                {plan.highlight && (
                  <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-primary-300">
                    <Sparkles className="h-3.5 w-3.5" />
                    Premium workspace
                  </div>
                )}
                <h2 className="text-xl font-semibold text-text-primary">{plan.name}</h2>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-text-primary">{plan.price}</span>
                  {plan.currency && <span className="text-sm text-text-muted">{plan.currency}{plan.period}</span>}
                </div>
                <p className="mt-3 text-sm text-text-muted">{plan.description}</p>
                <ul className="mt-6 flex-1 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex gap-2.5 text-sm text-text-secondary">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent-500" />
                      {f}
                    </li>
                  ))}
                </ul>
                <AnimatedButton
                  href={plan.cta.href}
                  variant={plan.highlight ? 'primary' : 'secondary'}
                  className="mt-8 w-full"
                >
                  {plan.cta.label}
                </AnimatedButton>
              </GlassCard>
            </FadeIn>
          ))}
        </div>

        <FadeIn className="mt-24">
          <h2 className="text-center text-2xl font-bold text-text-primary">Questions fréquentes</h2>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {FAQ.map((item) => (
              <GlassCard key={item.q} tilt className="p-6">
                <div className="mb-3 flex items-start gap-2">
                  <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-primary-400" />
                  <h3 className="text-sm font-semibold text-text-primary">{item.q}</h3>
                </div>
                <p className="text-sm leading-relaxed text-text-muted">{item.a}</p>
              </GlassCard>
            ))}
          </div>
        </FadeIn>
      </div>
    </div>
  )
}
