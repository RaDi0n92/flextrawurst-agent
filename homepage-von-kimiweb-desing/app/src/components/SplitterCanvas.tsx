import { useRef, useEffect, useCallback } from 'react'

const COLORS: [number, number, number][] = [
  [211, 211, 216], // Metallic Silver
  [0, 212, 255],   // Entity Cyan
  [255, 27, 141],  // Core Magenta
  [255, 140, 66],  // Warm Amber
  [184, 0, 92],    // Deep Magenta
  [212, 211, 216], // Silver
]

const BASE_RADIUS = 6
const MAX_SPEED = 2
const GRAVITY = 0.02
const FRICTION = 0.98
const SPRING_K = 0.05
const SPLIT_INTERVAL = 5000
const MAX_DEPTH = 6
const MAX_NODES = 40
const DRIFT_SPEED = 0.3

interface SplitterNode {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  colorIndex: number
  birth: number
  lastSplit: number
  depth: number
  hueShift: number
  connections: number[]
  oscPhase: number
}

export default function SplitterCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const nodesRef = useRef<SplitterNode[]>([])
  const mouseRef = useRef({ x: 0, y: 0 })
  const frameRef = useRef<number>(0)
  const visibleRef = useRef(true)

  const spawnNode = useCallback((x: number, y: number, vx: number, vy: number, depth: number, parentHue: number = 0) => {
    const radius = BASE_RADIUS * Math.pow(0.75, depth)
    const node: SplitterNode = {
      x,
      y,
      vx: vx * 0.5,
      vy: vy * 0.5,
      radius,
      colorIndex: Math.floor(Math.random() * COLORS.length),
      birth: performance.now(),
      lastSplit: performance.now(),
      depth,
      hueShift: parentHue + (Math.random() - 0.5) * 40,
      connections: [],
      oscPhase: Math.random() * Math.PI * 2,
    }
    nodesRef.current.push(node)
    return node
  }, [])

  const trySplit = useCallback(() => {
    const nodes = nodesRef.current
    if (nodes.length >= MAX_NODES) return
    const now = performance.now()

    for (let idx = 0; idx < nodes.length; idx++) {
      const node = nodes[idx]
      if (node.depth >= MAX_DEPTH) continue
      if (now - node.lastSplit < SPLIT_INTERVAL) continue

      let nearby = 0
      for (let i = 0; i < nodes.length; i++) {
        if (i === idx) continue
        const dist = Math.hypot(nodes[i].x - node.x, nodes[i].y - node.y)
        if (dist < 100) nearby++
      }

      const energy = 0.5 * (node.vx * node.vx + node.vy * node.vy)
      const splitChance = 0.001 + (energy * 0.1) + (nearby * 0.01)

      if (Math.random() < splitChance) {
        node.lastSplit = now
        const angle = Math.atan2(node.vy, node.vx)
        const spread = Math.PI / 4

        for (let i = 0; i < 2; i++) {
          const childAngle = angle + (i === 0 ? -spread : spread)
          const speed = Math.hypot(node.vx, node.vy) * 1.5 + 1
          spawnNode(
            node.x,
            node.y,
            Math.cos(childAngle) * speed,
            Math.sin(childAngle) * speed,
            node.depth + 1,
            node.hueShift
          )
        }

        const parentIndex = nodes.indexOf(node)
        nodes.splice(parentIndex, 1)

        // Rebuild connections
        for (const n of nodes) {
          n.connections = []
        }
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const dist = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y)
            if (dist < 150) {
              nodes[i].connections.push(j)
              nodes[j].connections.push(i)
            }
          }
        }
        break
      }
    }
  }, [spawnNode])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    function resize() {
      const parent = canvas!.parentElement
      if (!parent) return
      canvas!.width = parent.offsetWidth
      canvas!.height = parent.offsetHeight
    }

    resize()
    window.addEventListener('resize', resize)

    // Spawn initial node
    if (nodesRef.current.length === 0) {
      spawnNode(canvas.width * 0.5, canvas.height * 0.5, 0, 0, 1, 0)
    }

    function updateNodes() {
      const nodes = nodesRef.current
      const w = canvas!.width
      const h = canvas!.height

      for (const node of nodes) {
        // Gravity
        node.vy += GRAVITY

        // Speed limit
        const speed = Math.hypot(node.vx, node.vy)
        if (speed > MAX_SPEED) {
          node.vx = (node.vx / speed) * MAX_SPEED
          node.vy = (node.vy / speed) * MAX_SPEED
        }

        // Position update
        node.x += node.vx
        node.y += node.vy
        node.vx *= FRICTION
        node.vy *= FRICTION

        // Mouse repulsion
        const mdx = node.x - mouseRef.current.x
        const mdy = node.y - mouseRef.current.y
        const mDist = Math.hypot(mdx, mdy)
        if (mDist < 80 && mDist > 0) {
          const force = (80 - mDist) / 80 * 0.3
          node.vx += (mdx / mDist) * force
          node.vy += (mdy / mDist) * force
        }

        // Drift
        node.vx += (Math.random() - 0.5) * DRIFT_SPEED * 0.1
        node.vy += (Math.random() - 0.5) * DRIFT_SPEED * 0.1

        // Boundaries
        if (node.x < node.radius) { node.x = node.radius; node.vx *= -0.5 }
        if (node.x > w - node.radius) { node.x = w - node.radius; node.vx *= -0.5 }
        if (node.y < node.radius) { node.y = node.radius; node.vy *= -0.5 }
        if (node.y > h - node.radius) { node.y = h - node.radius; node.vy *= -0.5 }
      }

      // Spring connections
      for (const node of nodes) {
        for (const otherIndex of node.connections) {
          const other = nodes[otherIndex]
          if (!other) continue
          const dx = other.x - node.x
          const dy = other.y - node.y
          const dist = Math.hypot(dx, dy)
          const springLen = (node.radius + other.radius) * 2
          if (dist > 0 && dist > springLen) {
            const force = (dist - springLen) * SPRING_K
            node.vx += (dx / dist) * force
            node.vy += (dy / dist) * force
            other.vx -= (dx / dist) * force
            other.vy -= (dy / dist) * force
          }
        }
      }
    }

    function renderNodes() {
      const w = canvas!.width
      const h = canvas!.height
      const nodes = nodesRef.current
      const now = performance.now()

      ctx!.clearRect(0, 0, w, h)

      // Background
      ctx!.fillStyle = '#050508'
      ctx!.fillRect(0, 0, w, h)

      // Connections
      for (let i = 0; i < nodes.length; i++) {
        for (const otherIndex of nodes[i].connections) {
          if (otherIndex <= i) continue
          const other = nodes[otherIndex]
          if (!other) continue
          const dist = Math.hypot(nodes[i].x - other.x, nodes[i].y - other.y)
          const alpha = Math.max(0, 1 - dist / 150) * 0.6
          ctx!.strokeStyle = `rgba(255, 27, 141, ${alpha})`
          ctx!.lineWidth = 1.5
          ctx!.beginPath()
          ctx!.moveTo(nodes[i].x, nodes[i].y)
          ctx!.lineTo(other.x, other.y)
          ctx!.stroke()
        }
      }

      // Nodes
      for (const node of nodes) {
        const color = COLORS[node.colorIndex]
        const pulse = Math.sin(now * 0.002 + node.oscPhase) * 2
        const r = node.radius + pulse

        // Main circle
        ctx!.beginPath()
        ctx!.arc(node.x, node.y, Math.max(r, 2), 0, Math.PI * 2)
        ctx!.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.9)`
        ctx!.fill()

        // Highlight ring
        ctx!.beginPath()
        ctx!.arc(node.x, node.y, Math.max(r + 2, 4), 0, Math.PI * 2)
        ctx!.fillStyle = 'rgba(255, 255, 255, 0.1)'
        ctx!.fill()
      }
    }

    let lastSplitTry = 0
    function loop() {
      if (!visibleRef.current) {
        frameRef.current = requestAnimationFrame(loop)
        return
      }
      updateNodes()

      const now = performance.now()
      if (now - lastSplitTry > 100) {
        trySplit()
        lastSplitTry = now
      }

      renderNodes()
      frameRef.current = requestAnimationFrame(loop)
    }

    // IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        visibleRef.current = entries[0]?.isIntersecting ?? true
      },
      { threshold: 0.1 }
    )
    observer.observe(canvas)

    frameRef.current = requestAnimationFrame(loop)

    // Mouse handlers
    function handleMouseMove(e: MouseEvent) {
      const rect = canvas!.getBoundingClientRect()
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      }
    }

    function handleClick(e: MouseEvent) {
      const rect = canvas!.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      spawnNode(x, y, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, 0, 0)
    }

    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('click', handleClick)

    return () => {
      cancelAnimationFrame(frameRef.current)
      window.removeEventListener('resize', resize)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('click', handleClick)
      observer.disconnect()
    }
  }, [spawnNode, trySplit])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
      }}
    />
  )
}
