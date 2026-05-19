'use client'

import { useRef, useMemo, Suspense, type RefObject } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, Line, Sparkles } from '@react-three/drei'
import * as THREE from 'three'
import type { Group, Mesh, Points } from 'three'
import {
  TRADE_HUBS,
  TRADE_ROUTES,
  GLOBE_RADIUS,
  latLonToVector3,
  createRouteArc,
} from '@/lib/geo-utils'

type Quality = 'high' | 'low'

function GlobeAssembly({ quality }: { quality: Quality }) {
  const groupRef = useRef<Group>(null)
  const planeRef = useRef<Mesh>(null)
  const containerRef = useRef<Mesh>(null)
  const hubRef = useRef<Mesh>(null)

  const segments = quality === 'high' ? 48 : 24

  const { hubPositions, routes, planeRoute, containerRoute } = useMemo(() => {
    const hubs = TRADE_HUBS.map((h) => latLonToVector3(h.lat, h.lon, GLOBE_RADIUS * 1.004))
    const routeList = TRADE_ROUTES.map(([a, b]) => ({
      points: createRouteArc(hubs[a], hubs[b], segments, 0.5),
      key: `${a}-${b}`,
    }))
    return {
      hubPositions: hubs,
      routes: routeList,
      planeRoute: createRouteArc(hubs[0], hubs[2], quality === 'high' ? 64 : 32, 0.65),
      containerRoute: createRouteArc(hubs[0], hubs[1], quality === 'high' ? 64 : 32, 0.45),
    }
  }, [segments, quality])

  const gridLines = useMemo(() => {
    const lines: THREE.Vector3[][] = []
    const r = GLOBE_RADIUS * 1.001
    for (let lat = -60; lat <= 60; lat += 30) {
      const pts: THREE.Vector3[] = []
      for (let lon = -180; lon <= 180; lon += 8) pts.push(latLonToVector3(lat, lon, r))
      lines.push(pts)
    }
    for (let lon = -180; lon < 180; lon += 45) {
      const pts: THREE.Vector3[] = []
      for (let lat = -80; lat <= 80; lat += 8) pts.push(latLonToVector3(lat, lon, r))
      lines.push(pts)
    }
    return lines
  }, [])

  useFrame((state, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.04

    const t = (state.clock.elapsedTime * 0.08) % 1
    const t2 = (state.clock.elapsedTime * 0.05 + 0.3) % 1

    const moveAlong = (ref: RefObject<Mesh | null>, route: THREE.Vector3[], progress: number, look = false) => {
      if (!ref.current || route.length < 2) return
      const idx = Math.floor(progress * (route.length - 1))
      const frac = (progress * (route.length - 1)) % 1
      const a = route[idx]
      const b = route[Math.min(idx + 1, route.length - 1)]
      ref.current.position.lerpVectors(a, b, frac)
      if (look) ref.current.lookAt(b)
    }

    moveAlong(planeRef, planeRoute, t, true)
    moveAlong(containerRef, containerRoute, t2)

    if (hubRef.current) {
      const pulse = 0.9 + Math.sin(state.clock.elapsedTime * 1.5) * 0.1
      hubRef.current.scale.setScalar(pulse)
    }
  })

  return (
    <group ref={groupRef}>
      <mesh>
        <sphereGeometry args={[GLOBE_RADIUS * 0.998, 64, 64]} />
        <meshStandardMaterial color="#0c0c14" transparent opacity={0.92} roughness={0.85} metalness={0.15} />
      </mesh>
      <mesh>
        <sphereGeometry args={[GLOBE_RADIUS, 48, 48]} />
        <meshBasicMaterial color="#6366f1" wireframe transparent opacity={0.07} />
      </mesh>

      {gridLines.map((pts, i) => (
        <Line key={`g-${i}`} points={pts} color="#818cf8" transparent opacity={0.06} lineWidth={0.5} />
      ))}

      {routes.map(({ points, key }) => (
        <Line key={key} points={points} color="#34d399" transparent opacity={0.16} lineWidth={0.8} />
      ))}

      {hubPositions.map((pos, i) => (
        <mesh key={i} ref={i === 0 ? hubRef : undefined} position={pos}>
          <sphereGeometry args={[i === 0 ? 0.045 : 0.028, 12, 12]} />
          <meshBasicMaterial color={i === 0 ? '#34d399' : '#818cf8'} transparent opacity={i === 0 ? 0.95 : 0.7} />
        </mesh>
      ))}

      <mesh ref={planeRef}>
        <coneGeometry args={[0.025, 0.07, 4]} />
        <meshBasicMaterial color="#a5b4fc" transparent opacity={0.85} />
      </mesh>
      <mesh ref={containerRef}>
        <boxGeometry args={[0.04, 0.025, 0.025]} />
        <meshBasicMaterial color="#34d399" transparent opacity={0.75} />
      </mesh>
    </group>
  )
}

function DataParticles({ count }: { count: number }) {
  const ref = useRef<Points>(null)

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const r = GLOBE_RADIUS + 0.5 + Math.random() * 2
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      pos[i * 3 + 2] = r * Math.cos(phi)
    }
    return pos
  }, [count])

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = state.clock.elapsedTime * 0.012
    }
  })

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.016} color="#818cf8" transparent opacity={0.32} sizeAttenuation depthWrite={false} />
    </points>
  )
}

function AICore() {
  return (
    <Float speed={1.2} rotationIntensity={0.15} floatIntensity={0.4}>
      <mesh>
        <icosahedronGeometry args={[0.35, 1]} />
        <meshStandardMaterial
          color="#6366f1"
          emissive="#4338ca"
          emissiveIntensity={0.6}
          wireframe
          transparent
          opacity={0.35}
        />
      </mesh>
    </Float>
  )
}

function Scene({ quality }: { quality: Quality }) {
  return (
    <>
      <ambientLight intensity={0.25} />
      <pointLight position={[6, 4, 6]} intensity={0.8} color="#818cf8" />
      <pointLight position={[-5, -3, 4]} intensity={0.4} color="#34d399" />
      <directionalLight position={[0, 8, 2]} intensity={0.3} color="#c7d2fe" />

      <GlobeAssembly quality={quality} />
      <DataParticles count={quality === 'high' ? 120 : 60} />
      <AICore />
      <Sparkles count={quality === 'high' ? 28 : 14} scale={7} size={1} speed={0.2} opacity={0.18} color="#818cf8" />
    </>
  )
}

export function ExportGlobeScene({ quality = 'high' }: { quality?: Quality }) {
  return (
    <Canvas
      camera={{ position: [0, 0.4, 6.8], fov: 42 }}
      dpr={[1, 1.35]}
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      style={{ background: 'transparent' }}
    >
      <Suspense fallback={null}>
        <Scene quality={quality} />
      </Suspense>
    </Canvas>
  )
}
