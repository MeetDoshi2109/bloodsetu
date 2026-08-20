import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CheckCircle, XCircle, AlertTriangle, Building2,
  Droplets, CalendarDays, Users, Shield, Database
} from 'lucide-react'
import Layout, { PageHeader } from '../components/layout/Layout'
import { Tabs } from '../components/ui/Tabs'
import Button from '../components/ui/Button'
import { StatCard } from '../components/ui/Card'
import Alert from '../components/ui/Alert'
import { BloodGroupBadge } from '../components/ui/Badge'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

/* ── Pending Hospitals ─────────────────────────── */
function PendingHospitals({ onUpdate }) {
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  useEffect(() => {
    api.get('/admin/pending').then(r => setItems(r.data.hospitals || [])).finally(() => setLoading(false))
  }, [])

  const verify = async (id) => {
    await api.post('/admin/verify', { entity_type: 'hospital', entity_id: id })
    setItems(i => i.filter(x => x.id !== id))
    setMsg('Hospital verified successfully.')
    onUpdate()
  }

  const reject = async (id) => {
    await api.delete(`/admin/entity/hospital/${id}`)
    setItems(i => i.filter(x => x.id !== id))
    setMsg('Hospital removed.')
    onUpdate()
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-4">
      {msg && <Alert type="success" message={msg} onClose={() => setMsg('')} />}
      {!items.length
        ? <div className="text-center py-16 text-white/30 space-y-2"><Building2 size={40} className="mx-auto opacity-20" /><p>No pending hospitals.</p></div>
        : items.map(h => (
          <div key={h.id} className="glass-card p-5 flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="tag-pending">Pending</span>
                {h.emergency_24x7 ? <span className="tag-critical text-[10px]">24×7</span> : null}
              </div>
              <p className="font-semibold text-white">{h.name}</p>
              {h.doctor_name && <p className="text-xs text-white/50">Dr. {h.doctor_name}</p>}
              <p className="text-xs text-white/35 mt-0.5">{h.area}, {h.city} · {h.phone}</p>
              <p className="text-xs text-white/20 mt-0.5">Registered: {h.created_at?.slice(0, 10)}</p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button size="sm" variant="success" onClick={() => verify(h.id)} icon={<CheckCircle size={13} />}>Verify</Button>
              <Button size="sm" variant="danger"  onClick={() => reject(h.id)} icon={<XCircle size={13} />}>Reject</Button>
            </div>
          </div>
        ))
      }
    </div>
  )
}

/* ── Pending Blood Banks ───────────────────────── */
function PendingBanks({ onUpdate }) {
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  useEffect(() => {
    api.get('/admin/pending').then(r => setItems(r.data.blood_banks || [])).finally(() => setLoading(false))
  }, [])

  const verify = async (id) => {
    await api.post('/admin/verify', { entity_type: 'blood_bank', entity_id: id })
    setItems(i => i.filter(x => x.id !== id)); setMsg('Blood bank verified.'); onUpdate()
  }
  const reject = async (id) => {
    await api.delete(`/admin/entity/blood_bank/${id}`)
    setItems(i => i.filter(x => x.id !== id)); setMsg('Removed.'); onUpdate()
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-4">
      {msg && <Alert type="success" message={msg} onClose={() => setMsg('')} />}
      {!items.length
        ? <div className="text-center py-16 text-white/30 space-y-2"><Droplets size={40} className="mx-auto opacity-20" /><p>No pending blood banks.</p></div>
        : items.map(b => (
          <div key={b.id} className="glass-card p-5 flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1 min-w-0">
              <span className="tag-pending mb-1 inline-block">Pending</span>
              <p className="font-semibold text-white">{b.name}</p>
              {b.doctor_name && <p className="text-xs text-white/50">Dr. {b.doctor_name}</p>}
              <p className="text-xs text-white/35 mt-0.5">{b.area}, {b.city} · {b.phone}</p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button size="sm" variant="success" onClick={() => verify(b.id)} icon={<CheckCircle size={13} />}>Verify</Button>
              <Button size="sm" variant="danger"  onClick={() => reject(b.id)} icon={<XCircle size={13} />}>Reject</Button>
            </div>
          </div>
        ))
      }
    </div>
  )
}

/* ── Pending Camps ─────────────────────────────── */
function PendingCamps({ onUpdate }) {
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  useEffect(() => {
    api.get('/admin/pending').then(r => setItems(r.data.camps || [])).finally(() => setLoading(false))
  }, [])

  const verify = async (id) => {
    await api.post('/admin/verify', { entity_type: 'camp', entity_id: id })
    setItems(i => i.filter(x => x.id !== id)); setMsg('Camp verified.'); onUpdate()
  }
  const reject = async (id) => {
    await api.delete(`/admin/entity/camp/${id}`)
    setItems(i => i.filter(x => x.id !== id)); setMsg('Removed.'); onUpdate()
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-4">
      {msg && <Alert type="success" message={msg} onClose={() => setMsg('')} />}
      {!items.length
        ? <div className="text-center py-16 text-white/30 space-y-2"><CalendarDays size={40} className="mx-auto opacity-20" /><p>No pending camps.</p></div>
        : items.map(c => (
          <div key={c.id} className="glass-card p-5 flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1 min-w-0">
              <span className="tag-pending mb-1 inline-block">Pending</span>
              <p className="font-semibold text-white">{c.organizer}</p>
              {c.doctor_name && <p className="text-xs text-white/50">Dr. {c.doctor_name}</p>}
              <p className="text-xs text-white/35 mt-0.5">{c.area}, {c.city} · {c.camp_date}</p>
              {c.timings && <p className="text-xs text-white/25">{c.timings}</p>}
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button size="sm" variant="success" onClick={() => verify(c.id)} icon={<CheckCircle size={13} />}>Verify</Button>
              <Button size="sm" variant="danger"  onClick={() => reject(c.id)} icon={<XCircle size={13} />}>Reject</Button>
            </div>
          </div>
        ))
      }
    </div>
  )
}

/* ── Fraud Panel ───────────────────────────────── */
function FraudPanel() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  useEffect(() => {
    api.get('/admin/fraud-reports').then(r => setReports(r.data)).finally(() => setLoading(false))
  }, [])

  const act = async (id, action) => {
    await api.post('/admin/fraud-action', { report_id: id, action })
    setReports(r => r.map(x => x.id === id ? { ...x, admin_action: action } : x))
    setMsg(`Report ${action === 'Blocked' ? 'blocked' : 'ignored'}.`)
  }

  const pending  = reports.filter(r => r.admin_action === 'Pending')
  const resolved = reports.filter(r => r.admin_action !== 'Pending')

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-6">
      {msg && <Alert type="info" message={msg} onClose={() => setMsg('')} />}

      <div>
        <h3 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-3">Pending ({pending.length})</h3>
        {!pending.length
          ? <p className="text-white/25 text-sm">No pending reports.</p>
          : pending.map(r => (
            <div key={r.id} className="glass-card p-4 flex flex-col sm:flex-row sm:items-center gap-4 mb-3"
              style={{ borderColor: 'rgba(231,76,60,0.3)' }}>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-white text-sm">Phone: {r.reported_phone}</p>
                <p className="text-xs text-white/50 mt-0.5">Reason: {r.reason}</p>
                <p className="text-xs text-white/30">By: {r.reported_by_type} · {r.reported_at?.slice(0, 16)}</p>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <Button size="sm" variant="danger"   onClick={() => act(r.id, 'Blocked')} icon={<Shield size={13} />}>Block</Button>
                <Button size="sm" variant="secondary" onClick={() => act(r.id, 'Ignored')}>Ignore</Button>
              </div>
            </div>
          ))
        }
      </div>

      {resolved.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-3">Resolved ({resolved.length})</h3>
          <div className="space-y-2">
            {resolved.map(r => (
              <div key={r.id} className="glass-card p-3 flex items-center gap-3 opacity-60">
                <span className={r.admin_action === 'Blocked' ? 'tag-critical' : 'tag-verified'}>{r.admin_action}</span>
                <p className="text-xs text-white/50">{r.reported_phone} · {r.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Platform Database ─────────────────────────── */
function PlatformDB() {
  const [donors,    setDonors]    = useState([])
  const [hospitals, setHospitals] = useState([])
  const [banks,     setBanks]     = useState([])
  const [camps,     setCamps]     = useState([])
  const [open,      setOpen]      = useState('donors')
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/admin/all-donors'),
      api.get('/admin/all-hospitals'),
      api.get('/admin/all-blood-banks'),
      api.get('/admin/all-camps'),
    ]).then(([d, h, b, c]) => {
      setDonors(d.data); setHospitals(h.data); setBanks(b.data); setCamps(c.data)
    }).catch(() => {
      setDonors([]); setHospitals([]); setBanks([]); setCamps([])
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-white/30">Loading database…</div>

  const sections = [
    { id: 'donors',    label: `Donors (${donors.length})`,    data: donors,    cols: ['name','blood_group','city','area','phone','status','donations_count'] },
    { id: 'hospitals', label: `Hospitals (${hospitals.length})`, data: hospitals, cols: ['name','city','area','phone','blood_available','is_verified'] },
    { id: 'banks',     label: `Blood Banks (${banks.length})`, data: banks,     cols: ['name','city','area','phone','groups_available','is_verified'] },
    { id: 'camps',     label: `Camps (${camps.length})`,      data: camps,     cols: ['organizer','city','area','camp_date','timings','is_verified'] },
  ]

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {sections.map(s => (
          <button key={s.id} onClick={() => setOpen(s.id)}
            className={`px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${open === s.id ? 'bg-blood-700/30 text-blood-300 border border-blood-700/40' : 'bg-white/5 text-white/50 hover:text-white border border-white/5'}`}>
            {s.label}
          </button>
        ))}
      </div>

      {sections.filter(s => s.id === open).map(s => (
        <div key={s.id} className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/8">
                  {s.cols.map(c => (
                    <th key={c} className="px-4 py-3 text-left text-white/40 font-semibold uppercase tracking-wider whitespace-nowrap">
                      {c.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {s.data.map((row, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/3">
                    {s.cols.map(c => (
                      <td key={c} className="px-4 py-3 text-white/70 whitespace-nowrap">
                        {c === 'blood_group'
                          ? <BloodGroupBadge group={row[c]} size="sm" />
                          : c === 'is_verified'
                            ? <span className={row[c] ? 'tag-verified' : 'tag-pending'}>{row[c] ? 'Yes' : 'No'}</span>
                            : c === 'status'
                              ? <span className={row[c] === 'Available' ? 'tag-verified' : 'tag-critical'}>{row[c]}</span>
                              : String(row[c] ?? '—').slice(0, 40)
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {s.data.length === 0 && <p className="text-center py-8 text-white/30">No records.</p>}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ── Main Admin ────────────────────────────────── */
export default function Admin() {
  const { user }  = useAuth()
  const navigate  = useNavigate()
  const [tab,     setTab]     = useState('hospitals')
  const [stats,   setStats]   = useState(null)
  const [pending, setPending] = useState({ hospitals: [], blood_banks: [], camps: [] })

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    if (user.role !== 'admin') { navigate('/'); return }
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
    api.get('/admin/pending').then(r => setPending(r.data)).catch(() => {})
  }, [user])

  const refreshPending = () => {
    api.get('/admin/pending').then(r => setPending(r.data)).catch(() => {})
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
  }

  if (!user || user.role !== 'admin') return null

  const totalPending = (pending.hospitals?.length || 0) + (pending.blood_banks?.length || 0) + (pending.camps?.length || 0)

  const TABS = [
    { id: 'hospitals', label: 'Hospitals',   icon: <Building2 size={15} />,    count: pending.hospitals?.length },
    { id: 'banks',     label: 'Blood Banks', icon: <Droplets size={15} />,     count: pending.blood_banks?.length },
    { id: 'camps',     label: 'Camps',       icon: <CalendarDays size={15} />, count: pending.camps?.length },
    { id: 'fraud',     label: 'Fraud',       icon: <Shield size={15} /> },
    { id: 'database',  label: 'Database',    icon: <Database size={15} /> },
  ]

  return (
    <Layout>
      <PageHeader
        title="Admin Panel"
        subtitle="Manage verifications, fraud reports, and platform data."
      />

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
          <StatCard label="Donors"      value={stats.donors}      color="blood"  />
          <StatCard label="Hospitals"   value={stats.hospitals}   color="blue"   />
          <StatCard label="Blood Banks" value={stats.blood_banks} color="green"  />
          <StatCard label="Camps"       value={stats.camps}       color="gold"   />
          <StatCard label="Donations"   value={stats.donations}   color="purple" />
          <StatCard label="Pending"     value={totalPending}      color="blood"  />
        </div>
      )}

      {totalPending > 0 && (
        <Alert type="warning" message={`${totalPending} registration${totalPending > 1 ? 's' : ''} pending review.`} className="mb-6" />
      )}

      <Tabs tabs={TABS} active={tab} onChange={setTab} />
      {tab === 'hospitals' && <PendingHospitals onUpdate={refreshPending} />}
      {tab === 'banks'     && <PendingBanks     onUpdate={refreshPending} />}
      {tab === 'camps'     && <PendingCamps     onUpdate={refreshPending} />}
      {tab === 'fraud'     && <FraudPanel />}
      {tab === 'database'  && <PlatformDB />}
    </Layout>
  )
}
