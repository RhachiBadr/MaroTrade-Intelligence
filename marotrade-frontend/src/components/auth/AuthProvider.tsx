'use client'

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { AuthAccount } from '@/lib/auth-api'
import { fetchCurrentAccount, loginAccount, logoutAccount, registerAccount } from '@/lib/auth-api'

interface AuthContextValue {
  account: AuthAccount | null
  loading: boolean
  login: (payload: { email: string; password: string; remember: boolean }) => Promise<AuthAccount>
  register: (payload: Record<string, unknown>) => Promise<AuthAccount>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [account, setAccount] = useState<AuthAccount | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      setAccount(await fetchCurrentAccount())
    } catch {
      setAccount(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  async function login(payload: { email: string; password: string; remember: boolean }) {
    const next = await loginAccount(payload)
    setAccount(next)
    return next
  }

  async function register(payload: Record<string, unknown>) {
    const next = await registerAccount(payload)
    setAccount(next)
    return next
  }

  async function logout() {
    await logoutAccount()
    setAccount(null)
  }

  return <AuthContext.Provider value={{ account, loading, login, register, logout, refresh }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
