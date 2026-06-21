import Image from 'next/image'
import { cn } from '@/lib/utils'

interface BrandLogoProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  priority?: boolean
}

const sizes = { sm: 'h-8 w-8', md: 'h-10 w-10', lg: 'h-14 w-14' }
const pixels = { sm: 32, md: 40, lg: 56 }

export function BrandLogo({ size = 'md', className, priority = false }: BrandLogoProps) {
  return (
    <span className={cn('relative inline-flex shrink-0 overflow-hidden rounded-xl border border-white/15 bg-white shadow-lg shadow-primary-600/20', sizes[size], className)}>
      <Image
        src="/brand/marotrade-logo.avif"
        alt="Logo MaroTrade Intelligence"
        width={pixels[size]}
        height={pixels[size]}
        priority={priority}
        className="h-full w-full object-cover"
      />
    </span>
  )
}
