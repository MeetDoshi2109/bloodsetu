import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Package, Users, Share2, AlertTriangle, CheckCircle, Phone, MapPin } from 'lucide-react'
import Layout, { PageHeader } from '../../components/layout/Layout'
import { Tabs } from '../../components/ui/Tabs'
import Button from '../../components/ui/Button'
import { Input, Select } from '../../components/ui/Input'
import Alert from '../../components/ui/Alert'
import { BloodGroupBadge, StatusBadge } from '../../components/ui/Badge'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/client'

const ALL_GROUPS = ['A+','A-','B+','B-','O+','O-','AB+','AB-']

function ProviderRegistration({ type, onDone }) {
  const { register, login } = useAuth()
  const [step,    setStep]    = useState('account')
  const [acct,    setAcct]    = useState({ username:'', password:'', phone:'' })
  const [prof,    setProf]    = useState({ name:'', doctor_name:'', address:'', city:'', area:'', phone:'', emergency_24x7: false })
  const [cities,  setCities]  = useState([])
  const [areas,   setAreas]   = useState([])
  const [err,     setErr]     = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.get('/ref/cities').then(r => setCities(r.data)) }, [])
  useEffect(() => { if (prof.city) api.get(`/ref/areas/${prof.city}`).then(r => setAreas(r.data)) }, [prof.city])

  const handleAccount = async e => {
    e.preventDefault(); setErr('')
    if (acct.phone.length !== 10) { setErr('Enter a valid 10-digit phone'); return }
    setLoading(true)
    const res = await register(acct.username, acct.password, type, acct.phone)
    if (!res.ok) { setErr(res.message); setLoading(false); return }
    const lr = await login(acct.username, acct.password)
    if (!lr.ok) { setErr('Account created. Please sign in.'); setLoading(false); return }
    setLoading(false); setStep('profile')
  }

  const handleProfile = async e => {
    e.preventDefault(); setErr(''); setLoading(true)
    try { await api.post(`/hospital/profile`, prof); onDone() }
    catch (ex) { setErr(ex.response?.data?.detail || 'Failed') }
    finally { setLoading(false) }
  }

  if (step === 'account') return (
    <div className="max-w-md mx-auto">
      <h2 className="font-heading font-bold text-2xl text-white text-center mb-6">Register Hospital</h2>
      <form onSubmit={handleAccount} className="glass-card p-6 space-y-4">
        <Input label="Username" value={acct.username} onChange={e => setAcct(a => ({...a, username:e.target.value}))} required />
        <Input label="Password" type="password" value={acct.password} onChange={e => setAcct(a => ({...a, password:e.target.value}))} required />
        <Input label="Phone" value={acct.phone} onChange={e => setAcct(a => ({...a, phone:e.target.value}))} maxLength={10} required />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth>Create Account</Button>
      </form>
    </div>
  )

  return (
    <div className="max-w-md mx-auto">
      <h2 className="font-heading font-bold text-2xl text-white text-center mb-6">Hospital Profile</h2>
      <form onSubmit={handleProfile} className="glass-card p-6 space-y-4">
        <Input label="Hospital Name" value={prof.name} onChange={e => setProf(p => ({...p, name:e.target.value}))} required />
        <Input label="Doctor / Contact Name" value={prof.doctor_name} onChange={e => setProf(p => ({...p, doctor_name:e.target.value}))} />
        <Input label="Address" value={prof.address} onChange={e => setProf(p => ({...p, address:e.target.value}))} />
        <Select label="City" value={prof.city} onChange={e => setProf(p => ({...p, city:e.target.value}))} required>
          <option value="">Select City</option>
          {cities.map(c => <option key={c}>{c}</option>)}
        </Select>
        <Select label="Area" value={prof.area} onChange={e => setProf(p => ({...p, area:e.target.value}))} required disabled={!areas.length}>
          <option value="">Select Area</option>
          {areas.map(a => <option key={a}>{a}</option>)}
        </Select>
        <Input label="Phone" value={prof.phone} onChange={e => setProf(p => ({...p, phone:e.target.value}))} maxLength={10} required />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth>Save Profile</Button>
        <p className="text-xs text-white/35 text-center">Your profile will be visible after admin verification.</p>
      </form>
    </div>
  )
}

function InventoryTab({ profile, onRefresh }) {
  const [selected, setSelected] = useState((profile?.blood_available || '').split(',').map(s => s.trim()).filter(Boolean))
  const [msg, setMsg]     = useState('')
  const [loading, setLoading] = useState(false)

  const toggle = g => setSelected(s => s.includes(g) ? s.filter(x => x !== g) : [...s, g])

  const save = async () => {
    setLoading(true)
    try {
      await api.patch('/hospital/inventory', { groups: selected })
      setMsg('success'); onRefresh()
    } catch { setMsg('error') }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-xl space-y-5">
      <div className="glass-card p-5 space-y-4">
        <h3 className="font-semibold text-white">Blood Stock</h3>
        <p className="text-xs text-white/40">Select all blood groups currently available in your inventory.</p>
        <div className="grid grid-cols-4 gap-2">
          {ALL_GROUPS.map(g => (
            <button key={g} onClick={() => toggle(g)}
              className={`py-3 rounded-xl font-heading font-bold text-sm cursor-pointer transition-all duration-200 ${
                selected.includes(g)
                  ? 'bg-gradient-to-br from-blood-700 to-blood-900 text-white shadow-blood'
                  : 'bg-white/5 text-white/40 hover:bg-white/10 hover:text-white/70 border border-white/8'
              }`}>
              {g}
            </button>
          ))}
        </div>
        {msg === 'success' && <Alert type="success" message="Inventory updated successfully." />}
        {msg === 'error'   && <Alert type="error"   message="Failed to update inventory." />}
        <Button onClick={save} loading={loading} icon={<CheckCircle size={15} />}>
          Update Inventory
        </Button>
      </div>
      {profile?.update_due && (
        <Alert type="warning" message={`Inventory update due by ${profile.update_due}. Please update regularly.`} />
      )}
    </div>
  )
}

function SlotsTab({ entityType }) {
  const [slots,   setSlots]   = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  const apiBase = entityType === 'hospital' ? '/hospital' : '/blood-bank'

  useEffect(() => {
    api.get(`${apiBase}/slots`).then(r => setSlots(r.data)).finally(() => setLoading(false))
  }, [])

  const confirm = async id => {
    try {
      await api.post(`${apiBase}/confirm/${id}`)
      setSlots(s => s.filter(sl => sl.id !== id))
      setMsg('Donation confirmed! Donor stats updated.')
    } catch { setMsg('Failed to confirm.') }
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-4">
      {msg && <Alert type={msg.includes('Failed') ? 'error' : 'success'} message={msg} onClose={() => setMsg('')} />}
      {!slots.length ? (
        <div className="text-center py-16 text-white/30">No pending donor slots.</div>
      ) : slots.map(s => (
        <div key={s.id} className="glass-card p-4 flex items-center gap-4">
          <BloodGroupBadge group={s.blood_group} size="sm" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-white text-sm">{s.donor_name}</p>
            <p className="text-xs text-white/40">{s.slot_date} · {s.slot_time}</p>
            {s.donor_phone && <a href={`tel:${s.donor_phone}`} className="text-xs text-blood-400 flex items-center gap-1 mt-0.5"><Phone size={11}/> {s.donor_phone}</a>}
          </div>
          <Button size="sm" variant="success" onClick={() => confirm(s.id)} icon={<CheckCircle size={13} />}>
            Confirm
          </Button>
        </div>
      ))}
    </div>
  )
}

function FindDonorsTab() {
  const [cities, setCities] = useState([])
  const [areas,  setAreas]  = useState([])
  const [form,   setForm]   = useState({ blood_group:'', city:'', area:'' })
  const [donors, setDonors] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  useEffect(() => { api.get('/ref/cities').then(r => setCities(r.data)) }, [])
  useEffect(() => { if (form.city) api.get(`/ref/areas/${form.city}`).then(r => setAreas(r.data)) }, [form.city])

  const search = async e => {
    e.preventDefault(); setLoading(true); setSearched(true)
    try {
      const { data } = await api.get('/hospital/donors', { params: form })
      setDonors(data)
    } catch {} finally { setLoading(false) }
  }

  return (
    <div className="space-y-5">
      <form onSubmit={search} className="glass-card p-5 grid sm:grid-cols-4 gap-4 items-end">
        <Select label="Blood Group" value={form.blood_group} onChange={e => setForm(f => ({...f, blood_group:e.target.value}))} required>
          <option value="">Select</option>
          {ALL_GROUPS.map(g => <option key={g}>{g}</option>)}
        </Select>
        <Select label="City" value={form.city} onChange={e => setForm(f => ({...f, city:e.target.value}))} required>
          <option value="">Select City</option>
          {cities.map(c => <option key={c}>{c}</option>)}
        </Select>
        <Select label="Area" value={form.area} onChange={e => setForm(f => ({...f, area:e.target.value}))} disabled={!areas.length} required>
          <option value="">Select Area</option>
          {areas.map(a => <option key={a}>{a}</option>)}
        </Select>
        <Button type="submit" loading={loading}>Search</Button>
      </form>
      {searched && !loading && (
        donors.length ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {donors.map(d => (
              <div key={d.id} className="glass-card p-4 flex items-center gap-3">
                <BloodGroupBadge group={d.blood_group} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white text-sm">{d.name}</p>
                  <p className="text-xs text-white/40">{d.area} · {d.donations_count} donations</p>
                  <a href={`tel:${d.phone}`} className="text-xs text-blood-400 flex items-center gap-1 mt-0.5"><Phone size={11}/> {d.phone}</a>
                </div>
              </div>
            ))}
          </div>
        ) : <Alert type="info" message="No eligible donors found in this area. Try a wider search." />
      )}
    </div>
  )
}

function BroadcastTab({ apiBase, profile }) {
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api.get(`${apiBase}/wa-message`).then(r => setMsg(r.data.message)).catch(() => {})
  }, [])

  const waLink = `https://wa.me/?text=${encodeURIComponent(msg)}`
  return (
    <div className="max-w-xl space-y-4">
      <p className="text-sm text-white/45">Broadcast a blood drive announcement to your WhatsApp network.</p>
      {msg ? (
        <>
          <pre className="wa-box text-xs">{msg}</pre>
          <a href={waLink} target="_blank" rel="noreferrer"
            className="flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white w-full"
            style={{ background: 'linear-gradient(135deg,#25D366,#128C7E)' }}>
            <Share2 size={16} /> Share on WhatsApp
          </a>
        </>
      ) : <Alert type="info" message="Complete your profile to generate a broadcast message." />}
    </div>
  )
}

function FraudTab({ apiBase }) {
  const [phone,   setPhone]   = useState('')
  const [reason,  setReason]  = useState('')
  const [msg,     setMsg]     = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      await api.post(`${apiBase}/fraud-report`, { reported_phone: phone, reason })
      setMsg('success'); setPhone(''); setReason('')
    } catch { setMsg('error') }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-md space-y-5">
      <Alert type="warning" message="Only report if you have genuine evidence of fraudulent activity." />
      <form onSubmit={submit} className="glass-card p-5 space-y-4">
        <Input label="Reported Phone Number" placeholder="10-digit number" value={phone}
          onChange={e => setPhone(e.target.value)} maxLength={10} required />
        <Select label="Reason" value={reason} onChange={e => setReason(e.target.value)} required>
          <option value="">Select reason</option>
          <option>Fake blood request</option>
          <option>Harassment</option>
          <option>Suspicious activity</option>
          <option>Other</option>
        </Select>
        {msg === 'success' && <Alert type="success" message="Report submitted. Admin will review." />}
        {msg === 'error'   && <Alert type="error"   message="Failed to submit report." />}
        <Button type="submit" loading={loading} variant="danger" icon={<AlertTriangle size={15} />}>
          Submit Report
        </Button>
      </form>
    </div>
  )
}

export default function HospitalPortal() {
  const { user } = useAuth()
  const navigate  = useNavigate()
  const [tab,     setTab]     = useState('inventory')
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    if (user.role !== 'hospital' && user.role !== 'admin') { navigate('/'); return }
    api.get('/hospital/profile')
      .then(r => setProfile(r.data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) return null
  if (loading) return <Layout><div className="text-center py-20 text-white/30">Loading…</div></Layout>
  if (!profile) return <Layout><ProviderRegistration type="hospital" onDone={() => api.get('/hospital/profile').then(r => setProfile(r.data))} /></Layout>

  const isVerified = profile?.is_verified

  const TABS = [
    { id:'inventory', label:'Blood Inventory',  icon:<Package size={15} /> },
    { id:'slots',     label:'Donor Slots',       icon:<Users size={15} /> },
    { id:'donors',    label:'Find Donors',       icon:<Users size={15} /> },
    { id:'broadcast', label:'Broadcast',         icon:<Share2 size={15} /> },
    { id:'fraud',     label:'Fraud Report',      icon:<AlertTriangle size={15} /> },
  ]

  return (
    <Layout>
      <PageHeader
        title="Hospital Portal"
        subtitle={profile?.name}
        action={isVerified
          ? <span className="tag-verified flex items-center gap-1"><CheckCircle size={11} /> Verified</span>
          : <span className="tag-pending">Pending Verification</span>}
      />
      {!isVerified && (
        <Alert type="warning" message="Your hospital is pending admin verification. Full features unlock after approval." className="mb-6" />
      )}
      <Tabs tabs={TABS} active={tab} onChange={setTab} />
      {tab === 'inventory' && <InventoryTab profile={profile} onRefresh={() => api.get('/hospital/profile').then(r => setProfile(r.data))} />}
      {tab === 'slots'     && <SlotsTab entityType="hospital" />}
      {tab === 'donors'    && <FindDonorsTab />}
      {tab === 'broadcast' && <BroadcastTab apiBase="/hospital" profile={profile} />}
      {tab === 'fraud'     && <FraudTab apiBase="/hospital" />}
    </Layout>
  )
}
