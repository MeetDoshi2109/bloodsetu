import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, X } from 'lucide-react'
import api from '../../api/client'

export default function SOSBanner() {
  const [sos, setSos]         = useState([])
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    api.get('/sos/active').then(r => setSos(r.data)).catch(() => {})
  }, [])

  if (!sos.length || dismissed) return null
  const latest = sos[0]

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="w-full rounded-2xl border border-red-600/50 p-4 mb-6 flex items-center gap-4 slide-in"
      style={{ background: 'linear-gradient(135deg, rgba(192,57,43,0.18), rgba(120,20,20,0.1))' }}
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-700/30 flex items-center justify-center sos-pulse">
        <AlertTriangle size={18} className="text-red-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold text-red-400 uppercase tracking-widest">Active Emergency</p>
        <p className="text-sm text-white font-semibold mt-0.5">
          <span
            className="inline-block font-black text-red-300 mr-2 px-2 py-0.5 rounded-full text-xs"
            style={{ background: 'rgba(192,57,43,0.3)', border: '1px solid rgba(231,76,60,0.4)' }}
          >
            {latest.blood_group}
          </span>
          needed in <span className="text-white font-bold">{latest.area}, {latest.city}</span>
          {latest.urgency === 'Critical' && (
            <span className="ml-2 tag-critical">Critical</span>
          )}
        </p>
        {latest.seeker_phone && (
          <p className="text-xs text-white/50 mt-0.5">Contact: {latest.seeker_phone}</p>
        )}
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <Link
          to="/find-blood"
          className="px-3 py-1.5 rounded-lg text-xs font-bold text-white cursor-pointer transition-colors"
          style={{ background: 'linear-gradient(135deg, #c0392b, #7b241c)' }}
        >
          Respond
        </Link>
        <button
          onClick={() => setDismissed(true)}
          className="text-white/30 hover:text-white/70 cursor-pointer p-1"
          aria-label="Dismiss"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  )
}
