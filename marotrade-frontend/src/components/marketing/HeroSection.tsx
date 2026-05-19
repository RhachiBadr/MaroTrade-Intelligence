'use client'

import { motion } from 'framer-motion'
import { ArrowRight, BarChart3, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react'
import { HeroBackground } from '@/components/marketing/HeroBackground'
import { AnimatedButton } from '@/components/ui/animated-button'
import { FloatingCard } from '@/components/ui/floating-card'
import { Badge } from '@/components/ui/badge'
import { easeOut } from '@/lib/motion'

export function HeroSection() {
  return (
    <section id="hero-section" className="relative min-h-[92vh] overflow-hidden">
      <HeroBackground />

      <div className="relative z-10 mx-auto flex min-h-[92vh] max-w-6xl flex-col items-center justify-center px-4 py-28 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 36 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: easeOut }}
          className="relative mx-auto max-w-4xl text-center"
        >
          <motion.div
            className="pointer-events-none absolute -inset-x-8 -inset-y-12 rounded-3xl bg-background/20 blur-3xl"
            aria-hidden
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 1 }}
          />
          <div className="relative">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Badge variant="primary" className="mb-6 gap-1.5 px-4 py-1.5 backdrop-blur-md">
              <Sparkles className="h-3.5 w-3.5" />
              Intelligence export propulsée par l&apos;IA
            </Badge>
          </motion.div>

          <h1 className="text-balance text-5xl font-bold tracking-tight text-text-primary sm:text-6xl lg:text-7xl lg:leading-[1.05]">
            Exportez smarter.{' '}
            <span className="gradient-text">Décidez faster.</span>
          </h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="mx-auto mt-6 max-w-2xl text-pretty text-lg leading-relaxed text-text-secondary"
          >
            Scoring ML, routes commerciales et veille réglementaire — une plateforme IA pour prioriser vos
            marchés d&apos;export depuis le Maroc vers le monde.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <AnimatedButton href="/analyze" size="lg">
              Lancer une analyse
              <ArrowRight className="h-4 w-4" />
            </AnimatedButton>
            <AnimatedButton href="/dashboard" variant="secondary" size="lg">
              Explorer le dashboard
            </AnimatedButton>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.55 }}
            className="mt-6 text-sm text-text-muted"
          >
            Aucune carte bancaire · Données officielles · Essai gratuit
          </motion.p>
          </div>
        </motion.div>

        {/* Live trade metrics — floating over globe */}
        <motion.div
          initial={{ opacity: 0, y: 48 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5, ease: easeOut }}
          className="relative mt-20 grid w-full max-w-4xl grid-cols-1 gap-4 sm:grid-cols-3"
        >
          <FloatingCard delay={0.2} className="sm:translate-y-4 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500/20">
                <TrendingUp className="h-5 w-5 text-primary-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">87.3</p>
                <p className="text-xs text-text-muted">Score France · CAS→FRA</p>
              </div>
            </div>
          </FloatingCard>

          <FloatingCard delay={0.35} className="sm:-translate-y-2 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent-500/20">
                <ShieldCheck className="h-5 w-5 text-accent-500" />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary">3 alertes actives</p>
                <p className="text-xs text-text-muted">Veille EUDR · FDA · Halal</p>
              </div>
            </div>
          </FloatingCard>

          <FloatingCard delay={0.5} className="sm:translate-y-6 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500/20">
                <BarChart3 className="h-5 w-5 text-primary-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary">+12.4% CAGR</p>
                <p className="text-xs text-text-muted">Route CAS→USA · Prophet</p>
              </div>
            </div>
          </FloatingCard>
        </motion.div>
      </div>
    </section>
  )
}
