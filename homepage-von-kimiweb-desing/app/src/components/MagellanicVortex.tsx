import { useRef, useEffect } from 'react'
import * as THREE from 'three'

const HEIGHT = 14
const TWISTS = 1.0
const SEGMENTS_X = 128
const SEGMENTS_Y = 128

function createParametricGeometry() {
  const positions: number[] = []
  const normals: number[] = []
  const indices: number[] = []

  for (let y = 0; y <= SEGMENTS_Y; y++) {
    for (let x = 0; x <= SEGMENTS_X; x++) {
      const u = x / SEGMENTS_X
      const v = y / SEGMENTS_Y
      const theta = u * Math.PI * 2
      const phi = v * Math.PI

      const radius = 3 * Math.sin(phi)
      const t = phi * TWISTS * Math.PI * 2
      const tx = Math.cos(t) * 0.4
      const ty = Math.sin(t) * 0.4

      const px = (radius + tx) * Math.cos(theta)
      const py = (radius + tx) * Math.sin(theta)
      const pz = phi * HEIGHT + ty

      positions.push(px, py, pz)

      const r = 3 * Math.sin(phi)
      const dr = 3 * Math.cos(phi)
      const dPdu = new THREE.Vector3(
        -r * Math.sin(theta),
        r * Math.cos(theta),
        0
      ).normalize()
      const dPdv = new THREE.Vector3(
        dr * Math.cos(theta),
        dr * Math.sin(theta),
        HEIGHT
      ).normalize()
      const normal = dPdu.cross(dPdv).normalize()
      normals.push(normal.x, normal.y, normal.z)
    }
  }

  for (let y = 0; y < SEGMENTS_Y; y++) {
    for (let x = 0; x < SEGMENTS_X; x++) {
      const a = y * (SEGMENTS_X + 1) + x
      const b = a + SEGMENTS_X + 1
      const c = a + 1
      const d = b + 1
      indices.push(a, b, c, b, d, c)
    }
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3))
  geometry.setIndex(indices)
  return geometry
}

const dataStreamVertexShader = `
  varying vec2 vUv;
  varying float vY;
  uniform float time;
  uniform float speed;

  void main() {
    vUv = uv;
    vY = position.y;
    vec3 pos = position;
    pos.x += sin(pos.y * 2.0 + time * speed) * 0.2;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`

const dataStreamFragmentShader = `
  varying vec2 vUv;
  varying float vY;
  uniform vec3 color;
  uniform float time;
  uniform float speed;
  uniform float globalAlpha;

  void main() {
    float travelingLight = sin(vY * 5.0 - time * speed * 10.0);
    float alpha = smoothstep(0.2, 0.8, travelingLight) * globalAlpha * (0.5 + 0.5 * vUv.x);
    gl_FragColor = vec4(color, alpha);
  }
`

interface DataStreamLine {
  mesh: THREE.Line
  speed: number
}

function createDataStreams(numStreams: number): { group: THREE.Group; lines: DataStreamLine[] } {
  const group = new THREE.Group()
  const lines: DataStreamLine[] = []
  const streamPoints = 64
  const height = HEIGHT
  const radiusTop = 0.5
  const radiusBottom = 3

  for (let i = 0; i < numStreams; i++) {
    const points: THREE.Vector3[] = []
    const yStart = Math.random() * height
    const speed = 0.2 + Math.random() * 0.5
    const angle = Math.random() * Math.PI * 2

    for (let j = 0; j < streamPoints; j++) {
      const t = j / (streamPoints - 1)
      const y = yStart + t * height
      const r = radiusBottom + (radiusTop - radiusBottom) * t
      const x = Math.cos(angle + t * Math.PI * 2) * r
      const z = Math.sin(angle + t * Math.PI * 2) * r
      points.push(new THREE.Vector3(x, y, z))
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.ShaderMaterial({
      vertexShader: dataStreamVertexShader,
      fragmentShader: dataStreamFragmentShader,
      uniforms: {
        time: { value: 0 },
        speed: { value: speed },
        color: { value: new THREE.Color(0x00d4ff) },
        globalAlpha: { value: 0.6 },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })

    const line = new THREE.Line(geometry, material)
    group.add(line)
    lines.push({ mesh: line, speed })
  }

  return { group, lines }
}

export default function MagellanicVortex() {
  const containerRef = useRef<HTMLDivElement>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const frameRef = useRef<number>(0)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const w = container.offsetWidth || 600
    const h = container.offsetHeight || 800

    // Scene
    const scene = new THREE.Scene()
    scene.fog = new THREE.FogExp2(0x0a0a0a, 0.02)

    const camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 100)
    camera.position.set(-13, 6, 13)
    camera.lookAt(0, 4, 0)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x0a0a0a, 0)
    container.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5)
    scene.add(ambientLight)

    const pointLight = new THREE.PointLight(0xff1b8d, 800, 25)
    pointLight.position.set(0, 4, 0)
    scene.add(pointLight)

    const cyanLight = new THREE.PointLight(0x00d4ff, 200, 20)
    cyanLight.position.set(5, 8, 5)
    scene.add(cyanLight)

    // Parametric Mesh
    const geometry = createParametricGeometry()
    const material = new THREE.MeshPhysicalMaterial({
      color: 0xff1b8d,
      metalness: 0.6,
      roughness: 0.7,
      emissive: 0xff1b8d,
      emissiveIntensity: 0.25,
      side: THREE.DoubleSide,
      wireframe: false,
      transparent: true,
      opacity: 0.85,
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.castShadow = true
    mesh.receiveShadow = true
    mesh.position.y = -5
    scene.add(mesh)

    // Data Streams
    const { group: streamGroup, lines } = createDataStreams(20)
    scene.add(streamGroup)

    // Camera animation along bezier
    const clock = new THREE.Clock()
    let cameraT = 0
    const cameraDuration = 6

    function getBezierPoint(t: number): THREE.Vector3 {
      const p0 = new THREE.Vector3(-13, 6, 13)
      const p1 = new THREE.Vector3(-2, 16, 2)
      const p2 = new THREE.Vector3(10, 5, 10)
      const p3 = new THREE.Vector3(15, 6, 12)
      const oneMinusT = 1 - t
      return p0
        .clone()
        .multiplyScalar(oneMinusT * oneMinusT * oneMinusT)
        .add(p1.clone().multiplyScalar(3 * oneMinusT * oneMinusT * t))
        .add(p2.clone().multiplyScalar(3 * oneMinusT * t * t))
        .add(p3.clone().multiplyScalar(t * t * t))
    }

    // Animation loop
    function animate() {
      frameRef.current = requestAnimationFrame(animate)
      const elapsed = clock.getElapsedTime()
      const dt = clock.getDelta()

      // Rotate mesh
      mesh.rotation.y += 0.001

      // Orbit point light
      const lightRadius = 8
      pointLight.position.x = Math.cos(elapsed * 0.3) * lightRadius
      pointLight.position.z = Math.sin(elapsed * 0.3) * lightRadius
      pointLight.position.y = 6 + Math.sin(elapsed * 0.5) * 3

      // Update data streams
      for (const line of lines) {
        const mat = line.mesh.material as THREE.ShaderMaterial
        mat.uniforms.time.value = elapsed
      }

      // Camera animation
      if (cameraT < 1) {
        cameraT += dt / cameraDuration
        const easedT = cameraT < 0.5
          ? 4 * cameraT * cameraT * cameraT
          : 1 - Math.pow(-2 * cameraT + 2, 3) / 2
        const pos = getBezierPoint(Math.min(easedT, 1))
        camera.position.copy(pos)
        camera.lookAt(0, 4, 0)
      }

      renderer.render(scene, camera)
    }

    animate()

    // Resize handler
    function handleResize() {
      if (!container) return
      const newW = container.offsetWidth
      const newH = container.offsetHeight
      camera.aspect = newW / newH
      camera.updateProjectionMatrix()
      renderer.setSize(newW, newH)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(frameRef.current)
      window.removeEventListener('resize', handleResize)
      renderer.dispose()
      geometry.dispose()
      material.dispose()
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
    }
  }, [])

  return (
    <div
      ref={containerRef}
      style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: '50%',
        height: '100%',
        zIndex: 1,
      }}
    />
  )
}
