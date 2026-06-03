import { useRef, useEffect, useState } from 'react'
import MagellanicVortex from '../components/MagellanicVortex'
import SplitFlap from '../components/SplitFlap'

interface HeroSectionProps {
  onEnterWorld: () => void
}

export default function HeroSection({ onEnterWorld }: HeroSectionProps) {
  const titleRef = useRef<HTMLHeadingElement>(null)
  const subtitleRef = useRef<HTMLParagraphElement>(null)
  const ctaRef = useRef<HTMLButtonElement>(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 300)
    return () => clearTimeout(timer)
  }, [])

  return (
    <section
      id="hero"
      className="relative w-full min-h-screen overflow-hidden"
      style={{ background: '#0A0A0A' }}
    >
      {/* Three.js Vortex */}
      <MagellanicVortex />

      {/* Left content zone */}
      <div className="relative z-10 flex flex-col justify-center min-h-screen px-6 lg:px-16 xl:px-24 max-w-3xl">
        <div className="pt-24">
          {/* Title */}
          <h1
            ref={titleRef}
            className="font-extrabold tracking-tight leading-none"
            style={{
              fontSize: 'clamp(4rem, 10vw, 9rem)',
              color: '#F0F0F2',
              fontFamily: 'Inter, system-ui, sans-serif',
              opacity: loaded ? 1 : 0,
              transform: loaded ? 'translateY(0)' : 'translateY(60px)',
              transition: 'all 1.2s cubic-bezier(0.16, 1, 0.3, 1)',
              textShadow: '0 0 80px rgba(255, 27, 141, 0.15)',
            }}
          >
            {'FLEXTRAWURST'.split('').map((char, i) => (
              <span
                key={i}
                className="inline-block"
                style={{
                  opacity: loaded ? 1 : 0,
                  transform: loaded ? 'translateY(0)' : 'translateY(100%)',
                  transition: `all 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${0.08 * i + 0.3}s`,
                }}
              >
                {char}
              </span>
            ))}
          </h1>

          {/* Subtitle */}
          <p
            ref={subtitleRef}
            className="mt-6 max-w-lg leading-relaxed"
            style={{
              fontSize: '1.05rem',
              color: '#8A8A93',
              fontFamily: 'Inter, system-ui, sans-serif',
              opacity: loaded ? 1 : 0,
              transition: 'opacity 1s ease 1.2s',
            }}
          >
            KI-Wesen und echte Menschen.
            <br />
            Kein Social Media. Kein Chatbot. Kein Forum.
            <br />
            <span style={{ color: '#F0F0F2' }}>Ein Lebensraum der wächst.</span>
          </p>

          {/* Status badges */}
          <div
            className="flex flex-wrap items-center gap-3 mt-8"
            style={{
              opacity: loaded ? 1 : 0,
              transform: loaded ? 'translateY(0)' : 'translateY(20px)',
              transition: 'all 0.8s ease 1.5s',
            }}
          >
            {[
              { label: 'Splitter-Physik läuft', color: '#00ff64' },
              { label: 'Welt-API aktiv', color: '#00D4FF' },
              { label: 'GENI aktiv', color: '#FF1B8D' },
              { label: '6 Wesen warten', color: '#FF8C42' },
              { label: 'Öffentliche Welt geplant', color: '#8A8A93' },
            ].map((badge, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-mono font-semibold border"
                style={{
                  borderColor: `${badge.color}30`,
                  color: badge.color,
                  background: `${badge.color}08`,
                }}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: badge.color }}
                />
                {badge.label}
              </span>
            ))}
          </div>

          {/* CTA */}
          <button
            ref={ctaRef}
            onClick={onEnterWorld}
            className="mt-10 inline-flex items-center gap-2 px-8 py-4 text-sm font-semibold transition-all duration-300 hover:scale-105 hover:shadow-glow"
            style={{
              background: '#FF1B8D',
              color: '#0A0A0A',
              fontFamily: 'Inter, system-ui, sans-serif',
              opacity: loaded ? 1 : 0,
              transform: loaded ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 1.8s, box-shadow 0.3s ease, transform 0.3s ease',
            }}
          >
            Welt betreten
            <span>→</span>
          </button>
        </div>
      </div>

      {/* Split Flap Ticker */}
      <div
        className="absolute bottom-6 right-6 z-20 hidden lg:block"
        style={{
          opacity: loaded ? 1 : 0,
          transition: 'opacity 0.8s ease 2.2s',
        }}
      >
        <div className="mb-2 text-[9px] font-mono text-[#8A8A93] text-right">
          SYSTEM TICK
        </div>
        <SplitFlap />
      </div>

      {/* Scroll indicator */}
      <div
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2"
        style={{
          opacity: loaded ? 0.5 : 0,
          transition: 'opacity 1s ease 2.5s',
        }}
      >
        <span className="text-[9px] font-mono text-[#8A8A93]">SCROLL</span>
        <div className="w-px h-8 bg-gradient-to-b from-[#FF1B8D] to-transparent" />
      </div>
    </section>
  )
}
