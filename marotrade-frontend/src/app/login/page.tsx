'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Globe, Mail, Lock } from 'lucide-react'
import { GlassCard } from '@/components/ui/glass-card'
import { AnimatedButton } from '@/components/ui/animated-button'
import { Input } from '@/components/ui/input'
import { GradientOrb } from '@/components/ui/floating-card'
import { easeOut } from '@/lib/motion'

export default function LoginPage() {
  return (
    <div className="relative flex min-h-[85vh] items-center justify-center px-4 py-16">
      <GradientOrb className="left-1/4 top-1/4 h-96 w-96 -translate-x-1/2 opacity-50" />
      <GradientOrb className="right-1/4 bottom-1/4 h-80 w-80 translate-x-1/2 bg-[radial-gradient(circle,rgba(52,211,153,0.25)_0%,transparent_70%)]" />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: easeOut }}
        className="relative w-full max-w-md"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-lg shadow-primary-600/30">
            <Globe className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Bon retour</h1>
          <p className="mt-2 text-sm text-text-secondary">Connectez-vous à votre espace MaroTrade Intelligence</p>
        </div>

        <GlassCard glow className="p-8">
          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-text-secondary">
                Email
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
                <Input id="email" type="email" placeholder="vous@entreprise.ma" className="pl-10" />
              </div>
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-text-secondary">
                Mot de passe
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
                <Input id="password" type="password" placeholder="••••••••" className="pl-10" />
              </div>
            </div>
            <AnimatedButton type="submit" className="w-full">
              Se connecter
              <ArrowRight className="h-4 w-4" />
            </AnimatedButton>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-transparent px-2 text-text-muted">ou continuer en mode démo</span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <AnimatedButton href="/dashboard" variant="secondary" className="w-full">
              Accéder au dashboard
            </AnimatedButton>
            <AnimatedButton href="/analyze" variant="ghost" className="w-full">
              Lancer une analyse
            </AnimatedButton>
          </div>
        </GlassCard>

        <p className="mt-6 text-center text-sm text-text-muted">
          Pas encore de compte ?{' '}
          <Link href="/pricing" className="font-medium text-primary-400 hover:text-primary-300">
            Voir les offres
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
