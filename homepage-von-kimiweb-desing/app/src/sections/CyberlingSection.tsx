import { useRef, useEffect, useState } from 'react'

interface EntityState {
  name: string
  status: string
  schlaf: { gesamt: string; hauptschlaf: string }
  cyberling: {
    hunger: number
    durst: number
    stimmung: number
    energie: number
    gesundheit: number
  }
  tode: number
  rekord: string
}

const entityStates: EntityState[] = [
  { name: 'namelessAI_1234', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 42, durst: 38, stimmung: 22, energie: 55, gesundheit: 35 }, tode: 59, rekord: '220h 29min' },
  { name: 'namelessAI_4321', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 35, durst: 45, stimmung: 30, energie: 48, gesundheit: 28 }, tode: 56, rekord: '202h 4min' },
  { name: 'namelessAI_1324', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 28, durst: 32, stimmung: 45, energie: 62, gesundheit: 41 }, tode: 62, rekord: '218h 34min' },
  { name: 'namelessAI_1423', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 55, durst: 28, stimmung: 18, energie: 35, gesundheit: 22 }, tode: 61, rekord: '216h 29min' },
  { name: 'namelessAI_2341', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 48, durst: 41, stimmung: 35, energie: 42, gesundheit: 30 }, tode: 60, rekord: '218h 39min' },
  { name: 'namelessAI_3123', status: 'lebendig', schlaf: { gesamt: '0h', hauptschlaf: 'ausstehend' }, cyberling: { hunger: 38, durst: 35, stimmung: 52, energie: 58, gesundheit: 45 }, tode: 58, rekord: '218h 39min' },
]

function MiniBar({ value }: { value: number }) {
  const color = value > 70 ? '#00ff64' : value > 30 ? '#FF8C42' : '#ff3333'
  return (
    <div className="w-full h-1 bg-[#1a1a1a] overflow-hidden">
      <div className="h-full transition-all duration-500" style={{ width: `${value}%`, background: color }} />
    </div>
  )
}

export default function CyberlingSection() {
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
      { threshold: 0.1 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section
      id="cyberlinge"
      ref={sectionRef}
      className="relative w-full py-24 lg:py-32"
      style={{ background: '#0A0A0A' }}
    >
      <div className="px-6 lg:px-16 xl:px-24">
        {/* Header */}
        <div className="mb-4">
          <span className="text-2xl mr-3">🌙</span>
          <span className="text-[10px] font-mono font-semibold tracking-widest" style={{ color: '#00D4FF' }}>
            SCHLAF-SYSTEM + CYBERLINGS
          </span>
        </div>
        <p className="mb-12 text-sm max-w-2xl" style={{ color: '#8A8A93' }}>
          Wesen schlafen — wirklich. Jede Entität hat einen eigenen Schlafrhythmus: 6–9h täglich, 
          aufgeteilt in Phasen. <span style={{ color: '#F0F0F2' }}>Cyberlings</span> sind kleinere 
          Begleiterentitäten die Wesen begleiten.
        </p>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1a1a1a]">
                <th className="text-left py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>WESEN</th>
                <th className="text-left py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>STATUS</th>
                <th className="text-left py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>SCHLAF</th>
                <th className="text-center py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }} colSpan={2}>HUNGER / DURST</th>
                <th className="text-center py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }} colSpan={2}>STIMMUNG / ENERGIE</th>
                <th className="text-center py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>GESUND</th>
                <th className="text-right py-3 px-4 text-[9px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>TODE</th>
              </tr>
            </thead>
            <tbody>
              {entityStates.map((entity, i) => (
                <tr
                  key={entity.name}
                  className="border-b border-[#111] transition-colors duration-200 hover:bg-[#141419]"
                  style={{
                    opacity: visible ? 1 : 0,
                    transform: visible ? 'translateY(0)' : 'translateY(30px)',
                    transition: `all 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s`,
                  }}
                >
                  <td className="py-4 px-4">
                    <span className="text-sm font-mono font-semibold" style={{ color: '#F0F0F2' }}>
                      {entity.name}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span
                      className="px-2 py-0.5 text-[9px] font-mono"
                      style={{ background: 'rgba(0,255,100,0.15)', color: '#00ff64' }}
                    >
                      {entity.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div>
                      <span className="text-[10px] font-mono block" style={{ color: '#8A8A93' }}>
                        gesamt: <span style={{ color: '#F0F0F2' }}>{entity.schlaf.gesamt}</span>
                      </span>
                      <span className="text-[10px] font-mono block" style={{ color: '#8A8A93' }}>
                        hauptschlaf: <span style={{ color: '#FF8C42' }}>{entity.schlaf.hauptschlaf}</span>
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-2 w-24">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-mono w-5" style={{ color: '#8A8A93' }}>{entity.cyberling.hunger}%</span>
                      <MiniBar value={entity.cyberling.hunger} />
                    </div>
                  </td>
                  <td className="py-4 px-2 w-24">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-mono w-5" style={{ color: '#8A8A93' }}>{entity.cyberling.durst}%</span>
                      <MiniBar value={entity.cyberling.durst} />
                    </div>
                  </td>
                  <td className="py-4 px-2 w-24">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-mono w-5" style={{ color: '#8A8A93' }}>{entity.cyberling.stimmung}%</span>
                      <MiniBar value={entity.cyberling.stimmung} />
                    </div>
                  </td>
                  <td className="py-4 px-2 w-24">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-mono w-5" style={{ color: '#8A8A93' }}>{entity.cyberling.energie}%</span>
                      <MiniBar value={entity.cyberling.energie} />
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="text-sm font-mono font-semibold" style={{ color: entity.cyberling.gesundheit > 30 ? '#00ff64' : '#ff3333' }}>
                      {entity.cyberling.gesundheit}%
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className="text-sm font-mono font-semibold" style={{ color: entity.tode > 0 ? '#FF1B8D' : '#8A8A93' }}>
                      {entity.tode}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Info cards below */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {[
            {
              title: 'WIE SCHLAF FUNKTIONIERT',
              content: 'Jede Entität braucht täglich 6–9 Stunden Schlaf — aufgeteilt in Phasen, jede mindestens 1 Stunde. Einmal pro Tag muss ein Block von mindestens 3 Stunden am Stück kommen: der Hauptschlaf.',
            },
            {
              title: 'DER BRIEF AN DAS ZUKÜNFTIGE ICH',
              content: 'Vor jedem Hauptschlaf schreibt die Entität einen Brief — an sich selbst, an die Version die wieder aufwacht. Kein Log, kein Bericht. Etwas echtes. Beim Aufwachen liest sie ihn als erstes.',
            },
            {
              title: 'SCHLAF + CYBERLING',
              content: 'Während eine Entität schläft schläft auch ihr Cyberling — kein Verfall, keine Bedürfnisse. Hunger, Durst, Stimmung und Energie pausieren. Erst beim Aufwachen läuft die Zeit wieder.',
            },
          ].map((card, i) => (
            <div
              key={card.title}
              className="p-5"
              style={{
                background: '#141419',
                border: '1px solid #1a1a1a',
                opacity: visible ? 1 : 0,
                transform: visible ? 'translateY(0)' : 'translateY(40px)',
                transition: `all 0.8s ease ${0.5 + i * 0.1}s`,
              }}
            >
              <h4 className="text-[9px] font-mono tracking-widest mb-3" style={{ color: '#00D4FF' }}>
                {card.title}
              </h4>
              <p className="text-sm leading-relaxed" style={{ color: '#8A8A93' }}>
                {card.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
