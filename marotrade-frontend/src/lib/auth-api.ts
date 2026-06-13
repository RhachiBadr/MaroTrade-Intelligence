const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface AuthUser {
  id: string
  email: string
  name: string
  email_verified: boolean
  role: 'OWNER' | 'ADMIN' | 'MEMBER' | 'VIEWER'
}

export interface AuthOrganization {
  id: string
  name: string
  slug: string
  type: 'PME' | 'COOPERATIVE' | 'EXPORTER'
  country: string
  city?: string
  sector?: string
  size?: string
  products: string[]
  target_markets: string[]
  export_experience?: string
}

export interface AuthAccount {
  user: AuthUser
  organization: AuthOrganization
  verification_token_dev?: string
}

export interface WorkspaceAnalysis {
  id: string
  product_name: string
  hs_code: string
  top_n: number
  results: import('@/types').MarketResult[]
  created_at: string
}

async function authRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || 'Une erreur est survenue.')
  }
  return payload as T
}

export function loginAccount(payload: { email: string; password: string; remember: boolean }) {
  return authRequest<AuthAccount>('/auth/login', { method: 'POST', body: JSON.stringify(payload) })
}

export function registerAccount(payload: Record<string, unknown>) {
  return authRequest<AuthAccount>('/auth/register', { method: 'POST', body: JSON.stringify(payload) })
}

export function fetchCurrentAccount() {
  return authRequest<AuthAccount>('/auth/me')
}

export function logoutAccount() {
  return authRequest<{ logged_out: boolean }>('/auth/logout', { method: 'POST' })
}

export function verifyEmail(token: string) {
  return authRequest<{ verified: boolean }>('/auth/verify-email', {
    method: 'POST',
    body: JSON.stringify({ token }),
  })
}

export function requestPasswordReset(email: string) {
  return authRequest<{ sent: boolean; reset_token_dev?: string }>('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export function resetPassword(token: string, password: string) {
  return authRequest<{ password_reset: boolean }>('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, password }),
  })
}

export function fetchWorkspaceAnalyses() {
  return authRequest<WorkspaceAnalysis[]>('/api/me/analyses')
}

export function deleteWorkspaceAnalysis(id: string) {
  return authRequest<void>(`/api/me/analyses/${id}`, { method: 'DELETE' })
}
