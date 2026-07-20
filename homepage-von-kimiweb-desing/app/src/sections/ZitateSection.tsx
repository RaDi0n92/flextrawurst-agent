import { useRef, useEffect, useState } from 'react'
import LunarOracle from '../components/LunarOracle'

export default function ZitateSection() {
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
      { threshold: 0.2 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section
      id="zitate"
      ref={sectionRef}
      className="relative w-full min-h-screen flex items-center justify-center overflow-hidden"
      style={{
        background: '#E8E8E4',
        opacity: visible ? 1 : 0,
        clipPath: visible ? 'inset(0 0 0 0)' : 'inset(0 100% 0 0)',
        transition: 'clip-path 1s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.6s ease',
      }}
    >
      <LunarOracle />
    </section>
  )
}
