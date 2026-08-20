import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Search, Building2, Droplets, CalendarDays, Users,
  Phone, MapPin, Clock, CheckCircle, AlertTriangle, Share2, ChevronDown, ChevronUp
} from 'lucide-react'
import Layout, { PageHeader } from '../components/layout/Layout'
import Button from '../components/ui/Button'
import { BloodGroupBadge } from '../components/ui/Badge'
import Alert from '../components/ui/Alert'
import { Input, Select } from '../components/ui/Input'
import MapView, { MapLegend } from '../components/shared/MapView'
import api from '../api/client'

const BLOOD_GROUPS = ['A+','A-','B+','B-','O+','O-','AB+','AB-']

function TierLabel({ tier }) {
  const map = {
    T1: { label: 'Hospital',    color: '#3b82f6', bg: 'rgba(59,130,246,0.12)' },
    T2: { label: 'Blood Bank',  color: '#2ecc71', bg: 'rgba(46,204,113,0.12)' },
    T3: { label: 'Blood Camp',  color: '#f0c040', bg: 'rgba(240,192,64,0.12)' },
    T4: { label: 'Community Donor', color: '#e74c3c', bg: 'rgba(231,76,60,0.12)' },
  }
  const t = map[tier] || map.T1
  return (
    <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ color: t.color, background: t.bg, border: `1px solid ${t.color}30` }}>
      {t.label}
    </span>
  )
}

function HospitalCard({ h, revealed }) {
  return (
    <div className="result-card slide-in">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <TierLabel tier="T1" />
            {h.emergency_24x7 ? <span className="tag-critical text-[10px]">24×7 Emergency</span> : null}
            <span className="tag-verified">Verified</span>
          </div>
          <h3 className="font-heading font-bold text-white text-base">{h.name}</h3>
          {h.doctor_name && <p className="text-xs text-white/50 mt-0.5">Dr. {h.doctor_name}</p>}
          <p className="text-xs text-white/35 flex items-center gap-1 mt-1">
            <MapPin size={11} /> {h.address || `${h.area}, ${h.city}`}
          </p>
        </div>
        <Building2 size={28} className="text-blue-400 flex-shrink-0 opacity-60" />
      </div>
      {h.blood_available && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {h.blood_available.split(',').map(g => (
            <BloodGroupBadge key={g} group={g.trim()} size="sm" />
          ))}
        </div>
      )}
      {revealed && (
        <a
          href={`tel:${h.phone}`}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white cursor-pointer transition-all w-full justify-center"
          style={{ background: 'linear-gradient(135deg,#3b82f6,#1d4ed8)' }}
        >
          <Phone size={15} /> {h.phone}
        </a>
      )}
    </div>
  )
}

function BloodBankCard({ b, revealed }) {
  return (
    <div className="result-card slide-in" style={{ borderLeftColor: '#2ecc71' }}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <TierLabel tier="T2" />
            <span className="tag-verified">Verified</span>
          </div>
          <h3 className="font-heading font-bold text-white text-base">{b.name}</h3>
          {b.doctor_name && <p className="text-xs text-white/50 mt-0.5">Dr. {b.doctor_name}</p>}
          <p className="text-xs text-white/35 flex items-center gap-1 mt-1">
            <MapPin size={11} /> {b.area}, {b.city}
          </p>
        </div>
        <Droplets size={28} className="text-emerald-400 flex-shrink-0 opacity-60" />
      </div>
      {b.groups_available && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {b.groups_available.split(',').map(g => (
            <BloodGroupBadge key={g} group={g.trim()} size="sm" />
          ))}
        </div>
      )}
      {revealed && (
        <a
          href={`tel:${b.phone}`}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white cursor-pointer transition-all w-full justify-center"
          style={{ background: 'linear-gradient(135deg,#2ecc71,#16a34a)' }}
        >
          <Phone size={15} /> {b.phone}
        </a>
      )}
    </div>
  )
}

function CampCard({ c, revealed }) {
  return (
    <div className="result-card slide-in" style={{ borderLeftColor: '#f0c040' }}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <TierLabel tier="T3" />
          </div>
          <h3 className="font-heading font-bold text-white text-base">{c.organizer}</h3>
          {c.doctor_name && <p className="text-xs text-white/50 mt-0.5">Dr. {c.doctor_name}</p>}
          <p className="text-xs text-white/35 flex items-center gap-1 mt-1">
            <MapPin size={11} /> {c.area}, {c.city}
          </p>
        </div>
        <CalendarDays size={28} className="text-yellow-400 flex-shrink-0 opacity-60" />
      </div>
      <div className="flex gap-3 text-xs text-white/50 mb-3">
        <span className="flex items-center gap-1"><CalendarDays size={11} /> {c.camp_date}</span>
        {c.timings && <span className="flex items-center gap-1"><Clock size={11} /> {c.timings}</span>}
      </div>
      {revealed && (
        <a
          href={`tel:${c.phone}`}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white cursor-pointer transition-all w-full justify-center"
          style={{ background: 'linear-gradient(135deg,#f0c040,#d97706)' }}
        >
          <Phone size={15} /> {c.phone}
        </a>
      )}
    </div>
  )
}

function DonorCard({ d, revealed }) {
  return (
    <div className="result-card slide-in">
      <div className="flex items-center gap-4">
        <BloodGroupBadge group={d.blood_group} size="md" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <TierLabel tier="T4" />
          </div>
          <h3 className="font-semibold text-white text-sm">{d.name}</h3>
          <p className="text-xs text-white/40">{d.area} · {d.donations_count} donations</p>
        </div>
        {revealed && (
          <a
            href={`tel:${d.phone}`}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-white cursor-pointer flex-shrink-0"
            style={{ background: 'linear-gradient(135deg,#c0392b,#7b241c)' }}
          >
            <Phone size={13} /> Call
          </a>
        )}
      </div>
    </div>
  )
}

function SOSMessage({ msg }) {
  const [copied, setCopied] = useState(false)
  const waLink = `https://wa.me/?text=${encodeURIComponent(msg)}`
  const copy = () => {
    navigator.clipboard.writeText(msg)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div className="space-y-4">
      <Alert type="warning" message="No matching results found nearby. Share this emergency SOS to your WhatsApp network." />
      <pre className="wa-box text-xs">{msg}</pre>
      <div className="flex gap-3">
        <a href={waLink} target="_blank" rel="noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white"
          style={{ background: 'linear-gradient(135deg,#25D366,#128C7E)' }}>
          <Share2 size={16} /> Share on WhatsApp
        </a>
        <Button variant="secondary" onClick={copy} className="flex-1">
          {copied ? <CheckCircle size={15} className="text-emerald-400" /> : null}
          {copied ? 'Copied!' : 'Copy Message'}
        </Button>
      </div>
    </div>
  )
}

export default function FindBlood() {
  const location = useLocation()
  const init     = location.state || {}

  const [cities,  setCities]  = useState([])
  const [areas,   setAreas]   = useState([])
  const [form,    setForm]    = useState({
    blood_group: init.blood_group || '',
    city:        init.city        || '',
    area:        init.area        || '',
    urgency:     init.urgency     || 'Urgent',
  })

  const [loading,  setLoading]  = useState(false)
  const [results,  setResults]  = useState(null)
  const [revealed, setRevealed] = useState(false)
  const [seeker,   setSeeker]   = useState({ name: '', phone: '', area: '' })
  const [sosMsg,   setSosMsg]   = useState('')
  const [error,    setError]    = useState('')
  const [showMap,  setShowMap]  = useState(false)

  useEffect(() => {
    api.get('/ref/cities').then(r => setCities(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (form.city) {
      api.get(`/ref/areas/${form.city}`)
        .then(r => { setAreas(r.data); if (!form.area) setForm(f => ({ ...f, area: r.data[0] || '' })) })
        .catch(() => {})
    }
  }, [form.city])

  // Auto-search if navigated with state
  useEffect(() => {
    if (init.blood_group && init.city && init.area) handleSearch(null, init)
  }, [])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSearch = async (e, overrides) => {
    e?.preventDefault()
    const q = overrides || form
    if (!q.blood_group || !q.city || !q.area) return
    setLoading(true)
    setResults(null)
    setRevealed(false)
    setSosMsg('')
    setError('')
    try {
      const { data } = await api.get('/search', { params: { blood_group: q.blood_group, city: q.city, area: q.area } })
      setResults(data)
      if (data.found_at === 'T5') {
        const m = `🚨 URGENT BLOOD NEEDED 🚨\n\nBlood Group: ${q.blood_group}\nLocation: ${q.area}, ${q.city}\n\nPlease contact: [Your Number]\n\nEvery second counts. Share this. 🩸\n— BloodSetu`
        setSosMsg(m)
      }
    } catch {
      setError('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReveal = async (e) => {
    e.preventDefault()
    if (!seeker.name || !seeker.phone || seeker.phone.length !== 10) {
      setError('Please enter a valid name and 10-digit phone number.')
      return
    }
    // Post SOS + reveal
    try {
      await api.post('/sos', {
        blood_group: form.blood_group, city: form.city, area: seeker.area || form.area,
        seeker_name: seeker.name, seeker_phone: seeker.phone, urgency: form.urgency,
      })
    } catch {}
    setRevealed(true)
    setError('')
  }

  const hasResults = results && results.found_at !== 'T5'
  const allItems = [
    ...(results?.T1_hospitals || []),
    ...(results?.T2_banks     || []),
    ...(results?.T3_camps     || []),
    ...(results?.T4_donors    || []),
  ]

  return (
    <Layout>
      <PageHeader
        title="Find Blood"
        subtitle="AI-powered 5-tier search across Gujarat — hospitals, blood banks, camps, and community donors."
      />

      {/* Search form */}
      <div className="glass-card p-6 mb-8">
        <form onSubmit={handleSearch} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <Select label="Blood Group" value={form.blood_group} onChange={e => set('blood_group', e.target.value)} required>
            <option value="">Select</option>
            {BLOOD_GROUPS.map(g => <option key={g}>{g}</option>)}
          </Select>
          <Select label="City" value={form.city} onChange={e => set('city', e.target.value)} required>
            <option value="">Select City</option>
            {cities.map(c => <option key={c}>{c}</option>)}
          </Select>
          <Select label="Area" value={form.area} onChange={e => set('area', e.target.value)} required disabled={!areas.length}>
            <option value="">Select Area</option>
            {areas.map(a => <option key={a}>{a}</option>)}
          </Select>
          <Select label="Urgency" value={form.urgency} onChange={e => set('urgency', e.target.value)}>
            {['Planned','Urgent','Critical'].map(u => <option key={u}>{u}</option>)}
          </Select>
          <Button type="submit" loading={loading} icon={<Search size={16} />} fullWidth>
            {loading ? 'Searching…' : 'Search'}
          </Button>
        </form>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError('')} className="mb-6" />}

      {/* Loading state */}
      {loading && (
        <div className="text-center py-16 space-y-4">
          <div className="w-12 h-12 border-2 border-blood-700/30 border-t-blood-500 rounded-full animate-spin mx-auto" />
          <p className="text-white/50 text-sm">Scanning hospitals, blood banks, camps, and donors…</p>
          <p className="text-white/25 text-xs">Hang on, we're finding hope for you. 🩸</p>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="space-y-8">
          {/* Summary bar */}
          <div className="glass-card p-4 flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-3">
              <BloodGroupBadge group={form.blood_group} size="md" />
              <div>
                <p className="font-bold text-white text-sm">{form.blood_group} · {form.area}, {form.city}</p>
                <p className="text-xs text-white/40">
                  {hasResults
                    ? `Found at Tier ${results.found_at?.replace('T','')} · ${allItems.length} result${allItems.length !== 1 ? 's' : ''}`
                    : 'No results found nearby'}
                </p>
              </div>
            </div>
            {hasResults && (
              <div className="ml-auto">
                <span className="tag-verified flex items-center gap-1">
                  <CheckCircle size={11} /> Blood Found
                </span>
              </div>
            )}
          </div>

          {/* Seeker verification gate */}
          {hasResults && !revealed && (
            <div className="glass-card p-6 space-y-4" style={{ borderColor: 'rgba(240,192,64,0.35)' }}>
              <div className="flex items-start gap-3">
                <AlertTriangle size={20} className="text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-white mb-1">One last step — verify your request</h3>
                  <p className="text-sm text-white/50">
                    Enter your details to unlock contact numbers. This posts an active SOS so donors nearby can also find and reach you.
                  </p>
                </div>
              </div>
              <form onSubmit={handleReveal} className="grid sm:grid-cols-3 gap-4">
                <Input label="Your Name" placeholder="Full name" value={seeker.name}
                  onChange={e => setSeeker(s => ({...s, name: e.target.value}))} required />
                <Input label="Phone Number" placeholder="10-digit mobile" value={seeker.phone}
                  onChange={e => setSeeker(s => ({...s, phone: e.target.value}))} maxLength={10} required />
                <div className="flex items-end">
                  <Button type="submit" variant="success" fullWidth icon={<Phone size={15} />}>
                    Unlock Contacts
                  </Button>
                </div>
              </form>
            </div>
          )}

          {revealed && (
            <Alert type="success" message="Contacts unlocked. An SOS has been posted. Please reach out kindly — every donor is a volunteer. ❤️" />
          )}

          {/* T1 Hospitals */}
          {results.T1_hospitals?.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-3 flex items-center gap-2">
                <Building2 size={14} className="text-blue-400" /> Hospitals ({results.T1_hospitals.length})
              </h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.T1_hospitals.map(h => <HospitalCard key={h.id} h={h} revealed={revealed} />)}
              </div>
            </section>
          )}

          {/* T2 Blood Banks */}
          {results.T2_banks?.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-3 flex items-center gap-2">
                <Droplets size={14} className="text-emerald-400" /> Blood Banks ({results.T2_banks.length})
              </h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.T2_banks.map(b => <BloodBankCard key={b.id} b={b} revealed={revealed} />)}
              </div>
            </section>
          )}

          {/* T3 Camps */}
          {results.T3_camps?.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-3 flex items-center gap-2">
                <CalendarDays size={14} className="text-yellow-400" /> Blood Camps ({results.T3_camps.length})
              </h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.T3_camps.map(c => <CampCard key={c.id} c={c} revealed={revealed} />)}
              </div>
            </section>
          )}

          {/* T4 Donors */}
          {results.T4_donors?.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-3 flex items-center gap-2">
                <Users size={14} className="text-blood-400" /> Community Donors — AI Ranked ({results.T4_donors.length})
              </h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {results.T4_donors.map(d => <DonorCard key={d.id} d={d} revealed={revealed} />)}
              </div>
            </section>
          )}

          {/* T5 SOS */}
          {results.found_at === 'T5' && sosMsg && <SOSMessage msg={sosMsg} />}

          {/* Map toggle */}
          {hasResults && (
            <section>
              <button
                className="flex items-center gap-2 text-sm text-white/50 hover:text-white transition-colors cursor-pointer mb-3"
                onClick={() => setShowMap(m => !m)}
              >
                <MapPin size={15} />
                {showMap ? 'Hide' : 'Show'} map
                {showMap ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              {showMap && (
                <>
                  <MapView
                    city={form.city}
                    hospitals={results.T1_hospitals || []}
                    banks={results.T2_banks || []}
                    camps={results.T3_camps || []}
                    donors={results.T4_donors || []}
                    height={420}
                  />
                  <MapLegend />
                </>
              )}
            </section>
          )}
        </div>
      )}
    </Layout>
  )
}
