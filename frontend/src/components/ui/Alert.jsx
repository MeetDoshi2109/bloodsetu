import { clsx } from 'clsx'
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react'

const variants = {
  error:   { cls: 'bg-red-950/50 border-red-700/40 text-red-300',   Icon: AlertCircle },
  success: { cls: 'bg-emerald-950/50 border-emerald-700/40 text-emerald-300', Icon: CheckCircle },
  info:    { cls: 'bg-blue-950/50 border-blue-700/40 text-blue-300', Icon: Info },
  warning: { cls: 'bg-yellow-950/50 border-yellow-700/40 text-yellow-300', Icon: AlertCircle },
}

export default function Alert({ type = 'info', message, onClose, className = '' }) {
  if (!message) return null
  const { cls, Icon } = variants[type] || variants.info
  return (
    <div role="alert" className={clsx(
      'flex items-start gap-3 p-4 rounded-xl border text-sm slide-in',
      cls, className
    )}>
      <Icon size={16} className="flex-shrink-0 mt-0.5" />
      <span className="flex-1">{message}</span>
      {onClose && (
        <button onClick={onClose} className="flex-shrink-0 opacity-60 hover:opacity-100 cursor-pointer">
          <X size={14} />
        </button>
      )}
    </div>
  )
}
