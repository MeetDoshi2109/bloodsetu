import { clsx } from 'clsx'

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-xl bg-white/3 border border-white/5 mb-6">
      {tabs.map(t => (
        <button
          key={t.id}
          className={clsx('tab-btn flex items-center gap-2', active === t.id && 'active')}
          onClick={() => onChange(t.id)}
        >
          {t.icon && <span className="w-4 h-4">{t.icon}</span>}
          <span>{t.label}</span>
          {t.count != null && (
            <span className={clsx(
              'text-[10px] font-bold px-1.5 py-0.5 rounded-full',
              active === t.id ? 'bg-blood-700/50 text-blood-200' : 'bg-white/10 text-white/40'
            )}>
              {t.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
