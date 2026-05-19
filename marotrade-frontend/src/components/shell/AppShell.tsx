'use client'

import type { ReactNode } from 'react'
import { ShellProvider, useShell } from '@/components/shell/shell-context'
import Sidebar from '@/components/organisms/Sidebar'
import Header from '@/components/organisms/Header'
import { GradientOrb } from '@/components/ui/floating-card'

function ShellLayout({ children }: { children: ReactNode }) {
  const { mobileNavOpen, setMobileNavOpen } = useShell()

  return (
    <div className="relative flex min-h-screen bg-background">
      <GradientOrb className="pointer-events-none fixed left-0 top-0 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 opacity-40" />
      <GradientOrb className="pointer-events-none fixed bottom-0 right-0 h-[400px] w-[400px] translate-x-1/3 translate-y-1/3 bg-[radial-gradient(circle,rgba(52,211,153,0.2)_0%,transparent_70%)] opacity-30" />

      {mobileNavOpen && (
        <button
          type="button"
          aria-label="Fermer le menu"
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileNavOpen(false)}
        />
      )}
      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col lg:pl-64">
        <Header />
        <main className="flex-1 px-4 pb-8 pt-20 sm:px-6 lg:px-8 lg:pb-10 lg:pt-16">{children}</main>
      </div>
    </div>
  )
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <ShellProvider>
      <ShellLayout>{children}</ShellLayout>
    </ShellProvider>
  )
}
