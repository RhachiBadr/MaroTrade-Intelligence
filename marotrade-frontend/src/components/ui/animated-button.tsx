'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

type AnimatedButtonProps = {
  href?: string
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  className?: string
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit'
}

const variants = {
  primary: 'bg-primary-600 text-white shadow-lg shadow-primary-600/25 hover:bg-primary-500 hover:shadow-primary-500/30',
  secondary: 'glass text-text-primary hover:bg-white/10',
  ghost: 'text-text-secondary hover:text-text-primary hover:bg-white/5',
}

const sizes = {
  sm: 'h-9 px-4 text-sm',
  md: 'h-11 px-6 text-sm',
  lg: 'h-12 px-8 text-base',
}

export function AnimatedButton({
  href,
  variant = 'primary',
  size = 'md',
  className,
  children,
  onClick,
  type = 'button',
}: AnimatedButtonProps) {
  const classes = cn(
    'relative inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors overflow-hidden',
    variants[variant],
    sizes[size],
    className
  )

  const content = (
    <>
      {variant === 'primary' && (
        <motion.span
          className="absolute inset-0 bg-gradient-to-r from-primary-400/0 via-white/20 to-primary-400/0"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
        />
      )}
      <span className="relative">{children}</span>
    </>
  )

  if (href) {
    return (
      <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
        <Link href={href} className={classes}>
          {content}
        </Link>
      </motion.div>
    )
  }

  return (
    <motion.button
      type={type}
      onClick={onClick}
      className={classes}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {content}
    </motion.button>
  )
}
