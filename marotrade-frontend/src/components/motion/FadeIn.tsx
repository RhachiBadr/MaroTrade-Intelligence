'use client'

import { motion, type HTMLMotionProps } from 'framer-motion'
import { fadeUpVariants, easeOut } from '@/lib/motion'
import { cn } from '@/lib/utils'

type FadeInProps = HTMLMotionProps<'div'> & {
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'none'
}

const directionOffset = {
  up: { y: 24 },
  down: { y: -24 },
  left: { x: 24 },
  right: { x: -24 },
  none: {},
}

export function FadeIn({ children, className, delay = 0, direction = 'up', ...props }: FadeInProps) {
  const offset = directionOffset[direction]
  return (
    <motion.div
      initial={{ opacity: 0, ...offset }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, ease: easeOut, delay }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export function FadeInStagger({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-40px' }}
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.08 } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function FadeInItem({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div variants={fadeUpVariants} transition={{ duration: 0.45, ease: easeOut }} className={className}>
      {children}
    </motion.div>
  )
}
