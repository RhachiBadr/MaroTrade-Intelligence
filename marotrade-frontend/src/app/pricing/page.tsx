import type { Metadata } from 'next'
import { PricingPage } from '@/components/marketing/PricingPage'

export const metadata: Metadata = {
  title: 'Tarifs',
  description: 'Plans Starter, Pro et Enterprise pour MaroTrade Intelligence.',
}

export default function PricingRoute() {
  return <PricingPage />
}
