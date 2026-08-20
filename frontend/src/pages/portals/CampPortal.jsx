import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { CalendarDays, Users, Share2, AlertTriangle, CheckCircle, Phone, Clock, MapPin } from 'lucide-react'
import Layout, { PageHeader } from '../../components/layout/Layout'
import { Tabs } from '../../components/ui/Tabs'
import Button from '../../components/ui/Button'
import { Input, Select } from '../../components/ui/Input'
import Alert from '../../components/ui/Alert'
import { BloodGroupBadge } from '../../components/ui/Badge'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/client'

function CampRegistration({ onDone }) {
  const { register, login } = useAuth()
  const [step,    setStep]    = useState('account')
  const [acct,    setAcct]    = useState({ username:'', password:'', phone:'' })
  const [prof,    setProf]    = useState({ organizer:'', doctor_name:'', city:'', area:'', phone:'', camp_date:'', timings:'' })
  const [cities,  setCities]  = useState([])
  const [areas,   setAreas]   = useState([])
  const [err,     setErr]     = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.get('/ref/cities').then(r => setCities(r.data)) }, [])
  useEffect(() => { if (prof.city) api.get(`/ref/areas/${prof.city}`).then(r => setAreas(r.data)) }, [prof.city])

  const handleAccount = async e => {
    e.preventDefault(); setErr(''); setLoading(true)
    const res = await register(acct.username, acct.password, 'camp', acct.phone)
    if (!res.ok) { setErr(res.message); setLoading(false); return }
    await login(acct.username, acct.password)
    setLoading(false); setStep('profile')
  }

  const handleProfile = async e => {
    e.preventDefault(); setErr(''); setLoading(true)
    try { await api.post('/camp/profile', prof); onDone() }
    catch (ex) { setErr(ex.response?.data?.detail || 'Failed') }
    finally { setLoading(false) }
  }

  if (step === 'account') return (
    <div className="max-w-md mx-auto">
      <h2 className="font-heading font-bold text-2xl text-white text-center mb-6">Register Blood Camp</h2>
      <form onSubmit={handleAccount} className="glass-card p-6 space-y-4">
        <Input label="Username" value={acct.username} onChange={e=>setAcct(a=>({...a,username:e.target.value}))} required />
        <Input label="Password" type="password" value={acct.password} onChange={e=>setAcct(a=>({...a,password:e.target.value}))} required />
        <Input label="Phone" value={acct.phone} onChange={e=>setAcct(a=>({...a,phone:e.target.value}))} maxLength={10} required />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth>Create Account</Button>
      </form>
    </div>
  )

  return (
    <div className="max-w-md mx-auto">
      <h2 className="font-heading font-bold text-2xl text-white text-center mb-6">Camp Details</h2>
      <form onSubmit={handleProfile} className="glass-card p-6 space-y-4">
        <Input label="Organizer Name" value={prof.organizer} onChange={e=>setProf(p=>({...p,organizer:e.target.value}))} required />
        <Input label="Doctor / Coordinator" value={prof.doctor_name} onChange={e=>setProf(p=>({...p,doctor_name:e.target.value}))} />
        <Select label="City" value={prof.city} onChange={e=>setProf(p=>({...p,city:e.target.value}))} required>
          <option value="">Select City</option>
          {cities.map(c=><option key={c}>{c}</option>)}
        </Select>
        <Select label="Area" value={prof.area} onChange={e=>setProf(p=>({...p,area:e.target.value}))} required disabled={!areas.length}>
          <option value="">Select Area</option>
          {areas.map(a=><option key={a}>{a}</option>)}
        </Select>
        <Input label="Phone" value={prof.phone} onChange={e=>setProf(p=>({...p,phone:e.target.value}))} maxLength={10} required />
        <Input type="date" label="Camp Date" value={prof.camp_date}
          min={new Date().toISOString().split('T')[0]}
          onChange={e=>setProf(p=>({...p,camp_date:e.target.value}))} required />
        <Input label="Timings" placeholder="e.g. 9AM – 4PM" value={prof.timings}
          onChange={e=>setProf(p=>({...p,timings:e.target.value}))} />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth>Save Camp Details</Button>
      </form>
    </div>
  )
}

function OverviewTab({ profile }) {
  const isPast = profile?.camp_date < new Date().toISOString().split('T')[0]
  return (
    <div className="max-w-xl">
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-yellow-900/30 flex items-center justify-center flex-shrink-0">
            <CalendarDays size={22} className="text-yellow-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-heading font-bold text-white text-lg">{profile?.organizer}</h3>
            {profile?.doctor_name && <p className="text-xs text-white/50">Dr. {profile.doctor_name}</p>}
          </div>
          {isPast ? <span className="tag-critical">Past</span> : <span className="tag-verified">Active</span>}
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="glass-card p-3 !border-white/5">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Date</p>
            <p className="font-semibold text-white">{profile?.camp_date}</p>
          </div>
          <div className="glass-card p-3 !border-white/5">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Timings</p>
            <p className="font-semibold text-white">{profile?.timings || '—'}</p>
          </div>
          <div className="glass-card p-3 !border-white/5">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Location</p>
            <p className="font-semibold text-white">{profile?.area}, {profile?.city}</p>
          </div>
          <div className="glass-card p-3 !border-white/5">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Phone</p>
            <a href={`tel:${profile?.phone}`} className="font-semibold text-blood-400 hover:text-blood-300">{profile?.phone}</a>
          </div>
        </div>
        {isPast && <Alert type="warning" message="This camp date has passed. Your profile is still active but seekers won't see this camp in search results." />}
      </div>
    </div>
  )
}

function CampSlotsTab() {
  const [slots,   setSlots]   = useState([])
  const [loading, setLoading] = useState(true)
  const [msg,     setMsg]     = useState('')

  useEffect(() => { api.get('/camp/slots').then(r=>setSlots(r.data)).finally(()=>setLoading(false)) }, [])

  const confirm = async id => {
    try { await api.post(`/camp/confirm/${id}`); setSlots(s=>s.filter(sl=>sl.id!==id)); setMsg('Donation confirmed!') }
    catch { setMsg('Failed.') }
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  return (
    <div className="space-y-4">
      {msg && <Alert type={msg.includes('Failed')?'error':'success'} message={msg} onClose={()=>setMsg('')} />}
      {!slots.length
        ? <div className="text-center py-16 text-white/30">No registered donors yet.</div>
        : slots.map(s => (
          <div key={s.id} className="glass-card p-4 flex items-center gap-4">
            <BloodGroupBadge group={s.blood_group} size="sm" />
            <div className="flex-1">
              <p className="font-semibold text-white text-sm">{s.donor_name}</p>
              <p className="text-xs text-white/40">{s.slot_date} · {s.slot_time}</p>
              {s.donor_phone && <a href={`tel:${s.donor_phone}`} className="text-xs text-blood-400 flex items-center gap-1 mt-0.5"><Phone size={11}/>{s.donor_phone}</a>}
            </div>
            <Button size="sm" variant="success" onClick={()=>confirm(s.id)} icon={<CheckCircle size={13}/>}>Mark Done</Button>
          </div>
        ))
      }
    </div>
  )
}

function CampBroadcastTab() {
  const [msg, setMsg] = useState('')
  useEffect(() => { api.get('/camp/wa-message').then(r=>setMsg(r.data.message||'')).catch(()=>{}) }, [])
  const waLink = `https://wa.me/?text=${encodeURIComponent(msg)}`
  return (
    <div className="max-w-xl space-y-4">
      <p className="text-sm text-white/45">Share this announcement to WhatsApp and invite donors to your camp.</p>
      {msg ? (
        <>
          <pre className="wa-box text-xs">{msg}</pre>
          <a href={waLink} target="_blank" rel="noreferrer"
            className="flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white w-full"
            style={{ background:'linear-gradient(135deg,#25D366,#128C7E)' }}>
            <Share2 size={16}/> Share on WhatsApp
          </a>
        </>
      ) : <Alert type="info" message="Save camp details to generate broadcast message." />}
    </div>
  )
}

function CampFraudTab() {
  const [phone,  setPhone]  = useState('')
  const [reason, setReason] = useState('')
  const [msg,    setMsg]    = useState('')
  const [loading,setLoading]= useState(false)

  const submit = async e => {
    e.preventDefault(); setLoading(true)
    try { await api.post('/camp/fraud-report', { reported_phone:phone, reason }); setMsg('success') }
    catch { setMsg('error') }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-md space-y-5">
      <form onSubmit={submit} className="glass-card p-5 space-y-4">
        <Input label="Reported Phone" value={phone} onChange={e=>setPhone(e.target.value)} maxLength={10} required />
        <Select label="Reason" value={reason} onChange={e=>setReason(e.target.value)} required>
          <option value="">Select reason</option>
          <option>Fake blood request</option>
          <option>No-show</option>
          <option>Other</option>
        </Select>
        {msg==='success' && <Alert type="success" message="Report submitted." />}
        {msg==='error'   && <Alert type="error"   message="Failed." />}
        <Button type="submit" loading={loading} variant="danger" icon={<AlertTriangle size={15}/>}>Submit Report</Button>
      </form>
    </div>
  )
}

export default function CampPortal() {
  const { user } = useAuth()
  const navigate  = useNavigate()
  const [tab,     setTab]     = useState('overview')
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    if (user.role !== 'camp' && user.role !== 'admin') { navigate('/'); return }
    api.get('/camp/profile').then(r=>setProfile(r.data)).catch(()=>setProfile(null)).finally(()=>setLoading(false))
  }, [user])

  if (!user) return null
  if (loading) return <Layout><div className="text-center py-20 text-white/30">Loading…</div></Layout>
  if (!profile) return <Layout><CampRegistration onDone={()=>api.get('/camp/profile').then(r=>setProfile(r.data))} /></Layout>

  const TABS = [
    { id:'overview',   label:'Camp Overview', icon:<CalendarDays size={15}/> },
    { id:'slots',      label:'Donor RSVPs',   icon:<Users size={15}/> },
    { id:'broadcast',  label:'Broadcast',     icon:<Share2 size={15}/> },
    { id:'fraud',      label:'Fraud Report',  icon:<AlertTriangle size={15}/> },
  ]

  return (
    <Layout>
      <PageHeader title="Blood Camp Portal" subtitle={profile?.organizer}
        action={profile?.is_verified ? <span className="tag-verified flex items-center gap-1"><CheckCircle size={11}/> Verified</span> : <span className="tag-pending">Pending</span>} />
      {!profile?.is_verified && <Alert type="warning" message="Awaiting admin verification." className="mb-6" />}
      <Tabs tabs={TABS} active={tab} onChange={setTab} />
      {tab==='overview'  && <OverviewTab profile={profile} />}
      {tab==='slots'     && <CampSlotsTab />}
      {tab==='broadcast' && <CampBroadcastTab />}
      {tab==='fraud'     && <CampFraudTab />}
    </Layout>
  )
}
