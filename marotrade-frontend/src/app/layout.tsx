import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/organisms/Sidebar'
import Header from '@/components/organisms/Header'
import { Providers } from '@/app/providers'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'MaroTrade Intelligence — Export Analytics',
  description: "B2B SaaS platform for Export Intelligence.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                  document.documentElement.classList.add('dark')
                } else {
                  document.documentElement.classList.remove('dark')
                }
              } catch (_) {}
            `,
          }}
        />
      </head>
      <body className={`${inter.variable} font-sans bg-background text-text-primary antialiased selection:bg-primary-500 selection:text-white transition-colors duration-200`}>
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0 transition-all duration-200 ml-60 lg:ml-60">
              <Header />
              <main className="flex-1 p-6 lg:p-8 mt-16 animate-slide-down">
                {children}
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}
