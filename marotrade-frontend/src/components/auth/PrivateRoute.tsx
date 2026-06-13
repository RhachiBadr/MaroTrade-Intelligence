'use client'

import { useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { ShieldCheck } from 'lucide-react'
import { useAuth } from '@/components/auth/AuthProvider'

export function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { account, loading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!loading && !account) {
      router.replace(`/login?next=${encodeURIComponent(pathname || '/dashboard')}`)
    }
  }, [account, loading, pathname, router])

  if (loading || !account) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-5 py-4 text-sm font-medium text-text-secondary shadow-sm">
          <ShieldCheck className="h-5 w-5 animate-pulse text-primary-600" />
          Vérification de votre espace sécurisé...
        </div>
      </div>
    )
  }

  return children
}
