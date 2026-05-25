import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

type GlassCardProps = HTMLAttributes<HTMLDivElement> & {
  hover?: boolean
  glow?: boolean
  tilt?: boolean
}

export function GlassCard({ className, hover = true, glow = false, tilt = false, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'glass premium-card rounded-xl shadow-md',
        hover && 'transition-all duration-500 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_24px_90px_rgba(79,70,229,0.18)]',
        glow && 'premium-glow shadow-[0_0_80px_rgba(99,102,241,0.2)]',
        tilt && 'tilt-card',
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
