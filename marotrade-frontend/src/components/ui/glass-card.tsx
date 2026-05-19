import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

type GlassCardProps = HTMLAttributes<HTMLDivElement> & {
  hover?: boolean
  glow?: boolean
}

export function GlassCard({ className, hover = true, glow = false, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'glass rounded-xl shadow-md',
        hover && 'transition-all duration-300 hover:border-white/20 hover:shadow-lg',
        glow && 'shadow-[0_0_60px_rgba(99,102,241,0.15)]',
        className
      )}
      {...props}
    />
  )
}

export function GlassCardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('border-b border-border px-5 py-4', className)} {...props} />
}

export function GlassCardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-5', className)} {...props} />
}
