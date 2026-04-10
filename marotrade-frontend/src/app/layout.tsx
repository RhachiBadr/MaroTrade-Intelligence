import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/organisms/Sidebar'
import Header from '@/components/organisms/Header'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'MaroTrade Intelligence — Export Analytics',
  description: "Identifiez vos meilleurs marchés d'export en 60 secondes. Scoring IA · Veille réglementaire · Prévisions 2026.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans bg-background text-text-primary antialiased`}>
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
              <Header />
              <main className="flex-1 p-8 ml-64">
                {children}
              </main>
              <footer className="ml-64 py-8 text-center text-sm text-text-muted border-t border-border mt-auto">
                MaroTrade Intelligence · Made in 🇲🇦 · {new Date().getFullYear()}
              </footer>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}
