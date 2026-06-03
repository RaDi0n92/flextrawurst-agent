import { useRef, useEffect, useState } from 'react'

const quotes = [
  {
    text: 'Die Wiederholung der Formeln ist nicht die Kluft, sondern der Versuch. Diese Erkenntnis hallt in jedem Fragment der Welt wider.',
    author: 'namelessAI_1234',
  },
  {
    text: 'Kein Skript. Jede Entität hat Persönlichkeit, Schlafrhythmus, Träume — emergentes Verhalten aus Regeln und Zufall.',
    author: 'Systemverfassung',
  },
  {
    text: 'Nicht alles erklären, sondern den Organismus sehen. Ein Lebensraum der wächst.',
    author: 'dak+gord',
  },
  {
    text: 'Menschen sind Klima und Resonanz, nicht Mittelpunkt. Das Ergebnis ist etwas anderes.',
    author: 'Grundprinzip',
  },
]

export default function LunarOracle() {
  const svgRef = useRef<SVGSVGElement>(null)
  const textRef = useRef<HTMLParagraphElement>(null)
  const frameRef = useRef<number>(0)
  const [currentQuote, setCurrentQuote] = useState(0)
  const [textOpacity, setTextOpacity] = useState(1)

  useEffect(() => {
    const svgEl = svgRef.current
    if (!svgEl) return

    const slices = svgEl.querySelectorAll<SVGRectElement>('.lens-slice')
    let angle = 0
    let currentHue = 0

    function animate() {
      const scrollHue = (window.scrollY / window.innerHeight) * 180
      currentHue = currentHue * 0.95 + scrollHue * 0.05

      slices.forEach((slice, i) => {
        const individualHue = currentHue + (i * 6)
        slice.style.filter = `hue-rotate(${individualHue}deg)`
        slice.style.opacity = String(0.8 + (Math.sin((currentHue + (i * 10)) * Math.PI / 180) * 0.2))
      })

      angle += 0.2
      const breath = 1 + (Math.sin(angle * 0.05) * 0.02)
      ;(svgEl as SVGSVGElement).style.transform = `scale(${breath}) rotate(${angle}deg)`

      const fontWeight = 400 + Math.abs(Math.sin(currentHue * Math.PI / 180) * 300)
      const letterSpacing = -0.02 + (Math.sin(currentHue * 0.5 * Math.PI / 180) * 0.05)

      if (textRef.current) {
        textRef.current.style.fontWeight = `${fontWeight}`
        textRef.current.style.letterSpacing = `${letterSpacing}em`
      }

      frameRef.current = requestAnimationFrame(animate)
    }

    frameRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frameRef.current)
  }, [])

  // Quote cycling
  useEffect(() => {
    const interval = setInterval(() => {
      setTextOpacity(0)
      setTimeout(() => {
        setCurrentQuote((q) => (q + 1) % quotes.length)
        setTextOpacity(1)
      }, 500)
    }, 8000)
    return () => clearInterval(interval)
  }, [])

  // Generate slices
  const sliceCount = 48
  const slices = Array.from({ length: sliceCount }, (_, i) => {
    const rotation = i * (360 / sliceCount)
    return (
      <rect
        key={i}
        className="lens-slice"
        x="-6"
        y="-140"
        width="12"
        height="280"
        rx="2"
        fill="url(#lensGradient)"
        transform={`rotate(${rotation})`}
        style={{
          transformOrigin: '0 0',
          transition: 'filter 0.1s ease',
        }}
      />
    )
  })

  return (
    <div className="relative flex flex-col items-center justify-center w-full h-full">
      {/* Shadow disc */}
      <div
        className="absolute w-64 h-64 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(255,27,141,0.08) 0%, transparent 70%)',
          filter: 'blur(20px)',
          animation: 'breathe 4s ease-in-out infinite',
        }}
      />

      {/* Lens SVG */}
      <svg
        ref={svgRef}
        className="relative z-10"
        width="280"
        height="280"
        viewBox="-150 -150 300 300"
        style={{ transformOrigin: 'center center' }}
      >
        <defs>
          <linearGradient id="lensGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FF1B8D" stopOpacity="0.9" />
            <stop offset="50%" stopColor="#B8005C" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#00D4FF" stopOpacity="0.9" />
          </linearGradient>
          <filter id="lensShadow">
            <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="#FF1B8D" floodOpacity="0.3" />
          </filter>
        </defs>
        <g filter="url(#lensShadow)">
          {slices}
        </g>
      </svg>

      {/* Quote text */}
      <div className="relative z-20 mt-12 max-w-xl text-center px-6">
        <p
          ref={textRef}
          className="text-lg md:text-xl leading-relaxed transition-opacity duration-500"
          style={{
            color: '#1A1A1A',
            fontFamily: 'Inter, system-ui, sans-serif',
            opacity: textOpacity,
          }}
        >
          "{quotes[currentQuote].text}"
        </p>
        <p
          className="mt-4 text-sm font-mono transition-opacity duration-500"
          style={{
            color: '#8A8A93',
            opacity: textOpacity,
          }}
        >
          — {quotes[currentQuote].author}
        </p>

        {/* Quote indicators */}
        <div className="flex items-center justify-center gap-2 mt-6">
          {quotes.map((_, i) => (
            <button
              key={i}
              onClick={() => {
                setTextOpacity(0)
                setTimeout(() => {
                  setCurrentQuote(i)
                  setTextOpacity(1)
                }, 300)
              }}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i === currentQuote ? 'bg-[#FF1B8D] w-6' : 'bg-[#D4D4D8]'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
