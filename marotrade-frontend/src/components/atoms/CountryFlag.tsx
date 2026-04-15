import Image from 'next/image'

export function CountryFlag({ code, name }: { code: string, name: string }) {
  const lowerCode = code.toLowerCase()
  return (
    <div className="w-6 h-4 relative shrink-0 overflow-hidden border border-border/50 rounded-sm bg-secondary">
      {code ? (
        <Image
          src={`https://flagcdn.com/w20/${lowerCode}.png`}
          alt={name}
          fill
          className="object-cover"
          unoptimized
        />
      ) : (
        <span className="text-[8px] font-bold text-text-muted absolute inset-0 flex items-center justify-center">{code || '??'}</span>
      )}
    </div>
  )
}
