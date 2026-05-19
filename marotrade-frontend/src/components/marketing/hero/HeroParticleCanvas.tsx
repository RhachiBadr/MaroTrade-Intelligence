'use client'

import { useEffect, useRef } from 'react'
import { useReducedMotion } from 'framer-motion'

type Particle = {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  alpha: number
}

const HUB_DOTS = [
  { x: 0.48, y: 0.42 },
  { x: 0.52, y: 0.38 },
  { x: 0.72, y: 0.35 },
  { x: 0.28, y: 0.4 },
  { x: 0.62, y: 0.55 },
]

export function HeroParticleCanvas({ active = true }: { active?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    if (reduceMotion || !active) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let raf = 0
    let particles: Particle[] = []

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio, 2)
      const { width, height } = canvas.getBoundingClientRect()
      canvas.width = width * dpr
      canvas.height = height * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const count = width < 768 ? 35 : 65
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        size: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.35 + 0.15,
      }))
    }

    const draw = () => {
      const { width, height } = canvas.getBoundingClientRect()
      ctx.clearRect(0, 0, width, height)

      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0) p.x = width
        if (p.x > width) p.x = 0
        if (p.y < 0) p.y = height
        if (p.y > height) p.y = 0

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(129, 140, 248, ${p.alpha})`
        ctx.fill()
      }

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i]
          const b = particles[j]
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 100) {
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.strokeStyle = `rgba(52, 211, 153, ${0.06 * (1 - dist / 100)})`
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        }
      }

      for (const hub of HUB_DOTS) {
        const hx = hub.x * width
        const hy = hub.y * height
        const grad = ctx.createRadialGradient(hx, hy, 0, hx, hy, 24)
        grad.addColorStop(0, 'rgba(52, 211, 153, 0.15)')
        grad.addColorStop(1, 'transparent')
        ctx.fillStyle = grad
        ctx.beginPath()
        ctx.arc(hx, hy, 24, 0, Math.PI * 2)
        ctx.fill()

        ctx.beginPath()
        ctx.arc(hx, hy, 2, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(52, 211, 153, 0.5)'
        ctx.fill()
      }

      raf = requestAnimationFrame(draw)
    }

    resize()
    window.addEventListener('resize', resize)
    raf = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
    }
  }, [active, reduceMotion])

  if (reduceMotion) return null

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 h-full w-full opacity-50"
      aria-hidden
    />
  )
}
