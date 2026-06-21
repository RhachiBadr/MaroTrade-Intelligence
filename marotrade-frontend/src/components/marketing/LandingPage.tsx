'use client'

import Link from 'next/link'
import {
  ArrowRight,
  BarChart3,
  Check,
  Globe2,
  LineChart,
  Network,
  ShieldCheck,
  Zap,
  Brain,
  Activity,
  Gauge,
  Layers3,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { HeroSection } from '@/components/marketing/HeroSection'
import { AnimatedButton } from '@/components/ui/animated-button'
import { GlassCard } from '@/components/ui/glass-card'
import { FadeIn, FadeInItem, FadeInStagger } from '@/components/motion/FadeIn'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useI18n } from '@/lib/i18n'
import { marketingContent } from '@/lib/i18n/marketing-content'

const FEATURES = [
  { title: 'Market scoring engine', desc: 'Rank countries across 7 weighted dimensions with XGBoost and SHAP explainability.', icon: BarChart3, metric: '7D' },
  { title: 'Regulatory radar', desc: 'Track EUR-Lex, RASFF, FDA and halal requirements with impact-first prioritization.', icon: ShieldCheck, metric: '95%' },
  { title: 'Forecast intelligence', desc: 'Prophet projections turn historical import flows into route-level growth signals.', icon: LineChart, metric: '2026' },
  { title: 'Data fabric', desc: 'Comtrade, World Bank, Google Trends and cache layers normalized into one decision graph.', icon: Network, metric: 'Live' },
  { title: 'AI briefings', desc: 'Natural-language analysis translates complex trade constraints into practical next steps.', icon: Brain, metric: 'NLP' },
  { title: 'Composable API', desc: 'FastAPI endpoints designed for CRM, portals, export workflows and future automation.', icon: Zap, metric: 'REST' },
]

const PRICING = [
  {
    name: 'Starter',
    price: '0',
    period: 'Explore the platform',
    features: ['5 market analyses / month', 'Basic regulatory watch', 'Local browser history'],
    cta: { label: 'Start free', href: '/analyze' },
    highlight: false,
  },
  {
    name: 'Pro',
    price: 'Custom',
    period: 'For export teams',
    features: ['Unlimited analyses', 'API and webhooks', 'Priority support', 'Advanced compliance alerts'],
    cta: { label: 'Talk to us', href: '/pricing' },
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Tailored',
    period: 'For institutions',
    features: ['Dedicated deployment', 'Data governance', 'Team enablement', 'Shared roadmap'],
    cta: { label: 'Contact sales', href: 'mailto:contact@marotrade.ma' },
    highlight: false,
  },
]

function SectionGlow() {
  return (
    <>
      <div className="aurora-field pointer-events-none absolute inset-x-0 top-0 h-[520px] opacity-50" aria-hidden />
      <div className="light-grid pointer-events-none absolute inset-0 opacity-40" aria-hidden />
    </>
  )
}

function MiniLineChart() {
  return (
    <svg viewBox="0 0 360 150" className="h-full w-full" role="img" aria-label="Forecast trend chart">
      <defs>
        <linearGradient id="line" x1="0" x2="1">
          <stop offset="0%" stopColor="#818cf8" />
          <stop offset="55%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#34d399" />
        </linearGradient>
        <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#818cf8" stopOpacity="0.28" />
          <stop offset="100%" stopColor="#34d399" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d="M0 118 C40 105 52 68 94 76 C136 84 132 42 176 50 C220 58 226 28 270 34 C310 39 326 18 360 22 V150 H0 Z" fill="url(#area)" />
      <path d="M0 118 C40 105 52 68 94 76 C136 84 132 42 176 50 C220 58 226 28 270 34 C310 39 326 18 360 22" fill="none" stroke="url(#line)" strokeWidth="4" strokeLinecap="round" />
      {[94, 176, 270, 360].map((x, i) => (
        <circle key={x} cx={x} cy={[76, 50, 34, 22][i]} r="4" fill="#ffffff" opacity="0.85" />
      ))}
    </svg>
  )
}

export function LandingPage() {
  const { locale, t } = useI18n()
  const content = marketingContent[locale]
  const features = FEATURES.map((feature, index) => ({ ...feature, title: content.features[index][0], desc: content.features[index][1], metric: content.features[index][2] }))
  return (
    <div className="overflow-hidden">
      <HeroSection />

      <section className="relative border-y border-border/70 py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="flex flex-wrap items-center justify-center gap-x-12 gap-y-5 opacity-70">
            {['UN Comtrade', 'World Bank', 'EUR-Lex', 'RASFF', 'FDA', 'Google Trends'].map((name) => (
              <span key={name} className="text-sm font-semibold tracking-wide text-text-secondary">
                {name}
              </span>
            ))}
          </FadeIn>
        </div>
      </section>

      <section id="fonctionnalites" className="relative scroll-mt-24 py-28 sm:py-36">
        <SectionGlow />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-3xl text-center">
            <Badge variant="primary" className="mb-5">{content.layersBadge}</Badge>
            <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">
              {content.layersTitle}
            </h2>
            <p className="mt-5 text-lg leading-8 text-text-secondary">
              {content.layersText}
            </p>
          </FadeIn>

          <FadeInStagger className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {features.map(({ title, desc, icon: Icon, metric }) => (
              <FadeInItem key={title}>
                <GlassCard tilt className="animated-border group h-full p-[1px]">
                  <div className="h-full rounded-xl bg-background/70 p-6 backdrop-blur-xl">
                    <div className="mb-8 flex items-start justify-between">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500/25 via-sky-400/15 to-accent-500/20 shadow-[0_0_38px_rgba(99,102,241,0.18)]">
                        <Icon className="h-5 w-5 text-primary-300" />
                      </div>
                      <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-semibold text-text-muted">
                        {metric}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
                    <p className="mt-3 text-sm leading-6 text-text-muted">{desc}</p>
                    <div className="mt-6 h-px w-full bg-gradient-to-r from-primary-400/40 via-accent-400/30 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                  </div>
                </GlassCard>
              </FadeInItem>
            ))}
          </FadeInStagger>
        </div>
      </section>

      <section id="produit" className="relative scroll-mt-24 border-y border-border/70 py-28 sm:py-36">
        <SectionGlow />
        <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <FadeIn direction="right">
            <Badge variant="success" className="mb-5">{content.workflowBadge}</Badge>
            <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">
              {content.workflowTitle}
            </h2>
            <p className="mt-5 text-lg leading-8 text-text-secondary">
              {content.workflowText}
            </p>
            <div className="mt-8 space-y-4">
              {[
                ['Score', 'Country ranking with confidence and SHAP drivers'],
                ['Watch', 'Regulatory alerts converted into action items'],
                ['Forecast', 'Forward-looking demand indicators for 2026'],
              ].map(([label, text]) => (
                <div key={label} className="flex gap-4 rounded-xl border border-white/10 bg-white/[0.035] p-4">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-500/15 text-sm font-semibold text-primary-300">
                    {label.slice(0, 1)}
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-text-primary">{label}</p>
                    <p className="text-sm text-text-muted">{text}</p>
                  </div>
                </div>
              ))}
            </div>
            <AnimatedButton href="/analyze" className="mt-8">
              {content.runAnalysis}
              <ArrowRight className="h-4 w-4" />
            </AnimatedButton>
          </FadeIn>

          <FadeIn direction="left" delay={0.12}>
            <GlassCard tilt glow className="relative overflow-hidden p-5">
              <div className="absolute inset-x-8 top-0 h-24 rounded-full bg-primary-500/20 blur-3xl" aria-hidden />
              <div className="relative grid gap-4 md:grid-cols-[0.82fr_1fr]">
                <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Export score</p>
                  <div className="mt-5 flex h-48 items-center justify-center rounded-full border border-primary-400/20 bg-primary-500/5">
                    <div className="flex h-32 w-32 items-center justify-center rounded-full bg-gradient-to-br from-primary-500/30 to-accent-500/20 shadow-[0_0_60px_rgba(99,102,241,0.25)]">
                      <div className="text-center">
                        <p className="text-4xl font-semibold text-white">92</p>
                        <p className="text-xs text-text-muted">France</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-lg bg-white/5 p-3">
                      <p className="text-text-muted">Confidence</p>
                      <p className="mt-1 font-semibold text-accent-500">94%</p>
                    </div>
                    <div className="rounded-lg bg-white/5 p-3">
                      <p className="text-text-muted">Risk</p>
                      <p className="mt-1 font-semibold text-warning-500">Medium</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="h-48 rounded-xl border border-white/10 bg-black/20 p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Demand forecast</p>
                      <Activity className="h-4 w-4 text-accent-500" />
                    </div>
                    <MiniLineChart />
                  </div>
                  <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                    {['Trade agreement', 'Diaspora signal', 'Logistics quality'].map((item, idx) => (
                      <div key={item} className="flex items-center justify-between border-b border-white/10 py-3 last:border-0">
                        <span className="text-sm text-text-secondary">{item}</span>
                        <span className="text-sm font-semibold text-text-primary">{[98, 82, 76][idx]}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </FadeIn>
        </div>
      </section>

      <section id="chiffres" className="relative scroll-mt-24 py-28 sm:py-36">
        <div className="aurora-field pointer-events-none absolute inset-x-0 bottom-0 h-[520px] opacity-40" aria-hidden />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-3xl text-center">
            <Badge variant="primary" className="mb-5">{content.performanceBadge}</Badge>
            <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">
              {content.performanceTitle}
            </h2>
          </FadeIn>

          <div className="mt-14 grid grid-cols-2 gap-5 lg:grid-cols-4">
            {[
              { n: '38+', l: content.stats[0], icon: Globe2 },
              { n: '7', l: content.stats[1], icon: Layers3 },
              { n: '<3s', l: content.stats[2], icon: Gauge },
              { n: '95%', l: content.stats[3], icon: ShieldCheck },
            ].map((s, idx) => (
              <FadeIn key={s.l} delay={idx * 0.08}>
                <GlassCard tilt className="p-6">
                  <s.icon className="mb-7 h-5 w-5 text-primary-300" />
                  <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.08 + 0.15 }}
                    className="text-4xl font-semibold tracking-tight gradient-text"
                  >
                    {s.n}
                  </motion.p>
                  <p className="mt-2 text-sm text-text-muted">{s.l}</p>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section id="tarifs" className="relative scroll-mt-24 border-t border-border/70 py-28 sm:py-36">
        <SectionGlow />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-3xl text-center">
            <Badge variant="primary" className="mb-5">{content.pricingBadge}</Badge>
            <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">{content.pricingTitle}</h2>
            <p className="mt-5 text-lg text-text-secondary">{content.pricingText}</p>
          </FadeIn>

          <div className="mt-16 grid gap-6 lg:grid-cols-3">
            {PRICING.map((tier, idx) => (
              <FadeIn key={tier.name} delay={idx * 0.1}>
                <GlassCard
                  tilt
                  className={cn(
                    'flex h-full flex-col p-8',
                    tier.highlight && 'scale-[1.02] border-primary-400/30 bg-primary-500/10 shadow-[0_0_100px_rgba(99,102,241,0.28)]'
                  )}
                  glow={tier.highlight}
                >
                  {tier.highlight && <Badge variant="primary" className="mb-4 w-fit">Most capable</Badge>}
                  <h3 className="text-lg font-semibold text-text-primary">{tier.name}</h3>
                  <p className="mt-3 text-4xl font-semibold text-text-primary">{tier.price}</p>
                  <p className="text-sm text-text-muted">{tier.period}</p>
                  <ul className="mt-7 flex-1 space-y-3">
                    {tier.features.map((f) => (
                      <li key={f} className="flex gap-2 text-sm text-text-secondary">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <AnimatedButton href={tier.cta.href} variant={tier.highlight ? 'primary' : 'secondary'} className="mt-8 w-full">
                    {tier.cta.label}
                  </AnimatedButton>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
          <p className="mt-9 text-center">
            <Link href="/pricing" className="text-sm font-semibold text-primary-300 transition-colors hover:text-accent-500">
              Compare all plans <ArrowRight className="inline h-4 w-4" />
            </Link>
          </p>
        </div>
      </section>

      <section id="temoignages" className="relative scroll-mt-24 py-28 sm:py-36">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn className="mx-auto max-w-3xl text-center">
            <Badge variant="success" className="mb-5">{content.testimonialsBadge}</Badge>
            <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">{content.testimonialsTitle}</h2>
          </FadeIn>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {[
              { quote: 'The market ranking and EUDR watch saved weeks of spreadsheet work.', author: 'Fatima Z.', role: 'Export director' },
              { quote: 'SHAP explanations make our country decisions easy to defend internally.', author: 'Youssef M.', role: 'CEO, artisanat' },
              { quote: 'FDA and halal risks surfaced before our campaign, not after.', author: 'Amina K.', role: 'Quality lead' },
            ].map((t, idx) => (
              <FadeIn key={t.author} delay={idx * 0.1}>
                <GlassCard tilt className="h-full p-6">
                  <p className="text-base leading-7 text-text-secondary">&ldquo;{t.quote}&rdquo;</p>
                  <div className="mt-8 border-t border-border pt-4">
                    <p className="text-sm font-semibold text-text-primary">{t.author}</p>
                    <p className="text-xs text-text-muted">{t.role}</p>
                  </div>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section className="relative pb-28 sm:pb-36">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn>
            <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.045] px-8 py-16 text-center shadow-[0_38px_120px_rgba(0,0,0,0.28)] backdrop-blur-2xl sm:px-16">
              <div className="aurora-field absolute inset-0 opacity-60" aria-hidden />
              <div className="relative">
                <Badge variant="primary" className="mb-5">{content.readyBadge}</Badge>
                <h2 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">
                  {content.readyTitle}
                </h2>
                <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-text-secondary">
                  {content.readyText}
                </p>
                <div className="mt-9 flex flex-col items-center justify-center gap-4 sm:flex-row">
                  <AnimatedButton href="/analyze" size="lg">{content.runAnalysis}</AnimatedButton>
                  <AnimatedButton href="/login" variant="secondary" size="lg">{t('auth.loginAction')}</AnimatedButton>
                </div>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>
    </div>
  )
}
