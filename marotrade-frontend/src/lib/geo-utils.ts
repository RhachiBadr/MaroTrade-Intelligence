import * as THREE from 'three'

export type GeoPoint = { lat: number; lon: number; label: string }

/** Convert WGS84 lat/lon to a point on a sphere (Y-up). */
export function latLonToVector3(lat: number, lon: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  )
}

/** Elevated arc between two surface points — mimics shipping / flight routes. */
export function createRouteArc(
  start: THREE.Vector3,
  end: THREE.Vector3,
  segments: number,
  lift = 0.55
): THREE.Vector3[] {
  const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5)
  const dist = start.distanceTo(end)
  mid.normalize().multiplyScalar(start.length() + lift * (dist / 4))

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
  return curve.getPoints(segments)
}

/** Key export hubs — Morocco-centric trade network. */
export const TRADE_HUBS: GeoPoint[] = [
  { lat: 33.57, lon: -7.59, label: 'Casablanca' },
  { lat: 48.86, lon: 2.35, label: 'Paris' },
  { lat: 40.71, lon: -74.01, label: 'New York' },
  { lat: 40.42, lon: -3.7, label: 'Madrid' },
  { lat: 51.92, lon: 4.48, label: 'Rotterdam' },
  { lat: 25.2, lon: 55.27, label: 'Dubai' },
  { lat: 35.68, lon: 139.69, label: 'Tokyo' },
]

/** Routes emanating from Casablanca to major markets. */
export const TRADE_ROUTES: [number, number][] = [
  [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6],
  [1, 4], [2, 6], [3, 4],
]

export const GLOBE_RADIUS = 2.35
