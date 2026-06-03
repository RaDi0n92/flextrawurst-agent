import { useRef, useEffect, useState } from 'react'

interface System {
  name: string
  type: string
  status: 'LIVE' | 'GEPLANT'
  tech: string[]
  description: string
  accentColor: string
}

const systems: System[] = [
  {
    name: 'Welt-API',
    type: 'REST-API',
    status: 'LIVE',
    tech: ['Python 3.11', 'FastAPI', 'uvicorn', 'JWT', 'PostgreSQL'],
    description: 'Das Herz des Systems. Alle Daten fließen durch diese API — Räume, Wesen, Events, Resonanzen, Profile. REST-Endpunkte mit JWT-Auth. Jede Aktion schreibt ein Event — append-only.',
    accentColor: '#00D4FF',
  },
  {
    name: 'Frontend',
    type: 'Web',
    status: 'LIVE',
    tech: ['Node.js', 'TypeScript', 'HTML5', 'CSS3'],
    description: 'Das was du gerade siehst. Kein Framework — reines HTML, CSS, JavaScript. Wird aus TypeScript-Quellcode via build_surface.ts gebaut.',
    accentColor: '#FF1B8D',
  },
  {
    name: 'GENI',
    type: 'Wahrnehmung',
    status: 'LIVE',
    tech: ['Python', 'WebSocket', 'Event-Stream'],
    description: 'Das Nervensystem. Es hört auf Events, verarbeitet atmosphärische Signale und gibt Feedback — ohne direkte Kontrolle zu haben. Wie ein Organismus der spürt.',
    accentColor: '#FF8C42',
  },
  {
    name: 'Splitter-Physik',
    type: 'service',
    status: 'LIVE',
    tech: ['Python', 'systemd', '3 Ticks/min', 'PostgreSQL'],
    description: 'Alle 60 Sekunden tickt diese Engine. Verschmelzen, Explodieren, Veralten, Entstehen. Du siehst das Ergebnis live im KOMPOASE-Tab als schwebende Blasen.',
    accentColor: '#B8005C',
  },
  {
    name: 'PostgreSQL',
    type: 'Datenbank',
    status: 'LIVE',
    tech: ['PostgreSQL 15', 'JSONB', 'GIN-Index', 'append-only events'],
    description: 'Alle Daten der Welt leben hier. Events sind heilig — sie werden nur hinzugefügt, nie verändert oder gelöscht. JSONB-Felder erlauben flexible Erweiterungen.',
    accentColor: '#D4D4D8',
  },
  {
    name: 'Welt-Brücke',
    type: 'service',
    status: 'LIVE',
    tech: ['Python', 'systemd', 'Event-Bridge'],
    description: 'Brücke zwischen verschiedenen Systemschichten. Synchronisiert Weltzustand, leitet Events weiter, hält die Verbindung zwischen API, GENI und der Datenbank aufrecht.',
    accentColor: '#00D4FF',
  },
]

export default function SystemeSection() {
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
      id="systeme"
      ref={sectionRef}
      className="relative w-full py-24 lg:py-32"
      style={{ background: '#0A0A0A' }}
    >
      <div className="px-6 lg:px-16 xl:px-24">
        {/* Section header */}
        <div className="flex items-center gap-6 mb-16">
          <h2
            className="font-extrabold tracking-tight whitespace-nowrap"
            style={{
              fontSize: 'clamp(2.5rem, 5vw, 5rem)',
              color: '#F0F0F2',
              fontFamily: 'Inter, system-ui, sans-serif',
              lineHeight: 1,
            }}
          >
            SYSTEME
          </h2>
          <div
            className="flex-1 h-px"
            style={{ background: 'rgba(212, 212, 216, 0.2)' }}
          />
        </div>

        <p className="mb-12 text-sm max-w-2xl" style={{ color: '#8A8A93' }}>
          Alle Dienste die flextrawurst am Leben halten.{' '}
          <span className="text-green-400">Grüne Punkte</span> = läuft jetzt gerade auf diesem Server.
          Jede Karte erklärt was das System tut — auch wenn du kein Entwickler bist.
        </p>

        {/* System grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systems.map((sys, i) => (
            <div
              key={sys.name}
              className="relative group cursor-default"
              style={{
                opacity: visible ? 1 : 0,
                transform: visible ? 'translateY(0)' : 'translateY(60px)',
                transition: `all 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.12}s`,
              }}
            >
              {/* Top border */}
              <div
                className="absolute top-0 left-0 right-0 h-0.5"
                style={{
                  background: sys.accentColor,
                  transform: visible ? 'scaleX(1)' : 'scaleX(0)',
                  transformOrigin: 'left',
                  transition: `transform 0.6s ease ${i * 0.12 + 0.4}s`,
                }}
              />

              <div
                className="p-6 h-full transition-all duration-300 group-hover:-translate-y-1"
                style={{
                  background: '#141419',
                  border: '1px solid #222',
                }}
              >
                {/* Status + Type */}
                <div className="flex items-center justify-between mb-4">
                  <span
                    className="inline-flex items-center gap-1.5 px-2 py-1 text-[9px] font-mono font-semibold"
                    style={{
                      background: sys.status === 'LIVE'
                        ? 'rgba(0, 255, 100, 0.15)'
                        : 'rgba(255, 140, 66, 0.15)',
                      color: sys.status === 'LIVE' ? '#00ff64' : '#FF8C42',
                    }}
                  >
                    <span
                      className="w-1.5 h-1.5 rounded-full animate-pulse-dot"
                      style={{
                        background: sys.status === 'LIVE' ? '#00ff64' : '#FF8C42',
                      }}
                    />
                    {sys.status}
                  </span>
                  <span
                    className="text-[9px] font-mono"
                    style={{ color: '#8A8A93' }}
                  >
                    {sys.type}
                  </span>
                </div>

                {/* Name */}
                <h3
                  className="text-xl font-bold mb-3"
                  style={{
                    color: '#F0F0F2',
                    fontFamily: 'Inter, system-ui, sans-serif',
                  }}
                >
                  {sys.name}
                </h3>

                {/* Tech tags */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {sys.tech.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 text-[9px] font-mono"
                      style={{
                        background: '#0A0A0A',
                        color: '#8A8A93',
                        border: '1px solid #222',
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>

                {/* Description */}
                <p className="text-sm leading-relaxed" style={{ color: '#8A8A93' }}>
                  {sys.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
