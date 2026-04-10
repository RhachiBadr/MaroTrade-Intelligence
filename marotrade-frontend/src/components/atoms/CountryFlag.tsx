import { cn } from '@/lib/utils'

interface Props {
  flag: string
  name: string
  code?: string
  className?: string
}

/** Country flag emoji + name */
export function CountryFlag({ flag, name, code, className }: Props) {
  return (
    <span className={cn('inline-flex items-center gap-2', className)}>
      <span className="text-xl">{flag}</span>
      <span className="font-medium">{name}</span>
      {code && <span className="text-xs text-gray-400">({code})</span>}
    </span>
  )
}
