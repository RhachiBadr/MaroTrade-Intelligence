'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Building2,
  Check,
  ChevronLeft,
  Eye,
  EyeOff,
  Factory,
  Globe2,
  Lock,
  Mail,
  MapPin,
  PackageCheck,
  ShieldCheck,
  Sparkles,
  Store,
  Users,
} from 'lucide-react'
import { AnimatedButton } from '@/components/ui/animated-button'
import { GlassCard } from '@/components/ui/glass-card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { easeOut } from '@/lib/motion'

type AuthMode = 'login' | 'signup' | 'forgot' | 'verify'
type FormErrors = Record<string, string>

const MOROCCAN_CITIES = [
  'Casablanca',
  'Agadir',
  'Marrakech',
  'Fes',
  'Tanger',
  'Rabat',
  'Meknes',
  'Oujda',
  'Laayoune',
  'Dakhla',
]

const SECTORS = [
  'Agroalimentaire',
  'Produits du terroir',
  'Cooperative agricole',
  'Artisanat',
  'Textile et cuir',
  'Cosmetiques naturels',
  'Peche et conserves',
  'Industrie legere',
]

const COMPANY_SIZES = [
  '1-5 personnes',
  '6-20 personnes',
  '21-50 personnes',
  '51-200 personnes',
  '200+ personnes',
]

const EXPORT_EXPERIENCE = [
  'Je demarre',
  'Premieres commandes',
  'Export regulier',
  'Equipe export structuree',
]

const TARGET_MARKETS = ['France', 'Espagne', 'Allemagne', 'USA', 'Canada', 'UAE', 'Arabie Saoudite', 'Afrique de l Ouest']

const TRUST_POINTS = [
  'Scoring marches adapte aux PME marocaines',
  'Veille FDA, RASFF, EUDR et certification halal',
  'Onboarding pense pour cooperatives et exportateurs',
]

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function Field({
  label,
  name,
  type = 'text',
  value,
  placeholder,
  error,
  icon: Icon,
  onChange,
  autoComplete,
  children,
}: {
  label: string
  name: string
  type?: string
  value: string
  placeholder?: string
  error?: string
  icon?: React.ComponentType<{ className?: string }>
  onChange: (value: string) => void
  autoComplete?: string
  children?: React.ReactNode
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="text-sm font-medium text-text-secondary">
        {label}
      </label>
      <div className="relative">
        {Icon && <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />}
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          placeholder={placeholder}
          autoComplete={autoComplete}
          onChange={(event) => onChange(event.target.value)}
          aria-invalid={!!error}
          className={cn(
            'h-11 w-full rounded-xl border bg-white/[0.045] px-3 py-2 text-sm text-text-primary shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] outline-none backdrop-blur-xl transition-all',
            Icon && 'pl-10',
            children && 'pr-11',
            error
              ? 'border-danger-500/50 focus:border-danger-500 focus:ring-2 focus:ring-danger-500/20'
              : 'border-white/10 focus:border-primary-400/60 focus:ring-2 focus:ring-primary-400/20',
            'placeholder:text-text-muted'
          )}
        />
        {children}
      </div>
      {error && <p className="text-xs font-medium text-danger-500">{error}</p>}
    </div>
  )
}

function SelectField({
  label,
  name,
  value,
  options,
  error,
  icon: Icon,
  onChange,
}: {
  label: string
  name: string
  value: string
  options: string[]
  error?: string
  icon?: React.ComponentType<{ className?: string }>
  onChange: (value: string) => void
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="text-sm font-medium text-text-secondary">
        {label}
      </label>
      <div className="relative">
        {Icon && <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />}
        <select
          id={name}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className={cn(
            'h-11 w-full appearance-none rounded-xl border bg-[#0b0b14]/90 px-3 py-2 text-sm text-text-primary outline-none transition-all',
            Icon && 'pl-10',
            error
              ? 'border-danger-500/50 focus:border-danger-500 focus:ring-2 focus:ring-danger-500/20'
              : 'border-white/10 focus:border-primary-400/60 focus:ring-2 focus:ring-primary-400/20'
          )}
        >
          <option value="">Selectionner</option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      {error && <p className="text-xs font-medium text-danger-500">{error}</p>}
    </div>
  )
}

function PillPicker({
  label,
  values,
  options,
  error,
  onToggle,
}: {
  label: string
  values: string[]
  options: string[]
  error?: string
  onToggle: (value: string) => void
}) {
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-text-secondary">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const active = values.includes(option)
          return (
            <button
              key={option}
              type="button"
              onClick={() => onToggle(option)}
              className={cn(
                'rounded-full border px-3 py-2 text-xs font-semibold transition-all',
                active
                  ? 'border-primary-400/50 bg-primary-500/20 text-primary-100 shadow-[0_0_28px_rgba(99,102,241,0.18)]'
                  : 'border-white/10 bg-white/[0.035] text-text-muted hover:border-white/20 hover:text-text-primary'
              )}
            >
              {option}
            </button>
          )
        })}
      </div>
      {error && <p className="text-xs font-medium text-danger-500">{error}</p>}
    </div>
  )
}

function PasswordStrength({ password }: { password: string }) {
  const score = useMemo(() => {
    let value = 0
    if (password.length >= 8) value += 1
    if (/[A-Z]/.test(password)) value += 1
    if (/[0-9]/.test(password)) value += 1
    if (/[^A-Za-z0-9]/.test(password)) value += 1
    return value
  }, [password])

  const labels = ['Trop faible', 'Faible', 'Correct', 'Bon', 'Solide']
  const colors = ['bg-danger-500', 'bg-danger-500', 'bg-warning-500', 'bg-primary-400', 'bg-accent-500']

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-4 gap-1.5">
        {[0, 1, 2, 3].map((item) => (
          <span key={item} className={cn('h-1.5 rounded-full bg-white/10', item < score && colors[score])} />
        ))}
      </div>
      <p className="text-xs text-text-muted">Securite : {labels[score]}</p>
    </div>
  )
}

export default function LoginPage() {
  const [mode, setMode] = useState<AuthMode>('login')
  const [step, setStep] = useState(1)
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(true)
  const [errors, setErrors] = useState<FormErrors>({})
  const [notice, setNotice] = useState('')

  const [login, setLogin] = useState({ email: '', password: '' })
  const [forgotEmail, setForgotEmail] = useState('')
  const [verifyCode, setVerifyCode] = useState('')
  const [signup, setSignup] = useState({
    company: '',
    email: '',
    password: '',
    country: 'Maroc',
    city: '',
    sector: '',
    size: '',
    products: '',
    markets: [] as string[],
    experience: '',
  })

  function setSignupField<K extends keyof typeof signup>(key: K, value: (typeof signup)[K]) {
    setSignup((current) => ({ ...current, [key]: value }))
    setErrors((current) => ({ ...current, [key]: '' }))
  }

  function setLoginField(key: keyof typeof login, value: string) {
    setLogin((current) => ({ ...current, [key]: value }))
    setErrors((current) => ({ ...current, [key]: '' }))
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode)
    setErrors({})
    setNotice('')
  }

  function validateLogin() {
    const nextErrors: FormErrors = {}
    if (!emailRegex.test(login.email)) nextErrors.email = 'Entrez un email professionnel valide.'
    if (!login.password) nextErrors.password = 'Le mot de passe est requis.'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  function validateStep(currentStep: number) {
    const nextErrors: FormErrors = {}
    if (currentStep === 1) {
      if (signup.company.trim().length < 2) nextErrors.company = 'Nom entreprise ou cooperative requis.'
      if (!emailRegex.test(signup.email)) nextErrors.email = 'Email professionnel valide requis.'
      if (signup.password.length < 8) nextErrors.password = 'Minimum 8 caracteres.'
    }
    if (currentStep === 2) {
      if (!signup.country.trim()) nextErrors.country = 'Pays requis.'
      if (!signup.city) nextErrors.city = 'Ville requise.'
      if (!signup.sector) nextErrors.sector = 'Secteur requis.'
      if (!signup.size) nextErrors.size = 'Taille requise.'
    }
    if (currentStep === 3) {
      if (signup.products.trim().length < 2) nextErrors.products = 'Ajoutez au moins un produit.'
      if (signup.markets.length === 0) nextErrors.markets = 'Choisissez au moins un marche cible.'
      if (!signup.experience) nextErrors.experience = 'Selectionnez votre experience export.'
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  function handleLoginSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!validateLogin()) return
    setNotice('Connexion prete. Branchez ici votre API auth/JWT lorsque le backend sera active.')
  }

  function handleForgotSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!emailRegex.test(forgotEmail)) {
      setErrors({ forgotEmail: 'Entrez votre email professionnel.' })
      return
    }
    setErrors({})
    setMode('verify')
    setNotice('Lien de recuperation envoye. Entrez le code recu par email pour continuer.')
  }

  function handleSignupNext(event: React.FormEvent) {
    event.preventDefault()
    if (!validateStep(step)) return
    if (step < 3) {
      setStep((current) => current + 1)
      return
    }
    setMode('verify')
    setNotice(`Compte cree pour ${signup.company}. Un code de verification a ete envoye a ${signup.email}.`)
  }

  function handleVerify(event: React.FormEvent) {
    event.preventDefault()
    if (!/^\d{6}$/.test(verifyCode)) {
      setErrors({ verifyCode: 'Code a 6 chiffres requis.' })
      return
    }
    setErrors({})
    setNotice('Email verifie. Votre espace export est pret.')
  }

  const progress = mode === 'signup' ? (step / 3) * 100 : 0

  return (
    <div className="relative min-h-[calc(100vh-5rem)] overflow-hidden px-4 py-10 sm:px-6 lg:px-8">
      <div className="aurora-field pointer-events-none absolute inset-x-0 top-0 h-[680px] opacity-60" aria-hidden />
      <div className="light-grid pointer-events-none absolute inset-0 opacity-35" aria-hidden />

      <div className="relative mx-auto grid min-h-[calc(100vh-9rem)] w-full max-w-7xl min-w-0 items-center gap-8 lg:grid-cols-[0.92fr_1.08fr]">
        <motion.aside
          initial={{ opacity: 0, x: -28 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.55, ease: easeOut }}
          className="hidden lg:block"
        >
          <Badge variant="primary" className="mb-6 gap-1.5">
            <Sparkles className="h-3.5 w-3.5" />
            Espace export intelligent
          </Badge>
          <h1 className="max-w-xl text-5xl font-semibold leading-[1.02] tracking-tight text-text-primary xl:text-6xl">
            Une porte d entree premium pour vos decisions export.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-text-secondary">
            Connectez votre entreprise, cooperative ou equipe export a un cockpit qui comprend les produits marocains,
            les marches cibles, la conformite et les signaux de croissance.
          </p>

          <div className="mt-10 grid max-w-xl gap-4">
            {TRUST_POINTS.map((point) => (
              <div key={point} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.035] p-4 backdrop-blur-xl">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-500/15 text-accent-500">
                  <Check className="h-4 w-4" />
                </span>
                <p className="text-sm font-medium text-text-secondary">{point}</p>
              </div>
            ))}
          </div>

          <GlassCard tilt glow className="mt-10 max-w-xl p-5">
            <div className="grid grid-cols-3 gap-3">
              {[
                ['PME', 'Analyse rapide'],
                ['Coop', 'Produits terroir'],
                ['Export', 'Marches cibles'],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl border border-white/10 bg-black/20 p-4">
                  <p className="text-2xl font-semibold gradient-text">{label}</p>
                  <p className="mt-1 text-xs text-text-muted">{value}</p>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.aside>

        <motion.div
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08, ease: easeOut }}
          className="mx-auto w-full max-w-[calc(100vw-2rem)] min-w-0 sm:max-w-2xl"
        >
          <GlassCard glow className="w-full min-w-0 overflow-hidden p-0 shadow-[0_34px_130px_rgba(0,0,0,0.35)]">
            <div className="border-b border-white/10 p-5 sm:p-6">
              <div className="mb-5 flex items-center justify-between gap-4">
                <Link href="/" className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 via-sky-500 to-accent-500 text-white shadow-lg shadow-primary-600/30">
                    <Globe2 className="h-5 w-5" />
                  </span>
                  <span className="font-semibold text-text-primary">MaroTrade</span>
                </Link>
                <Badge variant="success" className="hidden sm:inline-flex">
                  Secure workspace
                </Badge>
              </div>

              <div className="grid min-w-0 grid-cols-2 rounded-xl border border-white/10 bg-white/[0.035] p-1">
                {[
                  ['login', 'Connexion'],
                  ['signup', 'Creer un compte'],
                ].map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => switchMode(value as AuthMode)}
                    className={cn(
                      'truncate rounded-lg px-2 py-2.5 text-xs font-semibold transition-all sm:px-3 sm:text-sm',
                      mode === value
                        ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                        : 'text-text-muted hover:text-text-primary'
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {notice && (
              <div className="mx-5 mt-5 rounded-xl border border-accent-500/20 bg-accent-500/10 px-4 py-3 text-sm text-accent-500 sm:mx-6">
                {notice}
              </div>
            )}

            <div className="min-w-0 p-5 sm:p-6">
              <AnimatePresence mode="wait">
                {mode === 'login' && (
                  <motion.form
                    key="login"
                    initial={{ opacity: 0, x: 18 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -18 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleLoginSubmit}
                    className="space-y-5"
                  >
                    <div>
                      <h2 className="text-2xl font-semibold tracking-tight text-text-primary">Bon retour</h2>
                      <p className="mt-2 text-sm leading-6 text-text-muted">
                        Accedez a vos analyses, alertes reglementaires et marches sauvegardes.
                      </p>
                    </div>

                    <Field
                      label="Email professionnel"
                      name="email"
                      type="email"
                      value={login.email}
                      placeholder="vous@entreprise.ma"
                      error={errors.email}
                      icon={Mail}
                      autoComplete="email"
                      onChange={(value) => setLoginField('email', value)}
                    />
                    <Field
                      label="Mot de passe"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={login.password}
                      placeholder="Minimum 8 caracteres"
                      error={errors.password}
                      icon={Lock}
                      autoComplete="current-password"
                      onChange={(value) => setLoginField('password', value)}
                    >
                      <button
                        type="button"
                        onClick={() => setShowPassword((current) => !current)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted transition-colors hover:text-text-primary"
                        aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </Field>

                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <label className="flex cursor-pointer items-center gap-2 text-sm text-text-secondary">
                        <input
                          type="checkbox"
                          checked={remember}
                          onChange={(event) => setRemember(event.target.checked)}
                          className="h-4 w-4 rounded border-white/20 bg-white/5 text-primary-600 focus:ring-primary-500"
                        />
                        Se souvenir de moi
                      </label>
                      <button
                        type="button"
                        onClick={() => switchMode('forgot')}
                        className="text-sm font-medium text-primary-300 transition-colors hover:text-accent-500"
                      >
                        Mot de passe oublie ?
                      </button>
                    </div>

                    <AnimatedButton type="submit" className="w-full">
                      Se connecter
                    </AnimatedButton>

                    <div className="grid gap-2 sm:grid-cols-2">
                      <AnimatedButton href="/dashboard" variant="secondary" className="w-full">
                        Mode demo dashboard
                      </AnimatedButton>
                      <AnimatedButton href="/analyze" variant="ghost" className="w-full">
                        Lancer une analyse
                      </AnimatedButton>
                    </div>
                  </motion.form>
                )}

                {mode === 'signup' && (
                  <motion.form
                    key={`signup-${step}`}
                    initial={{ opacity: 0, x: 18 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -18 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleSignupNext}
                    className="space-y-5"
                  >
                    <div>
                      <div className="mb-4 flex items-center justify-between gap-4">
                        <div>
                          <h2 className="text-2xl font-semibold tracking-tight text-text-primary">Creation du compte</h2>
                          <p className="mt-1 text-sm text-text-muted">Etape {step}/3 - profil export intelligent</p>
                        </div>
                        {step > 1 && (
                          <button
                            type="button"
                            onClick={() => setStep((current) => current - 1)}
                            className="inline-flex items-center gap-1 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary transition-colors hover:bg-white/5"
                          >
                            <ChevronLeft className="h-3.5 w-3.5" />
                            Retour
                          </button>
                        )}
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          className="h-full rounded-full bg-gradient-to-r from-primary-500 via-sky-400 to-accent-500"
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 0.35, ease: easeOut }}
                        />
                      </div>
                    </div>

                    {step === 1 && (
                      <div className="grid gap-5">
                        <Field
                          label="Nom entreprise / cooperative"
                          name="company"
                          value={signup.company}
                          placeholder="Ex. Cooperative Targanine"
                          error={errors.company}
                          icon={Building2}
                          autoComplete="organization"
                          onChange={(value) => setSignupField('company', value)}
                        />
                        <Field
                          label="Email professionnel"
                          name="signup-email"
                          type="email"
                          value={signup.email}
                          placeholder="contact@cooperative.ma"
                          error={errors.email}
                          icon={Mail}
                          autoComplete="email"
                          onChange={(value) => setSignupField('email', value)}
                        />
                        <Field
                          label="Mot de passe"
                          name="signup-password"
                          type={showPassword ? 'text' : 'password'}
                          value={signup.password}
                          placeholder="Minimum 8 caracteres"
                          error={errors.password}
                          icon={Lock}
                          autoComplete="new-password"
                          onChange={(value) => setSignupField('password', value)}
                        >
                          <button
                            type="button"
                            onClick={() => setShowPassword((current) => !current)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted transition-colors hover:text-text-primary"
                            aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </Field>
                        <PasswordStrength password={signup.password} />
                      </div>
                    )}

                    {step === 2 && (
                      <div className="grid gap-5 sm:grid-cols-2">
                        <Field
                          label="Pays"
                          name="country"
                          value={signup.country}
                          placeholder="Maroc"
                          error={errors.country}
                          icon={Globe2}
                          onChange={(value) => setSignupField('country', value)}
                        />
                        <SelectField
                          label="Ville"
                          name="city"
                          value={signup.city}
                          options={MOROCCAN_CITIES}
                          error={errors.city}
                          icon={MapPin}
                          onChange={(value) => setSignupField('city', value)}
                        />
                        <SelectField
                          label="Secteur d activite"
                          name="sector"
                          value={signup.sector}
                          options={SECTORS}
                          error={errors.sector}
                          icon={Factory}
                          onChange={(value) => setSignupField('sector', value)}
                        />
                        <SelectField
                          label="Taille entreprise / cooperative"
                          name="size"
                          value={signup.size}
                          options={COMPANY_SIZES}
                          error={errors.size}
                          icon={Users}
                          onChange={(value) => setSignupField('size', value)}
                        />
                      </div>
                    )}

                    {step === 3 && (
                      <div className="space-y-5">
                        <Field
                          label="Produits exportes"
                          name="products"
                          value={signup.products}
                          placeholder="Ex. huile d argan, dattes, sardines, zellige"
                          error={errors.products}
                          icon={PackageCheck}
                          onChange={(value) => setSignupField('products', value)}
                        />
                        <PillPicker
                          label="Marches cibles"
                          values={signup.markets}
                          options={TARGET_MARKETS}
                          error={errors.markets}
                          onToggle={(market) =>
                            setSignupField(
                              'markets',
                              signup.markets.includes(market)
                                ? signup.markets.filter((item) => item !== market)
                                : [...signup.markets, market]
                            )
                          }
                        />
                        <SelectField
                          label="Experience export"
                          name="experience"
                          value={signup.experience}
                          options={EXPORT_EXPERIENCE}
                          error={errors.experience}
                          icon={Store}
                          onChange={(value) => setSignupField('experience', value)}
                        />
                      </div>
                    )}

                    <AnimatedButton type="submit" className="w-full">
                      {step < 3 ? 'Continuer' : 'Creer et verifier mon email'}
                    </AnimatedButton>
                  </motion.form>
                )}

                {mode === 'forgot' && (
                  <motion.form
                    key="forgot"
                    initial={{ opacity: 0, x: 18 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -18 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleForgotSubmit}
                    className="space-y-5"
                  >
                    <button
                      type="button"
                      onClick={() => switchMode('login')}
                      className="inline-flex items-center gap-1 text-sm font-medium text-text-muted transition-colors hover:text-text-primary"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Retour connexion
                    </button>
                    <div>
                      <h2 className="text-2xl font-semibold tracking-tight text-text-primary">Recuperation du mot de passe</h2>
                      <p className="mt-2 text-sm leading-6 text-text-muted">
                        Recevez un lien securise et un code de verification sur votre email professionnel.
                      </p>
                    </div>
                    <Field
                      label="Email professionnel"
                      name="forgot-email"
                      type="email"
                      value={forgotEmail}
                      placeholder="vous@entreprise.ma"
                      error={errors.forgotEmail}
                      icon={Mail}
                      onChange={(value) => {
                        setForgotEmail(value)
                        setErrors({})
                      }}
                    />
                    <AnimatedButton type="submit" className="w-full">
                      Envoyer le lien de recuperation
                    </AnimatedButton>
                  </motion.form>
                )}

                {mode === 'verify' && (
                  <motion.form
                    key="verify"
                    initial={{ opacity: 0, x: 18 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -18 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleVerify}
                    className="space-y-5"
                  >
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-500/15 text-accent-500">
                      <ShieldCheck className="h-7 w-7" />
                    </div>
                    <div className="text-center">
                      <h2 className="text-2xl font-semibold tracking-tight text-text-primary">Verification email</h2>
                      <p className="mt-2 text-sm leading-6 text-text-muted">
                        Entrez le code a 6 chiffres envoye a votre adresse professionnelle.
                      </p>
                    </div>
                    <Field
                      label="Code de verification"
                      name="verify-code"
                      value={verifyCode}
                      placeholder="123456"
                      error={errors.verifyCode}
                      icon={ShieldCheck}
                      onChange={(value) => {
                        setVerifyCode(value.replace(/\D/g, '').slice(0, 6))
                        setErrors({})
                      }}
                    />
                    <AnimatedButton type="submit" className="w-full">
                      Verifier mon email
                    </AnimatedButton>
                    <button
                      type="button"
                      onClick={() => setNotice('Nouveau code envoye. Verifiez votre boite email professionnelle.')}
                      className="w-full rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
                    >
                      Renvoyer le code
                    </button>
                  </motion.form>
                )}
              </AnimatePresence>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}
