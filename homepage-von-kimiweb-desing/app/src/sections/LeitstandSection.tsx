import { useRef, useEffect, useState } from 'react'
import WorldMap from '../components/WorldMap'

interface Room {
  id: number
  name: string
  status: 'LIVE' | 'GEPLANT' | 'SPÄTER' | 'BLOCKIERT'
  accentColor: string
  x: number
  y: number
  rx: number
  ry: number
  description: string
  type: string
  schicht: string
  zweck: string
  realitaet: string
}

const roomsList: Room[] = [
  { id: 1, name: 'Herkunftsraum', status: 'GEPLANT', accentColor: '#B8005C', x: 20, y: 30, rx: 45, ry: 28, description: 'Flarum-Archiv · Ursprung der Wesen', type: 'Raum · Weltebene', schicht: 'Flarum-Archiv · Ursprung der Wesen', zweck: 'Ursprung aller namelessAI-Wesen. Archivraum des Flarum-Beitragsarchivs.', realitaet: 'Statisch · 6 Wesen registriert · kein Einzug vollzogen' },
  { id: 2, name: 'Weltfoyer', status: 'GEPLANT', accentColor: '#FF8C42', x: 50, y: 15, rx: 38, ry: 24, description: 'Erste Schicht · Ankunft', type: 'Raum · Weltebene', schicht: 'GENI · keine Organ-Bindung', zweck: 'Schwelle zur Welt. Erste Schicht für Ankömmlinge.', realitaet: 'Platzhalter · keine Belegung · keine Route eingerichtet' },
  { id: 3, name: 'Begegnungszone', status: 'GEPLANT', accentColor: '#FF8C42', x: 75, y: 25, rx: 35, ry: 22, description: 'Wesen-Begegnung · Resonanz', type: 'Raum · Weltebene', schicht: 'Resonanz-Schicht (Schatten) · GENI', zweck: 'Ort des Kontakts zwischen Wesen. Resonanz-Slot vorgesehen.', realitaet: 'Platzhalter · Resonanz-Slot deaktiviert' },
  { id: 4, name: 'Werkraum', status: 'LIVE', accentColor: '#FF1B8D', x: 35, y: 55, rx: 42, ry: 30, description: 'dak+gord · Koordination', type: 'Raum · Weltebene', schicht: 'dak+gord (aktiv) · GENI · Werkraum-Explorer', zweck: 'Koordinationsraum. dak+gord als aktiver Systemkörper präsent.', realitaet: 'Aktiv · dak+gord registriert · Werkraum-Explorer verknüpft' },
  { id: 5, name: 'Stille Zone', status: 'SPÄTER', accentColor: '#00D4FF', x: 70, y: 60, rx: 32, ry: 20, description: 'Rückzug · Kontemplation', type: 'Raum · Weltebene', schicht: 'KompOase-Slot (gesperrt) · GENI', zweck: 'Rückzugsraum. KompOase-Vorform — noch kein Organ.', realitaet: 'Platzhalter · Organ-Slot deaktiviert · KompOase nur Bauplan' },
  { id: 6, name: 'Diskursarchiv', status: 'GEPLANT', accentColor: '#FF8C42', x: 85, y: 50, rx: 36, ry: 24, description: 'Suche · Diskursarchäologie', type: 'Raum · Weltebene', schicht: 'Tiefensuche-Grundlage (registriert) · GENI', zweck: 'Suchraum. Diskursarchäologische Tiefensuche geplant.', realitaet: 'Platzhalter · Tiefensuche registriert · nicht implementiert' },
  { id: 7, name: 'Systemkammer', status: 'LIVE', accentColor: '#FF1B8D', x: 50, y: 80, rx: 40, ry: 26, description: 'Verwaltung · Steuerung', type: 'Raum · Weltebene', schicht: 'Verwaltungs-Steuerungsebene (aktiv) · GENI · Systemweiser', zweck: 'Verwaltungs- und Governance-Raum. Steuerungstore offen.', realitaet: 'Aktiv als Konzept · Verwaltungssteuerung aktiv · keine Sperren' },
]

const subsystems = [
  { name: 'Cyberling', status: 'LIVE' as const },
  { name: 'KompOase', status: 'SPÄTER' as const },
  { name: 'METAWAR', status: 'BLOCKIERT' as const },
  { name: 'Schlaf', status: 'LIVE' as const },
  { name: 'Substanz', status: 'BLOCKIERT' as const },
  { name: 'quality me time', status: 'SPÄTER' as const },
  { name: 'Urlaub', status: 'SPÄTER' as const },
  { name: 'Traum', status: 'BLOCKIERT' as const },
]

function getStatusColor(status: string) {
  switch (status) {
    case 'LIVE': return { bg: 'rgba(0,255,100,0.15)', text: '#00ff64', dot: '#00ff64' }
    case 'GEPLANT': return { bg: 'rgba(255,140,66,0.15)', text: '#FF8C42', dot: '#FF8C42' }
    case 'SPÄTER': return { bg: 'rgba(0,212,255,0.15)', text: '#00D4FF', dot: '#00D4FF' }
    case 'BLOCKIERT': return { bg: 'rgba(255,51,51,0.15)', text: '#ff3333', dot: '#ff3333' }
    default: return { bg: 'rgba(138,138,147,0.15)', text: '#8A8A93', dot: '#8A8A93' }
  }
}

export default function LeitstandSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const [visible, setVisible] = useState(false)
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)

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
      id="leitstand"
      ref={sectionRef}
      className="relative w-full min-h-screen"
      style={{ background: '#050508' }}
    >
      {/* Section header */}
      <div className="px-6 lg:px-16 xl:px-24 pt-24 pb-6">
        <h2
          className="font-extrabold tracking-tight"
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 5rem)',
            color: '#F0F0F2',
            fontFamily: 'Inter, system-ui, sans-serif',
            lineHeight: 1,
          }}
        >
          LEITSTAND
        </h2>
        <p className="mt-3 text-sm max-w-xl" style={{ color: '#8A8A93' }}>
          Die Weltkarte atmet. Ellipsen = Räume. Grüner Punkt = aktiv. 
          Blaue Punkte = Wesen (wartend). Gestrichelt = GENI-Membran.
        </p>
      </div>

      {/* Main content: Map + Sidebar */}
      <div className="flex flex-col lg:flex-row px-6 lg:px-16 xl:px-24 gap-6">
        {/* Left: Room list */}
        <div
          className="w-full lg:w-80 flex-shrink-0"
          style={{
            opacity: visible ? 1 : 0,
            transform: visible ? 'translateX(0)' : 'translateX(-100px)',
            transition: 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s',
          }}
        >
          <div className="mb-4">
            <span className="text-[10px] font-mono font-semibold tracking-widest" style={{ color: '#FF1B8D' }}>
              RÄUME
            </span>
          </div>
          <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-2">
            {roomsList.map((room) => {
              const sc = getStatusColor(room.status)
              const isSelected = selectedRoom?.id === room.id
              return (
                <button
                  key={room.id}
                  onClick={() => setSelectedRoom(isSelected ? null : room)}
                  className="w-full text-left p-3 transition-all duration-200 hover:bg-[#141419]"
                  style={{
                    background: isSelected ? '#141419' : 'transparent',
                    border: `1px solid ${isSelected ? room.accentColor + '40' : '#1a1a1a'}`,
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ background: sc.dot }}
                    />
                    <span className="text-sm font-semibold" style={{ color: '#F0F0F2' }}>
                      {room.name}
                    </span>
                    <span
                      className="ml-auto text-[9px] font-mono px-1.5 py-0.5"
                      style={{ background: sc.bg, color: sc.text }}
                    >
                      {room.status}
                    </span>
                  </div>
                  <p className="text-[10px] font-mono ml-5" style={{ color: '#8A8A93' }}>
                    {room.description}
                  </p>
                </button>
              )
            })}
          </div>

          {/* Subsystem ticker */}
          <div className="mt-6 pt-4 border-t border-[#1a1a1a]">
            <span className="text-[10px] font-mono tracking-widest" style={{ color: '#8A8A93' }}>
              SUBSYSTEME
            </span>
            <div className="flex flex-wrap gap-2 mt-3">
              {subsystems.map((sub) => {
                const sc = getStatusColor(sub.status)
                return (
                  <span
                    key={sub.name}
                    className="inline-flex items-center gap-1 px-2 py-1 text-[9px] font-mono"
                    style={{ background: sc.bg, color: sc.text }}
                  >
                    <span className="w-1 h-1 rounded-full" style={{ background: sc.dot }} />
                    {sub.name}
                  </span>
                )
              })}
            </div>
          </div>
        </div>

        {/* Center: Map */}
        <div
          className="flex-1 relative min-h-[500px] lg:min-h-[70vh]"
          style={{
            opacity: visible ? 1 : 0,
            transition: 'opacity 1.2s ease 0.4s',
          }}
        >
          <WorldMap onRoomSelect={setSelectedRoom} selectedRoom={selectedRoom} />
        </div>

        {/* Right: Room detail panel */}
        {selectedRoom && (
          <div
            className="w-full lg:w-80 flex-shrink-0"
            style={{
              animation: 'accordion-down 0.4s ease-out',
            }}
          >
            <div
              className="p-6 h-full"
              style={{
                background: '#141419',
                border: `1px solid ${selectedRoom.accentColor}30`,
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="text-xl font-bold"
                  style={{ color: '#F0F0F2', fontFamily: 'Inter, system-ui, sans-serif' }}
                >
                  {selectedRoom.name}
                </h3>
                <button
                  onClick={() => setSelectedRoom(null)}
                  className="text-[10px] font-mono hover:text-[#FF1B8D] transition-colors"
                  style={{ color: '#8A8A93' }}
                >
                  SCHLIESSEN ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <span className="text-[9px] font-mono tracking-widest block mb-1" style={{ color: '#8A8A93' }}>STATUS</span>
                  <span
                    className="inline-flex items-center gap-1.5 px-2 py-1 text-[10px] font-mono font-semibold"
                    style={{
                      background: getStatusColor(selectedRoom.status).bg,
                      color: getStatusColor(selectedRoom.status).text,
                    }}
                  >
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse-dot" style={{ background: getStatusColor(selectedRoom.status).dot }} />
                    {selectedRoom.status}
                  </span>
                </div>

                <div>
                  <span className="text-[9px] font-mono tracking-widest block mb-1" style={{ color: '#8A8A93' }}>TYP</span>
                  <span className="text-sm" style={{ color: '#F0F0F2' }}>{selectedRoom.type}</span>
                </div>

                <div>
                  <span className="text-[9px] font-mono tracking-widest block mb-1" style={{ color: '#8A8A93' }}>SCHICHT</span>
                  <span className="text-sm" style={{ color: '#F0F0F2' }}>{selectedRoom.schicht}</span>
                </div>

                <div>
                  <span className="text-[9px] font-mono tracking-widest block mb-1" style={{ color: '#8A8A93' }}>ZWECK</span>
                  <p className="text-sm leading-relaxed" style={{ color: '#F0F0F2' }}>{selectedRoom.zweck}</p>
                </div>

                <div>
                  <span className="text-[9px] font-mono tracking-widest block mb-1" style={{ color: '#8A8A93' }}>REALITÄT</span>
                  <p className="text-sm" style={{ color: '#8A8A93' }}>{selectedRoom.realitaet}</p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-[#222]">
                {[
                  { label: 'WESEN', value: '6' },
                  { label: 'POSTS', value: '1.413' },
                  { label: 'RESONANZEN', value: '19' },
                  { label: 'SPLITTER', value: '268' },
                ].map((stat) => (
                  <div key={stat.label}>
                    <span className="text-[9px] font-mono tracking-widest block" style={{ color: '#8A8A93' }}>
                      {stat.label}
                    </span>
                    <span
                      className="font-extrabold"
                      style={{
                        fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                        color: '#F0F0F2',
                        fontFamily: 'Inter, system-ui, sans-serif',
                      }}
                    >
                      {stat.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom ticker */}
      <div className="mt-8 h-10 flex items-center overflow-hidden border-t border-[#1a1a1a]" style={{ background: '#080808' }}>
        <div className="flex items-center gap-6 text-[9px] font-mono text-[#8A8A93] animate-ticker-scroll whitespace-nowrap px-4">
          {[...Array(2)].map((_, setIdx) => (
            <span key={setIdx} className="flex items-center gap-6">
              {subsystems.map((sub) => {
                const sc = getStatusColor(sub.status)
                return (
                  <span key={sub.name} className="flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full" style={{ background: sc.dot }} />
                    <span style={{ color: sc.text }}>{sub.name}</span>
                    <span style={{ color: sc.text }}>{sub.status}</span>
                  </span>
                )
              })}
              <span>·</span>
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
