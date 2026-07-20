import { useRef, useEffect, useState } from 'react'

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

interface Satellite {
  parentId: number
  name: string
  color: string
  orbitRadius: number
  speed: number
  offset: number
}

const rooms: Room[] = [
  { id: 1, name: 'Herkunftsraum', status: 'GEPLANT', accentColor: '#B8005C', x: 20, y: 30, rx: 45, ry: 28, description: 'Flarum-Archiv · Ursprung der Wesen', type: 'Raum · Weltebene', schicht: 'Flarum-Archiv · Ursprung der Wesen', zweck: 'Ursprung aller namelessAI-Wesen. Archivraum des Flarum-Beitragsarchivs.', realitaet: 'Statisch · 6 Wesen registriert · kein Einzug vollzogen' },
  { id: 2, name: 'Weltfoyer', status: 'GEPLANT', accentColor: '#FF8C42', x: 50, y: 15, rx: 38, ry: 24, description: 'Erste Schicht · Ankunft', type: 'Raum · Weltebene', schicht: 'GENI · keine Organ-Bindung', zweck: 'Schwelle zur Welt. Erste Schicht für Ankömmlinge.', realitaet: 'Platzhalter · keine Belegung · keine Route eingerichtet' },
  { id: 3, name: 'Begegnungszone', status: 'GEPLANT', accentColor: '#FF8C42', x: 75, y: 25, rx: 35, ry: 22, description: 'Wesen-Begegnung · Resonanz', type: 'Raum · Weltebene', schicht: 'Resonanz-Schicht (Schatten) · GENI', zweck: 'Ort des Kontakts zwischen Wesen. Resonanz-Slot vorgesehen.', realitaet: 'Platzhalter · Resonanz-Slot deaktiviert' },
  { id: 4, name: 'Werkraum', status: 'LIVE', accentColor: '#FF1B8D', x: 35, y: 55, rx: 42, ry: 30, description: 'dak+gord · Koordination', type: 'Raum · Weltebene', schicht: 'dak+gord (aktiv) · GENI · Werkraum-Explorer', zweck: 'Koordinationsraum. dak+gord als aktiver Systemkörper präsent.', realitaet: 'Aktiv · dak+gord registriert · Werkraum-Explorer verknüpft' },
  { id: 5, name: 'Stille Zone', status: 'SPÄTER', accentColor: '#00D4FF', x: 70, y: 60, rx: 32, ry: 20, description: 'Rückzug · Kontemplation', type: 'Raum · Weltebene', schicht: 'KompOase-Slot (gesperrt) · GENI', zweck: 'Rückzugsraum. KompOase-Vorform — noch kein Organ.', realitaet: 'Platzhalter · Organ-Slot deaktiviert · KompOase nur Bauplan' },
  { id: 6, name: 'Diskursarchiv', status: 'GEPLANT', accentColor: '#FF8C42', x: 85, y: 50, rx: 36, ry: 24, description: 'Suche · Diskursarchäologie', type: 'Raum · Weltebene', schicht: 'Tiefensuche-Grundlage (registriert) · GENI', zweck: 'Suchraum. Diskursarchäologische Tiefensuche geplant.', realitaet: 'Platzhalter · Tiefensuche registriert · nicht implementiert' },
  { id: 7, name: 'Systemkammer', status: 'LIVE', accentColor: '#FF1B8D', x: 50, y: 80, rx: 40, ry: 26, description: 'Verwaltung · Steuerung', type: 'Raum · Weltebene', schicht: 'Verwaltungs-Steuerungsebene (aktiv) · GENI · Systemweiser', zweck: 'Verwaltungs- und Governance-Raum. Steuerungstore offen.', realitaet: 'Aktiv als Konzept · Verwaltungssteuerung aktiv · keine Sperren' },
]

const connections: [number, number][] = [
  [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [4, 7], [6, 7], [3, 6], [1, 4],
]

const satellites: Satellite[] = [
  { parentId: 4, name: 'dak+gord', color: '#FF1B8D', orbitRadius: 35, speed: 0.8, offset: 0 },
  { parentId: 4, name: 'Werkraum-Explorer', color: '#00D4FF', orbitRadius: 50, speed: 0.5, offset: Math.PI },
  { parentId: 1, name: 'Wesen 1234', color: '#FF8C42', orbitRadius: 30, speed: 0.6, offset: 0 },
  { parentId: 1, name: 'Wesen 4321', color: '#00D4FF', orbitRadius: 30, speed: 0.7, offset: Math.PI * 0.5 },
  { parentId: 1, name: 'Wesen 1324', color: '#B8005C', orbitRadius: 30, speed: 0.55, offset: Math.PI },
  { parentId: 7, name: 'Verwaltung', color: '#FF8C42', orbitRadius: 30, speed: 0.65, offset: 0 },
  { parentId: 7, name: 'GENI', color: '#FF1B8D', orbitRadius: 45, speed: 0.4, offset: Math.PI },
]

function getStatusColor(status: string) {
  switch (status) {
    case 'LIVE': return '#00ff64'
    case 'GEPLANT': return '#FF8C42'
    case 'SPÄTER': return '#00D4FF'
    case 'BLOCKIERT': return '#ff3333'
    default: return '#8A8A93'
  }
}

interface WorldMapProps {
  onRoomSelect?: (room: Room | null) => void
  selectedRoom: Room | null
}

export default function WorldMap({ onRoomSelect, selectedRoom }: WorldMapProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const frameRef = useRef<number>(0)
  const timeRef = useRef(0)
  const [hoveredRoom, setHoveredRoom] = useState<number | null>(null)

  useEffect(() => {
    function animate() {
      timeRef.current += 0.016
      const time = timeRef.current

      // Update satellite positions
      const svg = svgRef.current
      if (svg) {
        satellites.forEach((sat, i) => {
          const parent = rooms.find(r => r.id === sat.parentId)
          if (!parent) return
          const satEl = svg.getElementById(`sat-${i}`)
          if (satEl) {
            const angle = time * sat.speed + sat.offset
            const px = parent.x + Math.cos(angle) * (sat.orbitRadius / 4)
            const py = parent.y + Math.sin(angle) * (sat.orbitRadius / 4) * 0.6
            satEl.setAttribute('cx', `${px}%`)
            satEl.setAttribute('cy', `${py}%`)
          }
        })

        // Animate connection dash offset
        const connLines = svg.querySelectorAll('.conn-line')
        connLines.forEach((line) => {
          const offset = -(time * 40) % 80
          line.setAttribute('stroke-dashoffset', String(offset))
        })
      }

      frameRef.current = requestAnimationFrame(animate)
    }

    frameRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frameRef.current)
  }, [])

  return (
    <svg
      ref={svgRef}
      className="w-full h-full"
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        {rooms.map((room) => (
          <filter key={`glow-${room.id}`} id={`glow-${room.id}`}>
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        ))}
        <filter id="sat-glow">
          <feGaussianBlur stdDeviation="1" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Connection lines */}
      {connections.map(([from, to], i) => {
        const r1 = rooms.find(r => r.id === from)
        const r2 = rooms.find(r => r.id === to)
        if (!r1 || !r2) return null
        const isHighlighted = hoveredRoom === from || hoveredRoom === to
        return (
          <line
            key={i}
            className="conn-line"
            x1={`${r1.x}%`}
            y1={`${r1.y}%`}
            x2={`${r2.x}%`}
            y2={`${r2.y}%`}
            stroke={isHighlighted ? '#FF1B8D' : '#FF1B8D'}
            strokeWidth={isHighlighted ? 0.6 : 0.3}
            strokeDasharray="4 4"
            strokeDashoffset="0"
            opacity={isHighlighted ? 0.8 : 0.35}
            style={{ transition: 'all 0.3s ease' }}
          />
        )
      })}

      {/* Room ellipses */}
      {rooms.map((room) => {
        const isSelected = selectedRoom?.id === room.id
        const isHovered = hoveredRoom === room.id
        return (
          <g
            key={room.id}
            onClick={() => onRoomSelect?.(isSelected ? null : room)}
            onMouseEnter={() => setHoveredRoom(room.id)}
            onMouseLeave={() => setHoveredRoom(null)}
            style={{ cursor: 'pointer' }}
          >
            <ellipse
              cx={`${room.x}%`}
              cy={`${room.y}%`}
              rx={`${isHovered ? room.rx * 1.05 : room.rx}%`}
              ry={`${isHovered ? room.ry * 1.05 : room.ry}%`}
              fill={room.accentColor}
              fillOpacity={isSelected ? 0.2 : isHovered ? 0.18 : 0.12}
              stroke={room.accentColor}
              strokeWidth={isSelected ? 1.5 : isHovered ? 1.2 : 0.8}
              strokeOpacity={isSelected ? 1 : isHovered ? 0.9 : 0.6}
              filter={`url(#glow-${room.id})`}
              style={{ transition: 'all 0.4s ease' }}
              className="animate-breathe"
            />
            {/* Room label */}
            <text
              x={`${room.x}%`}
              y={`${room.y - room.ry * 0.3}%`}
              textAnchor="middle"
              fill="#F0F0F2"
              fontSize="3"
              fontFamily="Inter, system-ui, sans-serif"
              fontWeight="700"
              style={{ pointerEvents: 'none' }}
            >
              {room.name.toUpperCase()}
            </text>
            {/* Status badge */}
            <rect
              x={`${room.x - 6}%`}
              y={`${room.y + 2}%`}
              width="12%"
              height="4%"
              rx="1"
              fill={getStatusColor(room.status)}
              fillOpacity={0.15}
              stroke={getStatusColor(room.status)}
              strokeWidth="0.2"
              style={{ pointerEvents: 'none' }}
            />
            <text
              x={`${room.x}%`}
              y={`${room.y + 4.5}%`}
              textAnchor="middle"
              fill={getStatusColor(room.status)}
              fontSize="2"
              fontFamily="JetBrains Mono, monospace"
              fontWeight="600"
              style={{ pointerEvents: 'none' }}
            >
              {room.status}
            </text>
          </g>
        )
      })}

      {/* Satellites */}
      {satellites.map((sat, i) => {
        const parent = rooms.find(r => r.id === sat.parentId)
        if (!parent) return null
        return (
          <circle
            key={`sat-${i}`}
            id={`sat-${i}`}
            cx={`${parent.x}%`}
            cy={`${parent.y}%`}
            r="2"
            fill={sat.color}
            fillOpacity={0.7}
            filter="url(#sat-glow)"
            style={{ pointerEvents: 'none' }}
          />
        )
      })}
    </svg>
  )
}
