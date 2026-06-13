'use client'

import { usePathname } from 'next/navigation'
import { AppShell } from '@/components/shell/AppShell'
import { MarketingShell } from '@/components/marketing/MarketingShell'
import { PrivateRoute } from '@/components/auth/PrivateRoute'

const MARKETING_ROUTES = ['/', '/login', '/pricing']

function isMarketingRoute(pathname: string | null): boolean {
  if (!pathname) return false
  return MARKETING_ROUTES.includes(pathname)
}

export function ConditionalRoot({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  if (isMarketingRoute(pathname)) {
    return <MarketingShell>{children}</MarketingShell>
  }
  return (
    <PrivateRoute>
      <AppShell>{children}</AppShell>
    </PrivateRoute>
  )
}
