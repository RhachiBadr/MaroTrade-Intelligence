'use client'

import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'framer-motion'

/** MP4 in /public/videos/ — add hero-export.webm for a smaller WebM variant */
const MP4_SRC = '/videos/hero-export.mp4'
const WEBM_SRC = '/videos/hero-export.webm'

export function HeroVideoLayer({ active = true }: { active?: boolean }) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [canPlay, setCanPlay] = useState(false)
  const [failed, setFailed] = useState(false)
  const [src, setSrc] = useState<string | null>(null)
  const reduceMotion = useReducedMotion()

  // Pick first available format (avoids 404 + error when .webm is missing)
  useEffect(() => {
    let cancelled = false

    async function resolveSource() {
      for (const url of [MP4_SRC, WEBM_SRC]) {
        try {
          const res = await fetch(url, { method: 'HEAD' })
          if (res.ok && !cancelled) {
            setSrc(url)
            return
          }
        } catch {
          /* ignore */
        }
      }
      if (!cancelled) setFailed(true)
    }

    resolveSource()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const video = videoRef.current
    if (!video || !src || failed) return

    const onCanPlay = () => setCanPlay(true)
    const onError = () => setFailed(true)

    video.addEventListener('canplay', onCanPlay)
    video.addEventListener('error', onError)
    video.src = src
    video.load()

    return () => {
      video.removeEventListener('canplay', onCanPlay)
      video.removeEventListener('error', onError)
    }
  }, [src, failed])

  useEffect(() => {
    const video = videoRef.current
    if (!video || !canPlay || reduceMotion) return

    if (active) {
      video.play().catch(() => {})
    } else {
      video.pause()
    }
  }, [active, canPlay, reduceMotion])

  if (reduceMotion || failed || !src) return null

  return (
    <>
      <video
        ref={videoRef}
        className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-1000 ${
          canPlay && active ? 'opacity-[0.18]' : 'opacity-0'
        }`}
        muted
        loop
        playsInline
        preload={active ? 'metadata' : 'none'}
        aria-hidden
      />
      {canPlay && <div className="absolute inset-0 bg-background/40 mix-blend-multiply" aria-hidden />}
    </>
  )
}
