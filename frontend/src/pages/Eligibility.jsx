import { useState } from 'react'
import { CheckCircle, XCircle, Calendar, Heart, Shield, Droplets, Info } from 'lucide-react'
import Layout, { PageHeader } from '../components/layout/Layout'
import Button from '../components/ui/Button'
import { Checkbox } from '../components/ui/Input'
import Card from '../components/ui/Card'

function calcEligibility(lastDonated, isFirstTime) {
  if (isFirstTime || !lastDonated) return { eligible: true, daysSince: null, daysLeft: 0, progress: 1 }
  const last = new Date(lastDonated)
  const today = new Date()
  const daysSince = Math.floor((today - last) / 86400000)
  const daysLeft = Math.max(0, 90 - daysSince)
  return { eligible: daysSince >= 90, daysSince, daysLeft, progress: Math.min(1, daysSince / 90) }
}

const CRITERIA = [
  { icon: <Calendar size={18} />, label: 'Age', value: '18 – 65 years', ok: true },
  { icon: <Shield size={18} />,   label: 'Weight', value: 'At least 45 kg', ok: true },
  { icon: <Heart size={18} />,    label: 'Haemoglobin', value: 'Min 12.5 g/dL', ok: true },
  { icon: <Droplets size={18} />, label: 'Interval', value: '90 days between donations', ok: true },
]

export default function Eligibility() {
  const [firstTime, setFirstTime] = useState(false)
  const [lastDate,  setLastDate]  = useState('')
  const [checked,   setChecked]   = useState(false)

  const result = checked ? calcEligibility(lastDate, firstTime) : null

  const formatDate = (d) => new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' })
  const nextEligible = lastDate ? new Date(new Date(lastDate).getTime() + 90 * 86400000) : null

  return (
    <Layout>
      <PageHeader
        title="Eligibility Check"
        subtitle="Find out if you're ready to donate blood based on WHO guidelines."
      />

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left — checker */}
        <div className="space-y-6">
          <Card>
            <h2 className="font-heading font-bold text-white mb-5">Check Your Eligibility</h2>
            <div className="space-y-5">
              <Checkbox
                label="I am donating for the first time"
                checked={firstTime}
                onChange={e => { setFirstTime(e.target.checked); setLastDate(''); setChecked(false) }}
              />
              {!firstTime && (
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-white/60 uppercase tracking-wider block">
                    Last Donation Date
                  </label>
                  <input
                    type="date"
                    value={lastDate}
                    onChange={e => { setLastDate(e.target.value); setChecked(false) }}
                    max={new Date().toISOString().split('T')[0]}
                    className="bs-input"
                  />
                </div>
              )}
              <Button
                fullWidth
                onClick={() => setChecked(true)}
                disabled={!firstTime && !lastDate}
                icon={<CheckCircle size={16} />}
              >
                Check Now
              </Button>
            </div>
          </Card>

          {/* Result */}
          {result && (
            <div
              className="glass-card p-6 slide-in space-y-5"
              style={{ borderColor: result.eligible ? 'rgba(46,204,113,0.4)' : 'rgba(231,76,60,0.4)' }}
            >
              <div className="flex items-center gap-4">
                {result.eligible
                  ? <CheckCircle size={36} className="text-emerald-400 flex-shrink-0" />
                  : <XCircle    size={36} className="text-blood-400 flex-shrink-0" />
                }
                <div>
                  <p className="font-heading font-black text-xl text-white">
                    {result.eligible ? 'You are eligible!' : 'Not yet eligible'}
                  </p>
                  <p className="text-sm text-white/50 mt-0.5">
                    {result.eligible
                      ? "Your body is ready. One donation saves up to 3 lives. 🩸"
                      : `${result.daysLeft} more day${result.daysLeft !== 1 ? 's' : ''} to go.`}
                  </p>
                </div>
              </div>

              {/* Progress bar */}
              {result.daysSince !== null && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-white/40">
                    <span>Day 0</span>
                    <span>{result.daysSince} / 90 days</span>
                    <span>Day 90</span>
                  </div>
                  <div className="progress-wrap">
                    <div className="progress-fill" style={{ width: `${result.progress * 100}%` }} />
                  </div>
                  {nextEligible && (
                    <p className="text-xs text-white/40 text-right">
                      Next eligible: <span className="text-white/70 font-semibold">{formatDate(nextEligible)}</span>
                    </p>
                  )}
                </div>
              )}

              {result.eligible && (
                <Button fullWidth variant="success" icon={<Heart size={16} />}
                  onClick={() => window.location.href = '/login?role=donor'}>
                  Register as Donor
                </Button>
              )}
            </div>
          )}

          {/* Rare blood notice */}
          <div className="glass-card p-4 flex gap-3" style={{ borderColor: 'rgba(240,192,64,0.3)' }}>
            <Info size={18} className="text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-yellow-300 mb-1">Rare Blood Types (AB−, O−)</p>
              <p className="text-xs text-white/45 leading-relaxed">
                If you have AB− or O− blood, you are especially valuable. O− is the universal donor
                used in emergencies. Please consider donating as often as you are eligible.
              </p>
            </div>
          </div>
        </div>

        {/* Right — criteria */}
        <div className="space-y-4">
          <h2 className="font-heading font-bold text-white text-lg">Eligibility Criteria</h2>
          <p className="text-sm text-white/40 mb-4">Based on WHO and Indian blood donation guidelines.</p>

          {CRITERIA.map(c => (
            <div key={c.label} className="glass-card p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-blood-900/40 flex items-center justify-center text-blood-400 flex-shrink-0">
                {c.icon}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-white text-sm">{c.label}</p>
                <p className="text-xs text-white/45">{c.value}</p>
              </div>
              <CheckCircle size={18} className="text-emerald-400 flex-shrink-0" />
            </div>
          ))}

          <div className="glass-card p-5 space-y-3" style={{ borderColor: 'rgba(231,76,60,0.2)' }}>
            <p className="font-semibold text-white text-sm flex items-center gap-2">
              <XCircle size={16} className="text-blood-400" /> Temporary Deferrals
            </p>
            <ul className="space-y-1.5 text-xs text-white/45 list-none">
              {[
                'Illness, fever, or infection in the last 2 weeks',
                'Tattoo or piercing in the last 6 months',
                'Dental procedure in the last 24 hours',
                'Pregnancy or breastfeeding',
                'Vaccination in the last 2 weeks (varies by vaccine)',
                'Travel to malaria-endemic areas in the last year',
              ].map(d => (
                <li key={d} className="flex items-start gap-2">
                  <span className="text-blood-600 mt-0.5">—</span>
                  <span>{d}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="glass-card p-5 space-y-2">
            <p className="font-semibold text-white text-sm">What Happens During Donation?</p>
            <ol className="space-y-2 text-xs text-white/45">
              {[
                'Registration & ID check (5 min)',
                'Health screening — BP, haemoglobin, pulse (10 min)',
                'Blood collection — 450 ml whole blood (8–10 min)',
                'Rest & refreshments (15 min)',
              ].map((s, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-blood-500 font-bold flex-shrink-0">{i+1}.</span>
                  <span>{s}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </Layout>
  )
}
