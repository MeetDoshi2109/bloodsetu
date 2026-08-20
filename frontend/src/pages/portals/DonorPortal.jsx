import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Heart, Clock, History, AlertTriangle, Trophy, Settings,
  CheckCircle, Phone, Calendar, Droplets, User, Bell
} from 'lucide-react'
import Layout, { PageHeader } from '../../components/layout/Layout'
import { Tabs } from '../../components/ui/Tabs'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { Input, Select, Checkbox } from '../../components/ui/Input'
import Alert from '../../components/ui/Alert'
import { BloodGroupBadge, DonorBadge, StatusBadge } from '../../components/ui/Badge'
import { useAuth } from '../../context/AuthContext'
import { GUJARAT_CITIES, GUJARAT_AREAS, ALL_BLOOD_GROUPS } from '../../data/gujarat'
import api from '../../api/client'

const ALL_BADGES = [
  { id:'first_drop', name:'First Drop Hero',      condition:'First donation',            min_donations:1 },
  { id:'life_saver', name:'Life Saver',            condition:'3 donations',               min_donations:3 },
  { id:'emergency',  name:'Emergency Responder',   condition:'Responded to SOS',          min_donations:1 },
  { id:'fast',       name:'Fast Responder',        condition:'Responded within 1 hour',   min_donations:1 },
  { id:'rare_blood', name:'Rare Blood Hero',       condition:'AB− or O− donor',           min_donations:1 },
  { id:'legend',     name:'Daata Legend',          condition:'5+ donations',              min_donations:5 },
]

const SLOT_TIMES = ['Morning (9AM – 12PM)', 'Afternoon (12PM – 3PM)', 'Evening (3PM – 6PM)']

/* ── Registration ──────────────────────────────── */
function DonorRegistration({ onDone }) {
  const { user, login } = useAuth()
  const [step,  setStep]  = useState(user ? 'profile' : 'account')
  const [acct,  setAcct]  = useState({ username:'', password:'', phone:'' })
  const [prof,  setProf]  = useState({ name:'', blood_group:'', city:'', area:'', phone:'' })
  const [err,   setErr]   = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()

  const profAreas = prof.city ? (GUJARAT_AREAS[prof.city] || []) : []
  const handleProfCity = (city) => setProf(p => ({ ...p, city, area: (GUJARAT_AREAS[city] || [])[0] || '' }))

  const handleAccount = async e => {
    e.preventDefault(); setErr('')
    if (acct.phone.length !== 10 || !/^\d+$/.test(acct.phone)) { setErr('Enter a valid 10-digit phone number'); return }
    setLoading(true)
    const res = await register(acct.username, acct.password, 'donor', acct.phone)
    if (!res.ok) { setErr(res.message); setLoading(false); return }
    const loginRes = await login(acct.username, acct.password)
    if (!loginRes.ok) { setErr('Account created but login failed. Please sign in.'); setLoading(false); return }
    setProf(p => ({ ...p, phone: acct.phone }))
    setLoading(false); setStep('profile')
  }

  const handleProfile = async e => {
    e.preventDefault(); setErr('')
    setLoading(true)
    try {
      await api.post('/donor/profile', prof)
      onDone()
    } catch (ex) {
      setErr(ex.response?.data?.detail || 'Failed to save profile')
    } finally { setLoading(false) }
  }

  if (step === 'account') return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="text-center">
        <Droplets size={40} className="text-blood-400 mx-auto mb-3 heartbeat" />
        <h2 className="font-heading font-bold text-2xl text-white">Become a Donor</h2>
        <p className="text-white/45 text-sm mt-1">You're about to save lives. Welcome to the BloodSetu family. 🩸</p>
      </div>
      <form onSubmit={handleAccount} className="glass-card p-6 space-y-4">
        <Input label="Username" placeholder="Choose a username" value={acct.username}
          onChange={e => setAcct(a => ({...a, username: e.target.value}))} required />
        <Input label="Password" type="password" placeholder="Choose a strong password" value={acct.password}
          onChange={e => setAcct(a => ({...a, password: e.target.value}))} required />
        <Input label="Phone Number" placeholder="10-digit mobile" value={acct.phone}
          onChange={e => setAcct(a => ({...a, phone: e.target.value}))} maxLength={10} required />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth size="lg">Create Account</Button>
        <p className="text-center text-xs text-white/35">Already have an account? <a href="/login" className="text-blood-400 hover:text-blood-300">Sign in</a></p>
      </form>
    </div>
  )

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="text-center">
        <CheckCircle size={36} className="text-emerald-400 mx-auto mb-3" />
        <h2 className="font-heading font-bold text-2xl text-white">Complete Your Profile</h2>
        <p className="text-white/45 text-sm mt-1">This information helps seekers find you in an emergency.</p>
      </div>
      <form onSubmit={handleProfile} className="glass-card p-6 space-y-4">
        <Input label="Full Name" value={prof.name} onChange={e => setProf(p => ({...p, name: e.target.value}))} required />
        <Select label="Blood Group" value={prof.blood_group} onChange={e => setProf(p => ({...p, blood_group: e.target.value}))} required>
          <option value="">Select Blood Group</option>
          {['A+','A-','B+','B-','O+','O-','AB+','AB-'].map(g => <option key={g}>{g}</option>)}
        </Select>
        <Select label="City" value={prof.city} onChange={e => handleProfCity(e.target.value)} required>
          <option value="">Select City</option>
          {GUJARAT_CITIES.map(c => <option key={c}>{c}</option>)}
        </Select>
        <Select label="Area" value={prof.area} onChange={e => setProf(p => ({...p, area: e.target.value}))} required disabled={!profAreas.length}>
          <option value="">Select Area</option>
          {profAreas.map(a => <option key={a}>{a}</option>)}
        </Select>
        <Input label="Phone" value={prof.phone} onChange={e => setProf(p => ({...p, phone: e.target.value}))} maxLength={10} required />
        {err && <Alert type="error" message={err} />}
        <Button type="submit" loading={loading} fullWidth size="lg" icon={<Heart size={16} />}>
          Save Profile & Start Donating
        </Button>
      </form>
    </div>
  )
}

/* ── Eligibility Tab ────────────────────────────── */
function EligibilityTab({ donor, onRefresh }) {
  const [hospitals, setHospitals] = useState([])
  const [banks,     setBanks]     = useState([])
  const [camps,     setCamps]     = useState([])
  const [slotForm,  setSlotForm]  = useState({ location_type: 'Hospital', location_id: '', slot_date: '', slot_time: SLOT_TIMES[0] })
  const [msg,       setMsg]       = useState('')
  const [loading,   setLoading]   = useState(false)

  useEffect(() => {
    if (donor?.city) {
      api.get('/hospitals',   { params: { city: donor.city } }).then(r => setHospitals(r.data)).catch(() => {})
      api.get('/blood-banks', { params: { city: donor.city } }).then(r => setBanks(r.data)).catch(() => {})
      api.get('/camps',       { params: { city: donor.city } }).then(r => setCamps(r.data)).catch(() => {})
    }
  }, [donor])

  const locations = slotForm.location_type === 'Hospital' ? hospitals
    : slotForm.location_type === 'Blood Bank' ? banks : camps

  const bookSlot = async e => {
    e.preventDefault(); setMsg('')
    setLoading(true)
    try {
      await api.post('/donor/slots', slotForm)
      setMsg('success')
      onRefresh()
    } catch (ex) {
      setMsg(ex.response?.data?.detail || 'Failed to book slot')
    } finally { setLoading(false) }
  }

  const progress = Math.round((donor?.progress || 0) * 100)

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="space-y-5">
        {/* Status card */}
        <div className="glass-card p-6 space-y-4"
          style={{ borderColor: donor?.is_eligible ? 'rgba(46,204,113,0.4)' : 'rgba(231,76,60,0.35)' }}>
          <div className="flex items-center gap-4">
            <BloodGroupBadge group={donor?.blood_group || 'O+'} size="lg" />
            <div>
              <p className="font-heading font-black text-2xl text-white">
                {donor?.is_eligible ? 'Ready to Donate!' : 'Not Yet Eligible'}
              </p>
              <p className="text-sm text-white/50 mt-0.5">
                {donor?.is_eligible
                  ? 'Your blood is needed. Book a slot today.'
                  : `${donor?.days_remaining ?? 0} more days until eligible`}
              </p>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-white/40">
              <span>Recovery progress</span>
              <span>{progress}%</span>
            </div>
            <div className="progress-wrap">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="glass-card p-3 !border-white/5">
              <p className="text-2xl font-heading font-black text-blood-400">{donor?.donations_count || 0}</p>
              <p className="text-xs text-white/40 mt-0.5">Total Donations</p>
            </div>
            <div className="glass-card p-3 !border-white/5">
              <p className="text-2xl font-heading font-black text-emerald-400">{(donor?.donations_count || 0) * 3}</p>
              <p className="text-xs text-white/40 mt-0.5">Lives Saved</p>
            </div>
          </div>
        </div>

        {/* Quick status toggle */}
        <div className="glass-card p-4">
          <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Availability Status</p>
          <div className="flex gap-2">
            {['Available','Unavailable'].map(s => (
              <button key={s}
                onClick={() => api.patch('/donor/status', null, { params: { status_val: s } }).then(onRefresh)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-semibold cursor-pointer transition-all duration-200 ${
                  donor?.status === s
                    ? s === 'Available' ? 'bg-emerald-700/30 text-emerald-300 border border-emerald-600/40' : 'bg-red-900/30 text-red-300 border border-red-700/40'
                    : 'bg-white/5 text-white/40 hover:text-white/70 border border-white/5'
                }`}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Slot booking */}
      {donor?.is_eligible && (
        <form onSubmit={bookSlot} className="glass-card p-6 space-y-4">
          <h3 className="font-heading font-bold text-white">Book a Donation Slot</h3>
          <Select label="Location Type" value={slotForm.location_type}
            onChange={e => setSlotForm(f => ({...f, location_type: e.target.value, location_id: ''}))}>
            {['Hospital','Blood Bank','Blood Camp'].map(t => <option key={t}>{t}</option>)}
          </Select>
          <Select label="Location" value={slotForm.location_id}
            onChange={e => setSlotForm(f => ({...f, location_id: Number(e.target.value)}))} required>
            <option value="">Select location</option>
            {locations.map(l => <option key={l.id} value={l.id}>{l.name || l.organizer}</option>)}
          </Select>
          <Input type="date" label="Date" value={slotForm.slot_date}
            min={new Date().toISOString().split('T')[0]}
            onChange={e => setSlotForm(f => ({...f, slot_date: e.target.value}))} required />
          <Select label="Time Slot" value={slotForm.slot_time}
            onChange={e => setSlotForm(f => ({...f, slot_time: e.target.value}))}>
            {SLOT_TIMES.map(t => <option key={t}>{t}</option>)}
          </Select>
          {msg === 'success' && <Alert type="success" message="Slot booked! Someone will live because you showed up. ❤️" />}
          {msg && msg !== 'success' && <Alert type="error" message={msg} />}
          <Button type="submit" loading={loading} fullWidth icon={<Calendar size={15} />}>
            Confirm Booking
          </Button>
        </form>
      )}
    </div>
  )
}

/* ── Slots Tab ──────────────────────────────────── */
function SlotsTab({ onRefresh }) {
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/donor/slots').then(r => setSlots(r.data)).finally(() => setLoading(false))
  }, [])

  const cancel = async id => {
    await api.delete(`/donor/slots/${id}`)
    setSlots(s => s.map(sl => sl.id === id ? {...sl, status:'Cancelled'} : sl))
    onRefresh()
  }

  if (loading) return <div className="text-center py-12 text-white/30">Loading slots…</div>
  if (!slots.length) return (
    <div className="text-center py-16 space-y-3">
      <Calendar size={40} className="text-white/15 mx-auto" />
      <p className="text-white/40">No slots booked yet.</p>
      <p className="text-white/25 text-sm">Book a slot from the Eligibility tab when you're ready to donate.</p>
    </div>
  )

  return (
    <div className="space-y-3">
      {slots.map(s => (
        <div key={s.id} className="glass-card p-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-blood-900/40 flex items-center justify-center flex-shrink-0">
            <Calendar size={18} className="text-blood-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-white text-sm">{s.location_name || s.location_type}</p>
            <p className="text-xs text-white/40 mt-0.5">{s.slot_date} · {s.slot_time}</p>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={s.status} />
            {s.status === 'Pending' && (
              <button onClick={() => cancel(s.id)}
                className="text-xs text-red-400 hover:text-red-300 cursor-pointer px-2 py-1 rounded hover:bg-red-950/20 transition-colors">
                Cancel
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ── History Tab ────────────────────────────────── */
function HistoryTab() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/donor/history').then(r => setHistory(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-white/30">Loading history…</div>
  if (!history.length) return (
    <div className="text-center py-16 space-y-3">
      <History size={40} className="text-white/15 mx-auto" />
      <p className="text-white/40">No donations recorded yet.</p>
    </div>
  )

  return (
    <div className="space-y-3">
      {history.map((d, i) => (
        <div key={d.id} className="glass-card p-4 flex items-center gap-4 slide-in" style={{ animationDelay: `${i * 60}ms` }}>
          <div className="w-10 h-10 rounded-xl bg-emerald-900/30 flex items-center justify-center flex-shrink-0">
            <CheckCircle size={18} className="text-emerald-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-white text-sm">{d.location_name || d.confirmed_by_type}</p>
            <p className="text-xs text-white/40 mt-0.5">Donated on {d.donation_date}</p>
            <p className="text-xs text-blood-400 mt-0.5">Next eligible: {d.next_eligible}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="font-heading font-black text-lg text-emerald-400">×3</p>
            <p className="text-[10px] text-white/30">lives saved</p>
          </div>
        </div>
      ))}
    </div>
  )
}

/* ── SOS Near Me Tab ────────────────────────────── */
function SOSNearMeTab({ donor }) {
  const [sos, setSos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (donor?.city) {
      api.get(`/sos/city/${donor.city}`).then(r => setSos(r.data)).finally(() => setLoading(false))
    } else setLoading(false)
  }, [donor])

  if (!donor?.is_eligible) return (
    <div className="text-center py-16 space-y-3">
      <Clock size={40} className="text-white/15 mx-auto" />
      <p className="text-white/40">You'll see active emergencies once you're eligible to donate.</p>
    </div>
  )
  if (loading) return <div className="text-center py-12 text-white/30">Loading…</div>
  if (!sos.length) return (
    <div className="text-center py-16 space-y-3">
      <Bell size={40} className="text-white/15 mx-auto" />
      <p className="text-white/40">No active SOS requests in {donor.city} right now.</p>
      <p className="text-white/25 text-sm">That's a good sign. Check back soon.</p>
    </div>
  )

  return (
    <div className="space-y-3">
      {sos.map(s => (
        <div key={s.id} className="glass-card p-4 border-l-4"
          style={{ borderLeftColor: s.urgency === 'Critical' ? '#e74c3c' : '#f0c040' }}>
          <div className="flex items-center gap-4">
            <BloodGroupBadge group={s.blood_group} size="md" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className={s.urgency === 'Critical' ? 'tag-critical' : 'tag-pending'}>{s.urgency}</span>
                <span className="text-xs text-white/40">{s.area}, {s.city}</span>
              </div>
              {s.seeker_name && <p className="text-xs text-white/50">Seeker: {s.seeker_name}</p>}
              <p className="text-xs text-white/30 mt-0.5">Posted {new Date(s.posted_at).toLocaleString()}</p>
            </div>
            {s.seeker_phone && (
              <a href={`tel:${s.seeker_phone}`}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-white cursor-pointer flex-shrink-0"
                style={{ background: 'linear-gradient(135deg,#c0392b,#7b241c)' }}>
                <Phone size={13} /> Respond
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ── Badges Tab ─────────────────────────────────── */
function BadgesTab({ donor }) {
  const earned = donor?.badges?.map(b => b.id) || []
  const rare = ['AB-','O-'].includes(donor?.blood_group)
  return (
    <div className="space-y-5">
      <p className="text-sm text-white/45">
        You've earned <span className="text-white font-bold">{earned.length}</span> of {ALL_BADGES.length} badges.
        Keep donating to unlock more recognition!
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {ALL_BADGES.map(b => {
          const isEarned = earned.includes(b.id) ||
            (b.id === 'rare_blood' && rare && (donor?.donations_count || 0) >= 1)
          return <DonorBadge key={b.id} badge={b} earned={isEarned} />
        })}
      </div>
      {earned.length > 0 && (
        <div className="glass-card p-4 text-center" style={{ borderColor: 'rgba(240,192,64,0.3)' }}>
          <p className="text-sm text-yellow-300 font-semibold">You gave someone their tomorrow. Thank you for being you. ❤️</p>
        </div>
      )}
    </div>
  )
}

/* ── Settings Tab ───────────────────────────────── */
function SettingsTab({ donor, onRefresh }) {
  const [daataWall, setDaataWall] = useState(donor?.daata_wall_opt === 1)
  const [waMsg,     setWaMsg]     = useState('')
  const [saved,     setSaved]     = useState(false)

  const saveSettings = async () => {
    await api.patch('/donor/daata-wall', null, { params: { opt_in: daataWall } })
    setSaved(true); setTimeout(() => setSaved(false), 2000)
    onRefresh()
  }

  useEffect(() => {
    api.get('/donor/wa-message').then(r => setWaMsg(r.data.message)).catch(() => {})
  }, [])

  const waLink = `https://wa.me/?text=${encodeURIComponent(waMsg)}`

  return (
    <div className="space-y-6 max-w-xl">
      <div className="glass-card p-5 space-y-4">
        <h3 className="font-semibold text-white">Daata Wall</h3>
        <p className="text-xs text-white/45 leading-relaxed">
          The Daata Wall of Honor publicly celebrates top donors. Enabling this shows your name, blood group, city, and donation count on the public leaderboard.
        </p>
        <Checkbox
          label="Show me on the Daata Wall of Honor"
          checked={daataWall}
          onChange={e => setDaataWall(e.target.checked)}
        />
        <Button onClick={saveSettings} icon={saved ? <CheckCircle size={14} /> : null}>
          {saved ? 'Saved!' : 'Save Settings'}
        </Button>
      </div>

      {waMsg && (
        <div className="glass-card p-5 space-y-3">
          <h3 className="font-semibold text-white">Spread Awareness</h3>
          <p className="text-xs text-white/45">Share this message to encourage others to donate.</p>
          <pre className="wa-box text-xs">{waMsg}</pre>
          <a href={waLink} target="_blank" rel="noreferrer"
            className="flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-bold text-white"
            style={{ background: 'linear-gradient(135deg,#25D366,#128C7E)' }}>
            Share on WhatsApp
          </a>
        </div>
      )}
    </div>
  )
}

/* ── Main Portal ────────────────────────────────── */
export default function DonorPortal() {
  const { user, donor, refreshDonor } = useAuth()
  const navigate = useNavigate()
  const [tab,     setTab]     = useState('eligibility')
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) { navigate('/login', { state: { role: 'donor' } }); return }
    if (user.role !== 'donor' && user.role !== 'admin') { navigate('/'); return }
    api.get('/donor/profile')
      .then(r => setProfile(r.data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false))
  }, [user])

  const handleDone = () => {
    api.get('/donor/profile').then(r => setProfile(r.data)).catch(() => {})
    refreshDonor()
  }

  if (!user) return null
  if (loading) return <Layout><div className="text-center py-20 text-white/30">Loading…</div></Layout>
  if (!profile) return <Layout><DonorRegistration onDone={handleDone} /></Layout>

  const TABS = [
    { id:'eligibility', label:'Eligibility', icon:<Heart size={15} /> },
    { id:'slots',       label:'My Slots',    icon:<Calendar size={15} /> },
    { id:'history',     label:'History',     icon:<History size={15} /> },
    { id:'sos',         label:'SOS Near Me', icon:<AlertTriangle size={15} /> },
    { id:'badges',      label:'Badges',      icon:<Trophy size={15} /> },
    { id:'settings',    label:'Settings',    icon:<Settings size={15} /> },
  ]

  return (
    <Layout>
      <PageHeader
        title="Donor Portal"
        subtitle={`Welcome back, ${profile.name}. Your blood can save ${(profile.donations_count||0)*3 + 3} more lives.`}
      />
      <Tabs tabs={TABS} active={tab} onChange={setTab} />
      {tab === 'eligibility' && <EligibilityTab donor={profile} onRefresh={handleDone} />}
      {tab === 'slots'       && <SlotsTab onRefresh={handleDone} />}
      {tab === 'history'     && <HistoryTab />}
      {tab === 'sos'         && <SOSNearMeTab donor={profile} />}
      {tab === 'badges'      && <BadgesTab donor={profile} />}
      {tab === 'settings'    && <SettingsTab donor={profile} onRefresh={handleDone} />}
    </Layout>
  )
}
