'use client'
import { useEffect, useState } from 'react'

export function ScoreCard({ score }: { score: number }) {
    const [mounted, setMounted] = useState(false)
    useEffect(() => setMounted(true), [])

    const color = score >= 75 ? 'stroke-success' : score >= 50 ? 'stroke-warning-500' : 'stroke-danger-600'
    const radius = 20
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (score / 100) * circumference

    return (
        <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 48 48">
                <circle cx="24" cy="24" r={radius} className="stroke-secondary dark:stroke-surface" strokeWidth="4" fill="none" />
                <circle
                    cx="24" cy="24" r={radius}
                    className={color}
                    strokeWidth="4"
                    fill="none"
                    strokeDasharray={circumference}
                    strokeDashoffset={mounted ? offset : circumference}
                    style={{ transition: 'stroke-dashoffset 600ms ease-out' }}
                />
            </svg>
            <span className="absolute text-[10px] font-bold text-text-primary">{score}</span>
        </div>
    )
}
