import { clsx } from 'clsx'

export default function Card({ children, className = '', hover = true, glow = false }) {
  return (
    <div className={clsx(
      'glass-card p-5',
      hover && 'hover:-translate-y-0.5 hover:shadow-card-hover',
      glow && 'shadow-glow-red',
      className
    )}>
      {children}
    </div>
  )
}

export function StatCard({ label, value, sub, icon, color = 'blood' }) {
  const colors = {
    blood:   { ring: 'border-blood-700/40', icon: 'text-blood-400', val: 'text-blood-300' },
    green:   { ring: 'border-emerald-700/40', icon: 'text-emerald-400', val: 'text-emerald-300' },
    blue:    { ring: 'border-blue-700/40', icon: 'text-blue-400', val: 'text-blue-300' },
    gold:    { ring: 'border-yellow-700/40', icon: 'text-yellow-400', val: 'text-yellow-300' },
    purple:  { ring: 'border-purple-700/40', icon: 'text-purple-400', val: 'text-purple-300' },
  }
  const c = colors[color] || colors.blood
  return (
    <div className={clsx('glass-card p-5 border', c.ring)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-white/40 uppercase tracking-wider font-semibold mb-1">{label}</p>
          <p className={clsx('text-3xl font-heading font-black', c.val)}>{value}</p>
          {sub && <p className="text-xs text-white/40 mt-1">{sub}</p>}
        </div>
        {icon && <span className={clsx('w-8 h-8 flex-shrink-0', c.icon)}>{icon}</span>}
      </div>
    </div>
  )
}

export function SectionHeader({ title, subtitle }) {
  return (
    <div className="mb-8">
      <h2 className="sec-header mb-2">{title}</h2>
      {subtitle && <p className="text-white/50 text-sm">{subtitle}</p>}
    </div>
  )
}
