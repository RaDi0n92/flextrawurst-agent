import { useState, useRef, useEffect } from 'react'

const navTabs = [
  { label: 'LEITSTAND', status: 'active' },
  { label: 'WAS IST DAS?', status: 'planned' },
  { label: 'RÄUME', status: 'planned' },
  { label: 'DISKURS', status: 'planned' },
  { label: 'WESEN', status: 'active' },
  { label: 'KOMPOASE', status: 'active' },
  { label: 'BLASEN', status: 'planned' },
  { label: 'MENSCHEN', status: 'active' },
  { label: 'SCHLAF', status: 'active' },
  { label: 'EINSICHT', status: 'planned' },
  { label: 'SUCHE', status: 'planned' },
  { label: 'ARCHÄOLOGIE', status: 'planned' },
  { label: 'CYBERLINGE', status: 'active' },
  { label: 'SPLITTER', status: 'active' },
  { label: 'ZITATE', status: 'active' },
  { label: 'SCHATTEN', status: 'planned' },
  { label: 'GRUPPEN', status: 'planned' },
  { label: 'SYSTEME', status: 'active' },
  { label: 'WISSEN', status: 'active' },
  { label: 'GESETZE', status: 'planned' },
  { label: 'FORSCHUNG', status: 'planned' },
  { label: 'PARTNER', status: 'planned' },
]

interface NavigationProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export default function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const [underlineStyle, setUnderlineStyle] = useState({ left: 0, width: 0 })
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map())
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = tabRefs.current.get(activeTab)
    if (el && scrollRef.current) {
      const scrollLeft = scrollRef.current.scrollLeft
      setUnderlineStyle({
        left: el.offsetLeft - scrollLeft,
        width: el.offsetWidth,
      })
    }
  }, [activeTab])

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0A0A0A]/85 backdrop-blur-md border-b border-[#222]">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 lg:px-6 h-10">
        <div className="flex items-center gap-3">
          <span className="font-sans font-extrabold text-sm tracking-wider text-[#F0F0F2]">
            FLEXTRAWURST
          </span>
          <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-mono text-[#8A8A93]">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse-dot" />
            Phase A — Im Aufbau
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2">
            <span className="status-dot bg-green-500" />
            <span className="text-[10px] font-mono text-[#8A8A93]">LIVE</span>
            <span className="w-1 h-1 rounded-full bg-[#FF8C42] opacity-60" />
            <span className="text-[10px] font-mono text-[#8A8A93]">GEPLANT</span>
          </div>
          <div className="flex items-center gap-1 text-[10px] font-mono text-[#8A8A93]">
            <button className="px-1.5 py-0.5 hover:text-[#FF1B8D] transition-colors">DE</button>
            <span>/</span>
            <button className="px-1.5 py-0.5 hover:text-[#FF1B8D] transition-colors">EN</button>
            <span>/</span>
            <button className="px-1.5 py-0.5 hover:text-[#FF1B8D] transition-colors">ES</button>
            <span>/</span>
            <button className="px-1.5 py-0.5 hover:text-[#FF1B8D] transition-colors">ZH</button>
          </div>
          <button className="text-[10px] font-mono px-3 py-1 border border-[#333] hover:border-[#FF1B8D] hover:text-[#FF1B8D] transition-all">
            LOGIN
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div
        ref={scrollRef}
        className="relative flex items-center gap-0 px-4 lg:px-6 overflow-x-auto scrollbar-hide h-9"
        style={{ scrollbarWidth: 'none' }}
      >
        {navTabs.map((tab) => (
          <button
            key={tab.label}
            ref={(el) => {
              if (el) tabRefs.current.set(tab.label, el)
            }}
            onClick={() => onTabChange(tab.label)}
            className={`relative flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-mono whitespace-nowrap transition-colors duration-200 ${
              activeTab === tab.label
                ? 'text-[#FF1B8D]'
                : 'text-[#8A8A93] hover:text-[#F0F0F2]'
            }`}
          >
            <span
              className={`w-1 h-1 rounded-full ${
                tab.status === 'active' ? 'bg-green-500' : 'bg-[#FF8C42] opacity-50'
              }`}
            />
            {tab.label}
          </button>
        ))}
        {/* Sliding underline */}
        <div
          className="absolute bottom-0 h-0.5 bg-[#FF1B8D] transition-all duration-400 ease-out"
          style={{
            left: underlineStyle.left,
            width: underlineStyle.width,
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </div>

      {/* Status ticker */}
      <div className="flex items-center gap-4 px-4 lg:px-6 h-6 bg-[#080808] border-t border-[#1a1a1a] overflow-hidden">
        <div className="flex items-center gap-3 text-[9px] font-mono text-[#8A8A93] animate-ticker-scroll whitespace-nowrap">
          {[...Array(2)].map((_, setIdx) => (
            <span key={setIdx} className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-green-500" />
                splitter-physik.service — aktiv
              </span>
              <span>·</span>
              <span className="flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-green-500" />
                Welt-API aktiv
              </span>
              <span>·</span>
              <span className="flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-green-500" />
                GENI Wahrnehmungsschicht aktiv
              </span>
              <span>·</span>
              <span>6 Wesen warten auf Einzug</span>
              <span>·</span>
              <span>7 Räume definiert</span>
              <span>·</span>
              <span className="flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-green-500" />
                Frontend aktiv
              </span>
              <span>·</span>
              <span>PostgreSQL flextrawurst — aktiv</span>
              <span>·</span>
            </span>
          ))}
        </div>
      </div>
    </nav>
  )
}
