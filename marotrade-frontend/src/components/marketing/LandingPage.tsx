'use client'

import Link from 'next/link'
import {
  ArrowRight,
  BarChart3,
  Check,
  Globe2,
  LineChart,
  ShieldCheck,
  Zap,
  Brain,
} from 'lucide-react'
import { HeroSection } from '@/components/marketing/HeroSection'
import { AnimatedButton } from '@/components/ui/animated-button'
import { GlassCard } from '@/components/ui/glass-card'
import { GradientOrb } from '@/components/ui/floating-card'
import { FadeIn, FadeInItem, FadeInStagger } from '@/components/motion/FadeIn'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const FEATURES = [
  { title: 'Scoring multi-marchés', desc: '7 dimensions, XGBoost et SHAP pour chaque pays cible.', icon: BarChart3 },
  { title: 'Veille réglementaire', desc: 'EUR-Lex, RASFF, FDA — alertes priorisées par impact.', icon: ShieldCheck },
  { title: 'Prévisions Prophet', desc: 'Projections de volumes importateurs 2023–2026.', icon: LineChart },
  { title: 'Données temps réel', desc: 'Comtrade, World Bank, Google Trends avec cache intelligent.', icon: Globe2 },
  { title: 'Analyse IA', desc: 'Pipeline NLP open-source et enrichissement LLM optionnel.', icon: Brain },
  { title: 'API REST', desc: 'Backend FastAPI prêt pour intégrations CRM et portails.', icon: Zap },
]

const PRICING = [
  {
    name: 'Starter',
    price: '0',
    period: 'Pour démarrer',
    features: ['5 analyses / mois', 'Veille de base', 'Historique local'],
    cta: { label: 'Commencer', href: '/analyze' },
    highlight: false,
  },
  {
    name: 'Pro',
    price: 'Sur devis',
    period: 'Équipes export',
    features: ['Analyses illimitées', 'API & webhooks', 'Support prioritaire', 'SLA données'],
    cta: { label: 'Nous contacter', href: '/pricing' },
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Sur mesure',
    period: 'Multi-sites, SSO',
    features: ['Déploiement dédié', 'Gouvernance données', 'Formation équipes', 'Roadmap partagée'],
    cta: { label: 'Parler à l\'équipe', href: 'mailto:contact@marotrade.ma' },
    highlight: false,
  },
]

export function LandingPage() {
  return (
    <>
      <HeroSection />

      {/* Social proof */}
      <section className="border-y border-border py-12">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6 opacity-60">
            {['UN Comtrade', 'World Bank', 'EUR-Lex', 'RASFF', 'FDA'].map((name) => (
              <span key={name} className="text-sm font-medium tracking-wide text-text-secondary">
                {name}
              </span>
            ))}
          </FadeIn>
        </div>
      </section>

      {/* Features */}
      <section id="fonctionnalites" className="scroll-mt-24 py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
              Tout ce qu&apos;il faut pour exporter
            </h2>
            <p className="mt-4 text-lg text-text-secondary">
              Une plateforme unifiée — du code HS au classement des marchés cibles.
            </p>
          </FadeIn>

          <FadeInStagger className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ title, desc, icon: Icon }) => (
              <FadeInItem key={title}>
                <GlassCard className="h-full p-6" glow>
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500/20 to-primary-600/10">
                    <Icon className="h-5 w-5 text-primary-400" />
                  </div>
                  <h3 className="font-semibold text-text-primary">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-muted">{desc}</p>
                </GlassCard>
              </FadeInItem>
            ))}
          </FadeInStagger>
        </div>
      </section>

      {/* Product showcase */}
      <section id="produit" className="scroll-mt-24 border-y border-border py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <FadeIn direction="right">
              <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
                Des décisions traçables, pas des intuitions
              </h2>
              <p className="mt-4 text-lg text-text-secondary">
                Chaque score est décomposé avec SHAP. Vous savez exactement quels facteurs tirent un marché vers le
                haut ou le bas.
              </p>
              <ul className="mt-8 space-y-4">
                {[
                  'Classement multi-pays avec explications en français',
                  'Veille EUDR, FDA, halal priorisée par impact',
                  'Prévisions Prophet intégrées au scoring',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-text-secondary">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent-500" />
                    {item}
                  </li>
                ))}
              </ul>
              <AnimatedButton href="/analyze" className="mt-8">
                Commencer une analyse
                <ArrowRight className="h-4 w-4" />
              </AnimatedButton>
            </FadeIn>

            <FadeIn direction="left" delay={0.15}>
              <GlassCard glow className="overflow-hidden p-1">
                <div className="rounded-lg bg-surface-elevated p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <span className="text-xs font-medium uppercase tracking-wider text-text-muted">Top marchés</span>
                    <Badge variant="success">Live</Badge>
                  </div>
                  {[
                    { country: 'France', score: 87, trend: '+5' },
                    { country: 'États-Unis', score: 84, trend: '+12' },
                    { country: 'Allemagne', score: 81, trend: '+3' },
                    { country: 'Espagne', score: 78, trend: '-1' },
                  ].map((row) => (
                    <div key={row.country} className="flex items-center justify-between border-b border-border py-3 last:border-0">
                      <span className="text-sm font-medium text-text-primary">{row.country}</span>
                      <div className="flex items-center gap-3">
                        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted">
                          <div className="h-full rounded-full bg-gradient-to-r from-primary-600 to-primary-400" style={{ width: `${row.score}%` }} />
                        </div>
                        <span className="w-8 text-right text-sm font-semibold text-text-primary">{row.score}</span>
                        <span className={cn('text-xs font-medium', row.trend.startsWith('+') ? 'text-success' : 'text-danger')}>
                          {row.trend}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section id="chiffres" className="scroll-mt-24 py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">Performance</h2>
          </FadeIn>
          <div className="mt-12 grid grid-cols-2 gap-4 lg:grid-cols-4">
            {[
              { n: '38+', l: 'Pays couverts' },
              { n: '7', l: 'Dimensions scoring' },
              { n: '<3s', l: 'Latence scoring' },
              { n: '95%', l: 'Couverture alertes' },
            ].map((s, idx) => (
              <FadeIn key={s.l} delay={idx * 0.08}>
                <GlassCard className="p-6 text-center">
                  <p className="text-4xl font-bold tracking-tight gradient-text">{s.n}</p>
                  <p className="mt-2 text-sm text-text-muted">{s.l}</p>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing preview */}
      <section id="tarifs" className="scroll-mt-24 border-t border-border py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">Tarifs simples</h2>
            <p className="mt-4 text-lg text-text-secondary">Commencez gratuitement, scalez quand vous êtes prêt.</p>
          </FadeIn>

          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {PRICING.map((tier, idx) => (
              <FadeIn key={tier.name} delay={idx * 0.1}>
                <GlassCard
                  className={cn(
                    'flex h-full flex-col p-8',
                    tier.highlight && 'gradient-border shadow-[0_0_60px_rgba(99,102,241,0.2)]'
                  )}
                  glow={tier.highlight}
                >
                  {tier.highlight && (
                    <Badge variant="primary" className="mb-4 w-fit">Populaire</Badge>
                  )}
                  <h3 className="text-lg font-semibold text-text-primary">{tier.name}</h3>
                  <p className="mt-2 text-4xl font-bold text-text-primary">{tier.price}</p>
                  <p className="text-sm text-text-muted">{tier.period}</p>
                  <ul className="mt-6 flex-1 space-y-3">
                    {tier.features.map((f) => (
                      <li key={f} className="flex gap-2 text-sm text-text-secondary">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <AnimatedButton
                    href={tier.cta.href}
                    variant={tier.highlight ? 'primary' : 'secondary'}
                    className="mt-8 w-full"
                  >
                    {tier.cta.label}
                  </AnimatedButton>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
          <p className="mt-8 text-center">
            <Link href="/pricing" className="text-sm font-medium text-primary-400 hover:text-primary-300">
              Voir tous les détails tarifaires →
            </Link>
          </p>
        </div>
      </section>

      {/* Testimonials */}
      <section id="temoignages" className="scroll-mt-24 py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">Ils exportent avec confiance</h2>
          </FadeIn>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {[
              { quote: 'Le top 5 pays + la veille EUDR nous ont fait gagner des semaines.', author: 'Fatima Z.', role: 'Directrice export' },
              { quote: 'Le radar SHAP aide à expliquer le pourquoi à notre comité.', author: 'Youssef M.', role: 'CEO — artisanat' },
              { quote: 'Alertes FDA et halal remontées au bon moment avant la campagne USA.', author: 'Amina K.', role: 'Responsable qualité' },
            ].map((t, idx) => (
              <FadeIn key={t.author} delay={idx * 0.1}>
                <GlassCard className="h-full p-6">
                  <p className="text-sm leading-relaxed text-text-secondary">&ldquo;{t.quote}&rdquo;</p>
                  <div className="mt-5 border-t border-border pt-4">
                    <p className="text-sm font-semibold text-text-primary">{t.author}</p>
                    <p className="text-xs text-text-muted">{t.role}</p>
                  </div>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="pb-24 sm:pb-32">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <FadeIn>
            <div className="relative overflow-hidden rounded-2xl glass-strong px-8 py-16 text-center sm:px-16">
              <GradientOrb className="left-1/2 top-0 h-64 w-64 -translate-x-1/2 -translate-y-1/2" />
              <h2 className="relative text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
                Prêt à conquérir vos marchés ?
              </h2>
              <p className="relative mx-auto mt-4 max-w-xl text-text-secondary">
                Lancez une analyse en quelques minutes ou explorez le dashboard.
              </p>
              <div className="relative mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
                <AnimatedButton href="/analyze" size="lg">Essayer maintenant</AnimatedButton>
                <AnimatedButton href="/login" variant="secondary" size="lg">Connexion</AnimatedButton>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>
    </>
  )
}
