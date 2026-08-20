import { clsx } from 'clsx'

const BLOOD_GROUP_COLORS = {
  'A+': 'from-red-700 to-red-900',
  'A-': 'from-red-600 to-red-800',
  'B+': 'from-orange-700 to-red-800',
  'B-': 'from-orange-600 to-red-700',
  'O+': 'from-blood-700 to-blood-900',
  'O-': 'from-blood-600 to-blood-800',
  'AB+':'from-purple-700 to-blood-900',
  'AB-':'from-purple-600 to-blood-800',
}

export function BloodGroupBadge({ group, size = 'md' }) {
  const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-12 h-12 text-sm', lg: 'w-16 h-16 text-lg', xl: 'w-20 h-20 text-xl' }
  const gradient = BLOOD_GROUP_COLORS[group] || 'from-blood-700 to-blood-900'
  return (
    <span className={clsx(
      'bg-badge flex-shrink-0',
      `bg-gradient-to-br ${gradient}`,
      sizes[size]
    )}>
      {group}
    </span>
  )
}

export function StatusBadge({ status }) {
  const variants = {
    Available:   'tag-verified',
    Unavailable: 'tag-critical',
    Pending:     'tag-pending',
    Confirmed:   'tag-verified',
    Cancelled:   'tag-critical',
    Verified:    'tag-verified',
  }
  return <span className={variants[status] || 'tag-pending'}>{status}</span>
}

export function DonorBadge({ badge, earned = true }) {
  const ICONS = {
    first_drop: '🩸', life_saver: '❤️', emergency: '⚡',
    fast: '🚀', rare_blood: '💎', legend: '👑',
  }
  return (
    <div className={clsx(
      'flex flex-col items-center gap-2 p-4 rounded-xl border text-center',
      earned
        ? 'border-yellow-600/40 bg-yellow-900/10'
        : 'border-white/5 bg-white/2 opacity-40 grayscale'
    )}>
      <span className="text-3xl">{ICONS[badge.id] || '🏅'}</span>
      <div>
        <p className={clsx('text-xs font-bold', earned ? 'text-yellow-300' : 'text-white/40')}>{badge.name}</p>
        <p className="text-[10px] text-white/30 mt-0.5">{badge.condition}</p>
      </div>
      {earned && <span className="tag-verified text-[10px]">Earned</span>}
    </div>
  )
}
