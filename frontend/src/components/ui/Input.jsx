import { clsx } from 'clsx'

export function Input({ label, error, hint, icon, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-semibold text-white/60 uppercase tracking-wider">{label}</label>}
      <div className="relative">
        {icon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 w-4 h-4">
            {icon}
          </span>
        )}
        <input
          className={clsx(
            'bs-input',
            icon && 'pl-10',
            error && 'border-red-500/60 focus:border-red-500',
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
      {hint && !error && <p className="text-xs text-white/30">{hint}</p>}
    </div>
  )
}

export function Select({ label, error, children, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-semibold text-white/60 uppercase tracking-wider">{label}</label>}
      <select className={clsx('bs-select', className)} {...props}>
        {children}
      </select>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}

export function Checkbox({ label, ...props }) {
  return (
    <label className="flex items-start gap-3 cursor-pointer group">
      <input
        type="checkbox"
        className="mt-0.5 w-4 h-4 rounded border-white/20 bg-white/5 accent-blood-600 cursor-pointer flex-shrink-0"
        {...props}
      />
      <span className="text-sm text-white/70 group-hover:text-white/90 transition-colors">{label}</span>
    </label>
  )
}
