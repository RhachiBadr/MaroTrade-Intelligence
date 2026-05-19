'use client'

import { motion, useReducedMotion } from 'framer-motion'

const BLOBS = [
  {
    className: 'left-[10%] top-[15%] h-[420px] w-[420px]',
    color: 'rgba(99, 102, 241, 0.45)',
    animate: { x: [0, 40, 0], y: [0, -30, 0], scale: [1, 1.08, 1] },
    duration: 22,
  },
  {
    className: 'right-[5%] top-[25%] h-[380px] w-[380px]',
    color: 'rgba(52, 211, 153, 0.35)',
    animate: { x: [0, -35, 0], y: [0, 25, 0], scale: [1, 1.05, 1] },
    duration: 26,
    delay: 3,
  },
  {
    className: 'left-[35%] bottom-[10%] h-[360px] w-[360px]',
    color: 'rgba(139, 92, 246, 0.28)',
    animate: { x: [0, 25, 0], y: [0, -20, 0], scale: [1, 1.1, 1] },
    duration: 20,
    delay: 1.5,
  },
  {
    className: 'right-[30%] top-[55%] h-[280px] w-[280px]',
    color: 'rgba(56, 189, 248, 0.2)',
    animate: { x: [0, -20, 0], y: [0, 15, 0], scale: [1, 1.06, 1] },
    duration: 18,
    delay: 5,
  },
]

export function AnimatedMeshGradient() {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div
      className="absolute inset-0"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.4 }}
    >
      <motion.div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99,102,241,0.12) 0%, transparent 55%), radial-gradient(ellipse 60% 40% at 100% 50%, rgba(52,211,153,0.08) 0%, transparent 50%)',
        }}
        animate={reduceMotion ? undefined : { opacity: [0.85, 1, 0.85] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />

      {BLOBS.map((blob, i) =>
        reduceMotion ? (
          <motion.div
            key={i}
            className={`absolute rounded-full blur-[100px] ${blob.className}`}
            style={{ background: `radial-gradient(circle, ${blob.color} 0%, transparent 70%)` }}
          />
        ) : (
          <motion.div
            key={i}
            className={`absolute rounded-full blur-[100px] ${blob.className}`}
            style={{ background: `radial-gradient(circle, ${blob.color} 0%, transparent 70%)` }}
            animate={blob.animate}
            transition={{
              duration: blob.duration,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: blob.delay ?? 0,
            }}
          />
        )
      )}
    </motion.div>
  )
}
