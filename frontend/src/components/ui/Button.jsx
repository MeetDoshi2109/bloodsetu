import { clsx } from 'clsx'

const variants = {
  primary:   'bg-gradient-to-r from-blood-700 to-blood-600 hover:from-blood-600 hover:to-blood-500 text-white shadow-blood',
  secondary: 'bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white',
  danger:    'bg-gradient-to-r from-red-800 to-red-700 hover:from-red-700 hover:to-red-600 text-white',
  ghost:     'hover:bg-white/5 text-white/70 hover:text-white',
  success:   'bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-600 hover:to-emerald-500 text-white',
  sos:       'bg-gradient-to-r from-blood-700 to-red-600 hover:from-blood-600 hover:to-red-500 text-white sos-pulse',
}

const sizes = {
  sm:  'px-3 py-1.5 text-xs',
  md:  'px-4 py-2.5 text-sm',
  lg:  'px-6 py-3 text-base',
  xl:  'px-8 py-4 text-lg',
}

export default function Button({
  children, variant = 'primary', size = 'md',
  className = '', disabled = false, loading = false,
  icon, fullWidth = false, ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl font-semibold',
        'transition-all duration-200 cursor-pointer',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blood-500 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0303]',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant], sizes[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading ? (
        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : icon ? (
        <span className="w-4 h-4 flex-shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  )
}
