import type { Metadata } from 'next'
import { LandingPage } from '@/components/marketing/LandingPage'

export const metadata: Metadata = {
  title: 'MaroTrade Intelligence — Intelligence export pour PME marocaines',
  description:
    'Scoring de marchés (XGBoost, SHAP), veille réglementaire internationale et prévisions. Priorisez vos exportations avec une plateforme moderne.',
  openGraph: {
    title: 'MaroTrade Intelligence',
    description: 'Décidez où exporter : données, ML et conformité dans une seule suite.',
    locale: 'fr_FR',
    type: 'website',
  },
}

export default function Home() {
  return <LandingPage />
}
