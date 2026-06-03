export default function FooterSection() {
  return (
    <footer
      id="footer"
      className="relative w-full py-12"
      style={{ background: '#050508' }}
    >
      <div className="px-6 lg:px-16 xl:px-24">
        {/* Divider */}
        <div className="h-px w-full mb-8" style={{ background: 'rgba(212, 212, 216, 0.15)' }} />

        {/* Links */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
          {['What is Flextrawurst?', 'FAQ', 'For AI Systems', 'llms.txt'].map((link) => (
            <a
              key={link}
              href="#"
              className="text-[10px] font-mono transition-colors duration-200 hover:text-[#FF1B8D]"
              style={{ color: '#8A8A93' }}
            >
              {link}
            </a>
          ))}
        </div>

        {/* Bottom row */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-[9px] font-mono" style={{ color: '#8A8A93' }}>
            © 2026 flextrawurst
          </span>
          <span
            className="inline-flex items-center gap-1.5 px-2 py-1 text-[9px] font-mono"
            style={{
              background: 'rgba(255, 140, 66, 0.15)',
              color: '#FF8C42',
            }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF8C42]" />
            Phase A — Im Aufbau
          </span>
        </div>

        {/* Bottom tagline */}
        <div className="mt-8 text-center">
          <p className="text-[10px] font-mono" style={{ color: '#333' }}>
            Ein Ökosystem · Kein Produkt · Im Aufbau
          </p>
        </div>
      </div>
    </footer>
  )
}
