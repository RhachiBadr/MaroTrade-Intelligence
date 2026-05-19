'use client'

import { motion, useReducedMotion } from 'framer-motion'

const ROUTES = [
  { d: 'M 80 300 Q 220 140 400 210', duration: 8 },
  { d: 'M 120 280 Q 300 200 480 250', duration: 10 },
  { d: 'M 60 320 Q 180 220 360 180', duration: 9 },
]

export function HeroDataFlow() {
  const reduceMotion = useReducedMotion()
  if (reduceMotion) return null

  return (
    <svg
      className="absolute inset-0 h-full w-full opacity-[0.14]"
      viewBox="0 0 560 400"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden
    >
      <defs>
        <linearGradient id="hero-route-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#818cf8" stopOpacity="0" />
          <stop offset="45%" stopColor="#34d399" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
        </linearGradient>
      </defs>
      {ROUTES.map(({ d, duration }, i) => (
        <motion.path
          key={i}
          d={d}
          fill="none"
          stroke="url(#hero-route-grad)"
          strokeWidth="1"
          strokeLinecap="round"
          strokeDasharray="4 12"
          initial={{ strokeDashoffset: 0, opacity: 0.3 }}
          animate={{ strokeDashoffset: -80, opacity: [0.25, 0.5, 0.25] }}
          transition={{
            strokeDashoffset: { duration, repeat: Infinity, ease: 'linear' },
            opacity: { duration: duration * 0.8, repeat: Infinity, ease: 'easeInOut' },
          }}
        />
      ))}
    </svg>
  )
}
