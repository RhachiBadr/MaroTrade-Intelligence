import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#F8FAFC',
        card:       '#FFFFFF',
        secondary:  '#F1F5F9',
        border:     '#E5E7EB',
        primary: {
          DEFAULT: '#2563EB',
          foreground: '#FFFFFF',
        },
        ai: {
          DEFAULT: '#8B5CF6', // Purple for AI features
        },
        success: '#16A34A',
        warning: '#F59E0B',
        danger:  '#DC2626',
        text: {
          primary:   '#0F172A',
          secondary: '#475569',
          muted:     '#94A3B8',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        display: ['Inter', 'sans-serif'], // User wants clean/minimal, Inter works best for both
      },
      animation: {
        'fade-in':    'fadeIn 0.5s ease-in-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn:  { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(16px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
export default config
