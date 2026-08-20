import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, Users, Building2, Droplets, TrendingUp, ChevronRight, Zap, Shield, Clock, Star } from 'lucide-react'
import Button from '../components/ui/Button'
import { StatCard } from '../components/ui/Card'
import { BloodGroupBadge } from '../components/ui/Badge'
import SOSBanner from '../components/shared/SOSBanner'
import BloodSearchForm from '../components/shared/BloodSearchForm'
import api from '../api/client'

const QUOTES = [
  { en: 'Every drop saves a life.', gu: 'દરેક ટીપું એક જીવ બચાવે છે.' },
  { en: 'One donation. Three lives. One hero.', gu: 'એક દાન. ત્રણ જીવ. એક હીરો.' },
  { en: "You don't need a cape to be a hero. Just say YES.", gu: 'હીરો બનવા ઝભ્ભો નથી જોઈતો. ફક્ત "હા" કહો.' },
  { en: 'Be someone\'s reason to smile today. Donate blood.', gu: 'આજે કોઈના સ્મિતનું કારણ બનો.' },
]

const TIERS = [
  { num: 'T1', label: 'Hospitals',    color: '#3b82f6', desc: 'Verified hospitals with live blood inventory' },
  { num: 'T2', label: 'Blood Banks',  color: '#2ecc71', desc: 'Certified blood banks stocking your type'      },
  { num: 'T3', label: 'Blood Camps',  color: '#f0c040', desc: 'Active donation drives in your city'           },
  { num: 'T4', label: 'Community',    color: '#e74c3c', desc: 'AI-ranked eligible donors near you'            },
  { num: 'T5', label: 'WhatsApp SOS', color: '#25D366', desc: 'Emergency broadcast to the community'          },
]

export default function Home() {
  const navigate = useNavigate()
  const [stats,    setStats]    = useState(null)
  const [topDonors, setTopDonors] = useState([])
  const [quoteIdx, setQuoteIdx] = useState(0)
  const [shortage, setShortage] = useState(null)

  useEffect(() => {
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
    api.get('/daata-wall').then(r => setTopDonors(r.data.slice(0, 3))).catch(() => {})
    api.get('/analytics/shortage').then(r => setShortage(r.data)).catch(() => {})
    const t = setInterval(() => setQuoteIdx(i => (i + 1) % QUOTES.length), 4000)
    return () => clearInterval(t)
  }, [])

  const q = QUOTES[quoteIdx]

  return (
    <div className="space-y-16">
      <SOSBanner />

      {/* ── Hero ─────────────────────────────────── */}
      <section className="grid lg:grid-cols-2 gap-10 items-center min-h-[80vh] lg:min-h-0 py-4">
        {/* Left */}
        <div className="space-y-8">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blood-700/40 bg-blood-950/30 text-xs font-semibold text-blood-300 uppercase tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-blood-400 animate-pulse" />
              Gujarat's Blood Network
            </div>
            <h1 className="font-heading font-black text-5xl lg:text-6xl leading-[1.05] text-white">
              Connect Blood.<br />
              <span style={{
                background: 'linear-gradient(135deg, #ff6b6b 0%, #c0392b 100%)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text'
              }}>Save Lives.</span>
            </h1>
            <div className="h-12 overflow-hidden">
              <p key={quoteIdx} className="text-white/55 text-lg leading-relaxed slide-in">{q.en}</p>
            </div>
            <p className="text-white/25 text-sm italic">{q.gu}</p>
          </div>

          {/* Stats row */}
          {stats && (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Donors',     value: stats.donors,    icon: <Users size={16} /> },
                { label: 'Hospitals',  value: stats.hospitals, icon: <Building2 size={16} /> },
                { label: 'Lives Saved',value: stats.lives_saved, icon: <Heart size={16} /> },
              ].map(s => (
                <div key={s.label} className="glass-card p-3 text-center">
                  <div className="flex justify-center text-blood-400 mb-1">{s.icon}</div>
                  <p className="font-heading font-black text-2xl text-white">{s.value.toLocaleString()}</p>
                  <p className="text-xs text-white/35 uppercase tracking-wider">{s.label}</p>
                </div>
              ))}
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <Button
              size="lg"
              variant="sos"
              onClick={() => navigate('/find-blood')}
              icon={<Zap size={18} />}
            >
              Emergency — Find Blood
            </Button>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => navigate('/login', { state: { role: 'donor' } })}
            >
              Become a Donor
            </Button>
          </div>
        </div>

        {/* Right — Search card */}
        <div className="glass-card p-6 lg:p-8 space-y-5" style={{ border: '1px solid rgba(192,57,43,0.25)' }}>
          <div>
            <h2 className="font-heading font-bold text-xl text-white mb-1">Find Blood Fast</h2>
            <p className="text-sm text-white/40">AI-powered 5-tier search across Gujarat</p>
          </div>
          <BloodSearchForm />
        </div>
      </section>

      {/* ── 5-Tier Architecture ───────────────────── */}
      <section>
        <div className="text-center mb-10">
          <h2 className="sec-header mb-3">How BloodSetu Finds Blood</h2>
          <p className="text-white/45 text-sm max-w-xl mx-auto">
            Our AI runs a 5-tier cascading search — from hospital inventories to community donors —
            stopping at the first tier where blood is found.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {TIERS.map((t, i) => (
            <div
              key={t.num}
              className="glass-card p-5 flex flex-col items-center text-center gap-3 hover:-translate-y-1 transition-transform cursor-default"
              style={{ borderColor: `${t.color}30` }}
            >
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center font-heading font-black text-sm text-white"
                style={{ background: `${t.color}25`, border: `2px solid ${t.color}50` }}
              >
                {t.num}
              </div>
              <p className="font-semibold text-white text-sm">{t.label}</p>
              <p className="text-xs text-white/35 leading-relaxed">{t.desc}</p>
              {i < TIERS.length - 1 && (
                <ChevronRight className="hidden lg:block absolute right-0 top-1/2 -translate-y-1/2 text-white/10" size={16} />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── Blood Shortage Forecast ───────────────── */}
      {shortage && (
        <section>
          <div className="flex items-end justify-between mb-6">
            <div>
              <h2 className="sec-header mb-1">AI Shortage Forecast</h2>
              <p className="text-white/40 text-sm">Predicted availability for next month</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => navigate('/analytics')}>
              Full Analytics <ChevronRight size={14} />
            </Button>
          </div>
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
            {Object.entries(shortage).map(([group, data]) => {
              const colors = { '🔴 Critical': '#e74c3c', '🟡 Low': '#f0c040', '🟢 Good': '#2ecc71' }
              const color  = colors[data.status] || '#2ecc71'
              const isCritical = data.status.includes('Critical')
              return (
                <div
                  key={group}
                  className="glass-card p-3 flex flex-col items-center gap-2 text-center"
                  style={{ borderColor: isCritical ? 'rgba(231,76,60,0.5)' : undefined }}
                >
                  <BloodGroupBadge group={group} size="sm" />
                  <div
                    className="w-full rounded-full overflow-hidden"
                    style={{ height: 4, background: 'rgba(255,255,255,0.06)' }}
                  >
                    <div style={{ width: `${data.probability}%`, height: '100%', background: color, borderRadius: 9999 }} />
                  </div>
                  <p className="text-[10px]" style={{ color }}>{data.status.split(' ')[1]}</p>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* ── Daata Wall Preview ───────────────────── */}
      {topDonors.length > 0 && (
        <section>
          <div className="flex items-end justify-between mb-6">
            <div>
              <h2 className="sec-header mb-1">Daata Wall of Honor</h2>
              <p className="text-white/40 text-sm">Celebrating Gujarat's most dedicated donors</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => navigate('/daata-wall')}>
              View All <ChevronRight size={14} />
            </Button>
          </div>
          <div className="grid sm:grid-cols-3 gap-4">
            {topDonors.map((d, i) => {
              const medals = ['👑', '🥈', '🥉']
              return (
                <div
                  key={d.id}
                  className="glass-card p-5 flex items-center gap-4"
                  style={i === 0 ? { borderColor: 'rgba(240,192,64,0.4)', background: 'rgba(240,192,64,0.05)' } : {}}
                >
                  <div className="text-3xl flex-shrink-0">{medals[i] || '🏅'}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <BloodGroupBadge group={d.blood_group} size="sm" />
                      <p className="font-semibold text-white text-sm truncate">{d.name}</p>
                    </div>
                    <p className="text-xs text-white/40">{d.city} · {d.donations_count} donations</p>
                    <p className="text-xs text-blood-400 font-semibold mt-0.5">
                      {(d.donations_count * 3)} lives saved
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* ── Why Donate ──────────────────────────── */}
      <section>
        <div className="text-center mb-10">
          <h2 className="sec-header mb-3">Why Your Blood Matters</h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { icon: <Heart size={22} />, title: '3 Lives Per Donation', desc: 'Each whole blood donation can be separated into components — red cells, platelets, and plasma — saving up to 3 lives.' },
            { icon: <Clock size={22} />, title: 'Ready in 90 Days', desc: 'After donating, your body replenishes red blood cells within 90 days. You can donate up to 4 times a year.' },
            { icon: <Shield size={22} />, title: 'Safe & Monitored', desc: 'All donations go through screening. Every donor gets a health check. The process takes under 30 minutes.' },
            { icon: <Zap size={22} />, title: 'Emergency Ready', desc: 'Accidents, surgeries, cancer treatments — all require blood. Your donation is someone\'s emergency backup.' },
            { icon: <Users size={22} />, title: 'Community Impact', desc: 'Only 7% of Indians donate blood. Join BloodSetu\'s network and be part of the 7% who make a difference.' },
            { icon: <Star size={22} />, title: 'Earn Badges', desc: 'Track your donations, earn recognition badges, and be featured on the Daata Wall of Honor for the community to celebrate.' },
          ].map(item => (
            <div key={item.title} className="glass-card p-5 flex gap-4">
              <div className="w-10 h-10 flex-shrink-0 rounded-xl bg-blood-900/50 flex items-center justify-center text-blood-400">
                {item.icon}
              </div>
              <div>
                <p className="font-semibold text-white mb-1 text-sm">{item.title}</p>
                <p className="text-xs text-white/40 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Band ─────────────────────────────── */}
      <section
        className="rounded-2xl p-8 lg:p-12 text-center space-y-5"
        style={{ background: 'linear-gradient(135deg, rgba(192,57,43,0.2) 0%, rgba(120,20,20,0.15) 100%)', border: '1px solid rgba(192,57,43,0.3)' }}
      >
        <div className="heartbeat inline-block">
          <Droplets size={40} className="text-blood-400 mx-auto" />
        </div>
        <h2 className="font-heading font-black text-3xl text-white">Ready to save a life today?</h2>
        <p className="text-white/50 text-sm max-w-md mx-auto">
          Register as a donor in under 2 minutes. You'll be found by seekers in your city when your blood group is needed.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button size="lg" variant="sos" onClick={() => navigate('/login', { state: { role: 'donor' } })}>
            Register as Donor
          </Button>
          <Button size="lg" variant="secondary" onClick={() => navigate('/find-blood')}>
            I Need Blood
          </Button>
        </div>
      </section>
    </div>
  )
}
