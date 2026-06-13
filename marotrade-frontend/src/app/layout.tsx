import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ConditionalRoot } from '@/components/shell/ConditionalRoot'
import { Providers } from '@/app/providers'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: { default: 'MaroTrade Intelligence', template: '%s · MaroTrade Intelligence' },
  description: 'Intelligence export pour PME marocaines : scoring marchés, veille réglementaire, prévisions.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning data-scroll-behavior="smooth">
      <body className={`${inter.variable} bg-background font-sans text-text-primary antialiased selection:bg-primary-500 selection:text-white transition-colors duration-200`}>
        <Providers>
          <ConditionalRoot>{children}</ConditionalRoot>
        </Providers>
      </body>
    </html>
  )
}
