'use client'

import { motion, useReducedMotion } from 'framer-motion'

export function HeroAtmosphere() {
  const reduceMotion = useReducedMotion()

  return (
    <>
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-background via-background/55 to-background"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-background/85 via-transparent to-background/85" />
      <motion.div
        className="absolute inset-x-0 top-0 h-[38%] bg-gradient-to-b from-background via-background/70 to-transparent"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2, delay: 0.2 }}
      />
      <div className="absolute inset-x-0 bottom-0 h-[45%] bg-gradient-to-t from-background via-background/92 to-transparent" />

      <motion.div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 75% 55% at 50% 42%, transparent 0%, var(--background) 72%)',
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.4 }}
      />

      <div className="hero-noise absolute inset-0" aria-hidden />

      <motion.div className="absolute inset-0 backdrop-blur-[2px] sm:backdrop-blur-[3px]" />

      <div
        className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(129,140,248,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(129,140,248,0.6) 1px, transparent 1px)',
          backgroundSize: '72px 72px',
        }}
      />

      {!reduceMotion && (
        <motion.div
          className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-primary-400/15 to-transparent"
          animate={{ top: ['18%', '78%', '18%'] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />
      )}

      {!reduceMotion && (
        <motion.div
          className="absolute inset-x-0 bottom-[32%] h-px bg-gradient-to-r from-transparent via-accent-500/10 to-transparent"
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}
    </>
  )
}
