'use client'

import { motion } from 'framer-motion'
import { pageTransition } from '@/lib/motion'

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={pageTransition.initial} animate={pageTransition.animate} exit={pageTransition.exit} transition={pageTransition.transition}>
      {children}
    </motion.div>
  )
}
