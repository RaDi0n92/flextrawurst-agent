import { useState, useEffect } from 'react'

function SplitFlapDigit({ target }: { target: string }) {
  const [current, setCurrent] = useState(target)
  const [prev, setPrev] = useState(target)
  const [flipping, setFlipping] = useState(false)

  useEffect(() => {
    if (target !== current) {
      setPrev(current)
      setFlipping(true)
      const randomChars = '0123456789ABCDEF'
      let steps = 0
      const maxSteps = 6
      const interval = setInterval(() => {
        steps++
        if (steps >= maxSteps) {
          clearInterval(interval)
          setCurrent(target)
          setTimeout(() => setFlipping(false), 350)
        } else {
          setCurrent(randomChars[Math.floor(Math.random() * randomChars.length)])
        }
      }, 50)
      return () => clearInterval(interval)
    }
  }, [target])

  return (
    <div className="split-flap">
      {/* Fixed top half showing previous */}
      <div className="face top" data-char={prev} />
      {/* Fixed bottom half showing current */}
      <div className="face bottom" data-char={current} />
      {/* Flipping overlays */}
      {flipping && (
        <>
          <div
            className="face top"
            data-char={current}
            style={{
              animation: 'flip-top 0.3s ease-in forwards',
              transformOrigin: '50% 100%',
            }}
          />
          <div
            className="face bottom"
            data-char={prev}
            style={{
              animation: 'flip-bottom 0.3s ease-out 0.15s forwards',
              transformOrigin: '50% 0%',
            }}
          />
        </>
      )}
    </div>
  )
}

export default function SplitFlap() {
  const [value, setValue] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setValue((v) => v + 1)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const digits = String(value).padStart(5, '0').split('')

  return (
    <div className="flex items-center gap-1">
      {digits.map((d, i) => (
        <SplitFlapDigit key={i} target={d} />
      ))}
    </div>
  )
}
