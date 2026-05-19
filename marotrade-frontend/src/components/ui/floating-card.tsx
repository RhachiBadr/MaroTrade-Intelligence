'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

type FloatingCardProps = {
  children: React.ReactNode
  className?: string
  delay?: number
  floatIntensity?: number
}

export function FloatingCard({ children, className, delay = 0, floatIntensity = 8 }: FloatingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn('glass rounded-xl p-5 shadow-lg', className)}
    >
      <motion.div
        animate={{ y: [-floatIntensity / 2, floatIntensity / 2, -floatIntensity / 2] }}
        transition={{ duration: 4 + delay, repeat: Infinity, ease: 'easeInOut' }}
      >
        {children}
      </motion.div>
    </motion.div>
  )
}

export function GradientOrb({ className }: { className?: string }) {
  return (
    <div
      className={cn('pointer-events-none absolute rounded-full glow-orb', className)}
      aria-hidden
    />
  )
}
