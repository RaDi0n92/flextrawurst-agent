import { useRef, useEffect, useState } from 'react'
import SplitterCanvas from '../components/SplitterCanvas'

export default function KompoaseSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.15 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section
      id="kompoase"
      ref={sectionRef}
      className="relative w-full min-h-screen overflow-hidden"
      style={{ background: '#050508' }}
    >
      {/* Splitter Canvas */}
      <div className="absolute inset-0 crt-overlay">
        <SplitterCanvas />
      </div>

      {/* UI Overlay Panel */}
      <div
        className="absolute bottom-8 left-8 z-10 max-w-sm"
        style={{
          background: 'rgba(10, 10, 10, 0.7)',
          backdropFilter: 'blur(12px)',
          padding: '1.5rem',
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(50px)',
          transition: 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.3s',
        }}
      >
        <span
          className="text-[10px] font-mono font-semibold tracking-widest"
          style={{ color: '#FF1B8D' }}
        >
          KOMPOASE
        </span>
        <div
          className="mt-2 font-extrabold"
          style={{
            fontSize: 'clamp(2rem, 4vw, 4rem)',
            color: '#F0F0F2',
            fontFamily: 'Inter, system-ui, sans-serif',
            lineHeight: 1.1,
          }}
        >
          48 Splitter
        </div>
        <p className="mt-3 text-sm leading-relaxed" style={{ color: '#8A8A93' }}>
          Gedankenfragmente aus dem Zwischenraum. Sie entstehen aus innerer Auseinandersetzung. 
          Energie steigt durch Interaktion. Zwei energiereiche Splitter können{' '}
          <span style={{ color: '#FF1B8D', fontWeight: 600 }}>verschmelzen</span> und neue 
          Entitäten gebären. Die Physik-Engine läuft alle 60 Sekunden.
        </p>
        <div className="flex items-center gap-3 mt-4">
          <button
            className="px-4 py-2 text-[10px] font-mono font-semibold border transition-all hover:border-[#FF1B8D] hover:text-[#FF1B8D]"
            style={{ borderColor: '#333', color: '#8A8A93' }}
          >
            GÄRRAUM ▲
          </button>
          <button
            className="px-4 py-2 text-[10px] font-mono font-semibold border transition-all hover:border-[#00D4FF] hover:text-[#00D4FF]"
            style={{ borderColor: '#333', color: '#8A8A93' }}
          >
            ARCHIV ▶
          </button>
        </div>
        <p className="mt-3 text-[10px] font-mono" style={{ color: '#555' }}>
          Klick auf Blase für Details · Hover lädt Energie auf
        </p>
      </div>

      {/* Right side label */}
      <div
        className="absolute top-1/2 right-8 z-10 -translate-y-1/2"
        style={{
          opacity: visible ? 1 : 0,
          transition: 'opacity 1s ease 0.6s',
        }}
      >
        <div
          className="text-[10px] font-mono tracking-widest vertical-text"
          style={{
            color: '#8A8A93',
            writingMode: 'vertical-rl',
            textOrientation: 'mixed',
          }}
        >
          SPLITTER-PHYSIK LIVE · 60s TAKT
        </div>
      </div>
    </section>
  )
}
