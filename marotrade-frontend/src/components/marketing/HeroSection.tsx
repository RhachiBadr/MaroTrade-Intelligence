'use client'

import { motion } from 'framer-motion'
import {
  BarChart3,
  CheckCircle2,
  Globe2,
  LineChart,
  RadioTower,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { HeroBackground } from '@/components/marketing/HeroBackground'
import { useI18n } from '@/lib/i18n'
import { marketingContent } from '@/lib/i18n/marketing-content'
import { AnimatedButton } from '@/components/ui/animated-button'
import { FloatingCard } from '@/components/ui/floating-card'
import { Badge } from '@/components/ui/badge'
import { easeOut } from '@/lib/motion'

const BARS = [58, 86, 72, 93, 64, 78, 88, 69]
function DashboardPreview() {
  const { locale } = useI18n()
  const preview = marketingContent[locale].heroPreview
  const icons = [ShieldCheck, BarChart3, Globe2, CheckCircle2]
  const decisionFeed = preview.feed.map(([title, text], index) => ({ title, text, icon: icons[index] }))
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, rotateX: 8 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 0.8, delay: 0.55, ease: easeOut }}
      className="relative mx-auto mt-16 w-full max-w-5xl px-2 [perspective:1600px]"
    >
      <div className="absolute inset-x-10 -top-8 h-24 rounded-full bg-primary-500/20 blur-3xl" aria-hidden />
      <div className="relative rotate-x-[3deg] rounded-2xl border border-white/10 bg-background/50 p-2 shadow-[0_42px_140px_rgba(0,0,0,0.42)] backdrop-blur-2xl">
        <div className="overflow-hidden rounded-xl border border-white/10 bg-[#080812]/90">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-danger-500" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning-500" />
              <span className="h-2.5 w-2.5 rounded-full bg-accent-500" />
            </div>
            <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-wide text-text-muted sm:flex">
              <RadioTower className="h-3 w-3 text-accent-500" />
              {preview.live}
            </div>
          </div>

          <div className="relative grid gap-4 p-4 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-400/70 to-transparent scanline" />

            <div className="space-y-4">
              <div className="rounded-xl border border-white/10 bg-white/[0.045] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{preview.score}</p>
                    <h3 className="mt-1 text-xl font-semibold text-white">{preview.cockpit}</h3>
                  </div>
                  <Badge variant="success">XGBoost + SHAP</Badge>
                </div>
                <div className="grid gap-3 sm:grid-cols-3">
                  {[
                    ['France', '92.4', '+8.1%'],
                    ['USA', '88.7', '+12.4%'],
                    ['UAE', '82.9', '+6.8%'],
                  ].map(([country, score, trend]) => (
                    <div key={country} className="rounded-lg border border-white/10 bg-black/20 p-3">
                      <div className="flex items-center justify-between text-xs text-text-muted">
                        <span>{country}</span>
                        <TrendingUp className="h-3.5 w-3.5 text-accent-500" />
                      </div>
                      <p className="mt-2 text-2xl font-semibold text-white">{score}</p>
                      <p className="text-xs font-medium text-accent-500">{trend} {preview.demandSignal}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-[0.72fr_1fr]">
                <div className="rounded-xl border border-white/10 bg-white/[0.045] p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{preview.riskRadar}</p>
                  <div className="relative mx-auto mt-4 h-44 w-44 rounded-full border border-primary-400/20 bg-primary-500/5">
                    <div className="absolute inset-5 rounded-full border border-accent-400/15" />
                    <div className="absolute inset-12 rounded-full border border-white/10" />
                    <div className="absolute left-1/2 top-1/2 h-24 w-px origin-bottom -translate-x-1/2 -translate-y-full rotate-45 bg-gradient-to-t from-primary-400 to-transparent" />
                    <div className="absolute left-[62%] top-[24%] h-2.5 w-2.5 rounded-full bg-accent-500 shadow-[0_0_22px_rgba(52,211,153,0.9)]" />
                    <div className="absolute left-[32%] top-[58%] h-2 w-2 rounded-full bg-primary-400 shadow-[0_0_18px_rgba(129,140,248,0.9)]" />
                    <div className="absolute inset-0 rounded-full bg-[conic-gradient(from_90deg,rgba(129,140,248,0.24),transparent_22%,rgba(52,211,153,0.2),transparent_60%)]" />
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.045] p-4">
                  <div className="mb-4 flex items-center justify-between">
                    <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{preview.forecast}</p>
                    <LineChart className="h-4 w-4 text-primary-300" />
                  </div>
                  <div className="flex h-44 items-end gap-2">
                    {BARS.map((height, index) => (
                      <div key={index} className="flex flex-1 flex-col items-center gap-2">
                        <div
                          className="chart-bar w-full rounded-t-md bg-gradient-to-t from-primary-700 via-primary-400 to-accent-400 shadow-[0_0_22px_rgba(99,102,241,0.28)]"
                          style={{ height: `${height}%`, animationDelay: `${index * 90}ms` }}
                        />
                        <span className="h-1 w-1 rounded-full bg-white/30" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-xl border border-white/10 bg-white/[0.045] p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{preview.decisionFeed}</p>
                <div className="mt-4 space-y-3">
                  {decisionFeed.map(({ title, text, icon: Icon }) => (
                    <div key={title} className="flex items-start gap-3 rounded-lg border border-white/10 bg-black/20 p-3">
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-500/15">
                        <Icon className="h-4 w-4 text-primary-300" />
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-white">{title}</p>
                        <p className="text-xs text-text-muted">{text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-accent-400/20 bg-accent-500/10 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-accent-500">{preview.action}</p>
                <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                  {preview.actionText}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export function HeroSection() {
  const { locale } = useI18n()
  const content = marketingContent[locale]
  return (
    <section id="hero-section" className="relative min-h-[100vh] overflow-hidden">
      <HeroBackground />

      <div className="relative z-10 mx-auto flex min-h-[100vh] w-full max-w-7xl flex-col items-center justify-center overflow-hidden px-4 pb-24 pt-28 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 36 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: easeOut }}
          className="relative mx-auto w-full max-w-5xl text-center"
        >
          <div className="absolute inset-x-0 -top-20 h-56 rounded-full bg-primary-500/10 blur-3xl" aria-hidden />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Badge variant="primary" className="mb-7 max-w-full gap-1.5 px-4 py-1.5 text-[11px] backdrop-blur-md sm:text-xs">
              <Sparkles className="h-3.5 w-3.5" />
              <span className="truncate">{content.heroBadge}</span>
            </Badge>
          </motion.div>

          <h1 className="mx-auto max-w-[18.5rem] text-balance text-4xl font-semibold leading-[1.04] tracking-tight text-text-primary sm:max-w-5xl sm:text-7xl lg:text-8xl lg:leading-[0.95]">
            {content.heroTitle}
          </h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="mx-auto mt-7 max-w-[18.5rem] text-pretty text-base leading-7 text-text-secondary sm:max-w-3xl sm:text-xl sm:leading-8"
          >
            {content.heroText}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-10 flex w-full flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <AnimatedButton href="/analyze" size="lg" className="h-14 w-full max-w-xs px-8 sm:w-auto">
              {content.heroPrimary}
            </AnimatedButton>
            <AnimatedButton href="/dashboard" variant="secondary" size="lg" className="h-14 w-full max-w-xs px-8 sm:w-auto">
              {content.heroSecondary}
            </AnimatedButton>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.55 }}
            className="mt-7 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-sm text-text-muted"
          >
            <span>{content.heroProofs[0]}</span>
            <span className="h-1 w-1 rounded-full bg-text-muted/40" />
            <span>{content.heroProofs[1]}</span>
            <span className="h-1 w-1 rounded-full bg-text-muted/40" />
            <span>{content.heroProofs[2]}</span>
          </motion.div>
        </motion.div>

        <div className="w-full overflow-hidden">
          <DashboardPreview />
        </div>

        <div className="pointer-events-none relative z-20 -mt-8 hidden w-full max-w-6xl grid-cols-3 gap-4 lg:grid">
          <FloatingCard delay={0.2} className="float-slow translate-y-8 backdrop-blur-xl">
            <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Opportunity signal</p>
            <p className="mt-2 text-2xl font-semibold text-text-primary">+24%</p>
            <p className="text-xs text-text-muted">premium demand in EU channels</p>
          </FloatingCard>
          <FloatingCard delay={0.35} className="float-slow -translate-y-8 backdrop-blur-xl">
            <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Compliance status</p>
            <p className="mt-2 text-sm font-semibold text-text-primary">3 active regulations tracked</p>
            <p className="text-xs text-text-muted">EUDR, FDA, halal certification</p>
          </FloatingCard>
          <FloatingCard delay={0.5} className="float-slow translate-y-10 backdrop-blur-xl">
            <p className="text-xs font-medium uppercase tracking-wide text-text-muted">Forecast model</p>
            <p className="mt-2 text-sm font-semibold text-text-primary">Prophet trend confidence 91%</p>
            <p className="text-xs text-text-muted">2026 route projection ready</p>
          </FloatingCard>
        </div>
      </div>
    </section>
  )
}
