'use client'

import Link from 'next/link'
import { Globe, Menu, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AnimatedButton } from '@/components/ui/animated-button'

const NAV = [
  { label: 'Produit', href: '/#produit' },
  { label: 'Fonctionnalités', href: '/#fonctionnalites' },
  { label: 'Chiffres', href: '/#chiffres' },
  { label: 'Tarifs', href: '/pricing' },
  { label: 'Témoignages', href: '/#temoignages' },
]

export function MarketingShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="fixed inset-x-0 top-0 z-50">
        <div className="mx-4 mt-4 sm:mx-6 lg:mx-8">
          <nav className="glass flex h-14 items-center justify-between gap-4 rounded-2xl px-4 sm:px-6">
            <Link href="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-lg shadow-primary-600/30">
                <Globe className="h-4 w-4" aria-hidden />
              </span>
              <span className="font-semibold tracking-tight text-text-primary">MaroTrade</span>
            </Link>

            <div className="hidden items-center gap-1 md:flex">
              {NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
                >
                  {item.label}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="hidden rounded-lg px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary sm:inline-block"
              >
                Connexion
              </Link>
              <AnimatedButton href="/analyze" size="sm" className="hidden sm:inline-flex">
                Essayer gratuitement
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
              className="mx-4 mt-2 glass rounded-2xl p-4 md:hidden sm:mx-6"
            >
              <nav className="flex flex-col gap-1">
                {NAV.map((item) => (
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
                  Connexion
                </Link>
                <AnimatedButton href="/dashboard" className="mt-2 w-full">
                  Accéder à l&apos;app
                </AnimatedButton>
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <main className="flex-1 pt-20">{children}</main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary-400" />
                <span className="font-semibold text-text-primary">MaroTrade Intelligence</span>
              </div>
              <p className="text-sm leading-relaxed text-text-muted">
                Aide à la décision export pour les PME marocaines.
              </p>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">Produit</p>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link href="/#fonctionnalites" className="hover:text-primary-400">Fonctionnalités</Link></li>
                <li><Link href="/pricing" className="hover:text-primary-400">Tarifs</Link></li>
                <li><Link href="/dashboard" className="hover:text-primary-400">Application</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">Ressources</p>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link href="/analyze" className="hover:text-primary-400">Nouvelle analyse</Link></li>
                <li><Link href="/analytics" className="hover:text-primary-400">Analytics</Link></li>
                <li><Link href="/regulations" className="hover:text-primary-400">Veille</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">Légal</p>
              <ul className="space-y-2 text-sm text-text-muted">
                <li>Mentions légales</li>
                <li>Confidentialité</li>
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
