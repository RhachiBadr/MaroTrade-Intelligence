'use client'

import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AnimatedButton } from '@/components/ui/animated-button'
import { LanguageSwitcher } from '@/components/i18n/LanguageSwitcher'
import { useI18n } from '@/lib/i18n'
import { BrandLogo } from '@/components/brand/BrandLogo'

export function MarketingShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const { t } = useI18n()
  const nav = [
    { label: t('marketing.product'), href: '/#produit' }, { label: t('marketing.features'), href: '/#fonctionnalites' },
    { label: t('marketing.figures'), href: '/#chiffres' }, { label: t('nav.pricing'), href: '/pricing' },
    { label: t('marketing.testimonials'), href: '/#temoignages' },
  ]

  return (
    <div className="flex min-h-screen w-full max-w-full flex-col overflow-x-hidden bg-background">
      <header className="fixed inset-x-0 top-0 z-50">
        <div className="mx-auto mt-4" style={{ width: 'min(80rem, calc(100vw - 2rem))' }}>
          <nav className="glass flex h-16 w-full min-w-0 items-center justify-between gap-3 rounded-2xl px-3 shadow-[0_18px_70px_rgba(0,0,0,0.2)] ring-1 ring-white/5 sm:px-4">
            <Link href="/" className="group flex items-center gap-2.5 rounded-xl px-2 py-1.5" onClick={() => setOpen(false)}>
              <BrandLogo size="sm" priority className="transition-transform duration-300 group-hover:scale-105" />
              <span className="font-semibold tracking-tight text-text-primary">MaroTrade</span>
            </Link>

            <div className="hidden items-center gap-1 rounded-xl border border-white/10 bg-white/[0.035] p-1 md:flex">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="relative rounded-lg px-3 py-2 text-sm font-medium text-text-secondary transition-all duration-300 hover:bg-white/10 hover:text-text-primary"
                >
                  {item.label}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <LanguageSwitcher compact />
              <Link
                href="/login"
                className="hidden rounded-lg px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary sm:inline-block"
              >
                {t('auth.login')}
              </Link>
              <AnimatedButton href="/analyze" size="sm" className="hidden sm:inline-flex">
                {t('marketing.try')}
              </AnimatedButton>
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border md:hidden"
                onClick={() => setOpen((o) => !o)}
                aria-expanded={open}
                aria-label={open ? 'Fermer le menu' : 'Menu'}
              >
                {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </nav>
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
            className="mx-4 mt-2 glass rounded-2xl p-4 shadow-[0_18px_70px_rgba(0,0,0,0.25)] md:hidden sm:mx-6"
            >
              <nav className="flex flex-col gap-1">
                {nav.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="rounded-lg px-3 py-2.5 text-sm font-medium text-text-primary hover:bg-white/5"
                    onClick={() => setOpen(false)}
                  >
                    {item.label}
                  </Link>
                ))}
                <Link href="/login" className="rounded-lg px-3 py-2.5 text-sm text-text-secondary" onClick={() => setOpen(false)}>
                  {t('auth.login')}
                </Link>
                <AnimatedButton href="/dashboard" className="mt-2 w-full">
                  {t('marketing.openApp')}
                </AnimatedButton>
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <main className="flex-1 pt-20">{children}</main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <BrandLogo size="sm" />
                <span className="font-semibold text-text-primary">MaroTrade Intelligence</span>
              </div>
              <p className="text-sm leading-relaxed text-text-muted">
                {t('marketing.tagline')}
              </p>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">{t('marketing.product')}</p>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link href="/#fonctionnalites" className="hover:text-primary-400">{t('marketing.features')}</Link></li>
                <li><Link href="/pricing" className="hover:text-primary-400">{t('nav.pricing')}</Link></li>
                <li><Link href="/dashboard" className="hover:text-primary-400">{t('marketing.openApp')}</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">{t('marketing.resources')}</p>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link href="/analyze" className="hover:text-primary-400">{t('marketing.newAnalysis')}</Link></li>
                <li><Link href="/analytics" className="hover:text-primary-400">{t('nav.analytics')}</Link></li>
                <li><Link href="/regulations" className="hover:text-primary-400">{t('marketing.watch')}</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">{t('marketing.legal')}</p>
              <ul className="space-y-2 text-sm text-text-muted">
                <li>{t('marketing.legalNotice')}</li>
                <li>{t('marketing.privacy')}</li>
              </ul>
            </div>
          </div>
          <div className="mt-12 border-t border-border pt-8 text-center text-xs text-text-muted">
            © {new Date().getFullYear()} MaroTrade Intelligence
          </div>
        </div>
      </footer>
    </div>
  )
}
