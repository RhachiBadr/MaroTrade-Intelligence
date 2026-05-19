'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { motion, useReducedMotion } from 'framer-motion'
import { AnimatedMeshGradient } from '@/components/marketing/hero/AnimatedMeshGradient'
import { HeroParticleCanvas } from '@/components/marketing/hero/HeroParticleCanvas'
import { HeroVideoLayer } from '@/components/marketing/hero/HeroVideoLayer'
import { HeroAtmosphere } from '@/components/marketing/hero/HeroAtmosphere'
import { HeroDataFlow } from '@/components/marketing/hero/HeroDataFlow'

const ExportGlobeScene = dynamic(
  () => import('@/components/three/ExportGlobeScene').then((m) => m.ExportGlobeScene),
  {
    ssr: false,
    loading: () => <HeroStaticFallback />,
  }
)

function HeroStaticFallback() {
  return (
    <motion.div
      className="absolute inset-0 mesh-gradient opacity-40"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      aria-hidden
    >
      <motion.div className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background" />
    </motion.div>
  )
}

export function HeroBackground() {
  const [quality, setQuality] = useState<'high' | 'low'>('high')
  const [visible, setVisible] = useState(true)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 768px)')
    const update = () => setQuality(mq.matches ? 'low' : 'high')
    update()
    mq.addEventListener('change', update)
    return () => mq.removeEventListener('change', update)
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.05 }
    )
    const el = document.getElementById('hero-section')
    if (el) observer.observe(el)
    return () => observer.disconnect()
  }, [])

  const show3d = visible && !reduceMotion

  return (
    <motion.div
      className="pointer-events-none absolute inset-0 overflow-hidden"
      aria-hidden
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Layer 1 — Stripe / Linear style mesh gradients */}
      <AnimatedMeshGradient />

      {/* Layer 2 — optional lightweight video (satellite / port / data) */}
      <HeroVideoLayer active={visible} />

      {/* Layer 3 — SVG logistics data-flow lines */}
      <HeroDataFlow />

      {/* Layer 4 — React Three Fiber: globe, routes, ports, cargo */}
      <motion.div
        className="absolute inset-0"
        animate={{ opacity: show3d ? 0.55 : reduceMotion ? 0.35 : 0.2 }}
        transition={{ duration: 0.8 }}
      >
        {reduceMotion ? (
          <HeroStaticFallback />
        ) : show3d ? (
          <ExportGlobeScene quality={quality} />
        ) : (
          <HeroStaticFallback />
        )}
      </motion.div>

      {/* Layer 5 — Canvas particles (AI / data network) */}
      <HeroParticleCanvas active={show3d} />

      {/* Layer 6 — cinematic overlays: vignette, blur, gradients */}
      <HeroAtmosphere />
    </motion.div>
  )
}
