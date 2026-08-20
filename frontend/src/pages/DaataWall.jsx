import { useEffect, useState } from 'react'
import { Share2, Crown, Heart, Droplets } from 'lucide-react'
import Layout, { PageHeader } from '../components/layout/Layout'
import { StatCard } from '../components/ui/Card'
import { BloodGroupBadge, DonorBadge } from '../components/ui/Badge'
import api from '../api/client'

const WA_MSG = `💉 Did you know?\n\nEvery 2 seconds someone in India needs blood.\nOnly 7% of Indians donate.\nYou could be someone's miracle.\n\n🩸 Register as a donor on BloodSetu\nGujarat's AI-powered Blood Connection Portal\n\n✅ One drop of yours = Three lives saved. ❤️\n\nShare this. Spread hope. Be a hero.`

function PodiumCard({ donor, rank }) {
  const medals = [
    { icon: '👑', color: '#f0c040', ring: 'rgba(240,192,64,0.4)', bg: 'rgba(240,192,64,0.07)', size: 'lg' },
    { icon: '🥈', color: '#9ca3af', ring: 'rgba(156,163,175,0.35)', bg: 'rgba(156,163,175,0.05)', size: 'md' },
    { icon: '🥉', color: '#b45309', ring: 'rgba(180,83,9,0.35)', bg: 'rgba(180,83,9,0.05)', size: 'md' },
  ]
  const m = medals[rank] || medals[2]

  return (
    <div className="glass-card p-6 flex flex-col items-center text-center gap-4"
      style={{ borderColor: m.ring, background: m.bg }}>
      <span className="text-4xl">{m.icon}</span>
      <BloodGroupBadge group={donor.blood_group} size={m.size} />
      <div>
        <p className="font-heading font-bold text-white text-lg">{donor.name}</p>
        <p className="text-xs text-white/40 mt-0.5">{donor.city}</p>
      </div>
      <div className="grid grid-cols-2 gap-3 w-full">
        <div className="glass-card p-2.5 !border-white/5 text-center">
          <p className="font-heading font-black text-xl" style={{ color: m.color }}>{donor.donations_count}</p>
          <p className="text-[10px] text-white/35 uppercase tracking-wider">Donations</p>
        </div>
        <div className="glass-card p-2.5 !border-white/5 text-center">
          <p className="font-heading font-black text-xl text-blood-400">{donor.donations_count * 3}</p>
          <p className="text-[10px] text-white/35 uppercase tracking-wider">Lives Saved</p>
        </div>
      </div>
      {donor.badges?.length > 0 && (
        <div className="flex flex-wrap justify-center gap-1">
          {donor.badges.map(b => (
            <span key={b.id} className="text-lg" title={b.name}>
              {b.id === 'first_drop' ? '🩸' : b.id === 'life_saver' ? '❤️' : b.id === 'legend' ? '👑' : b.id === 'rare_blood' ? '💎' : '🏅'}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export default function DaataWall() {
  const [donors, setDonors] = useState([])
  const [stats,  setStats]  = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/daata-wall').then(r => setDonors(r.data)).finally(() => setLoading(false))
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
  }, [])

  const waLink = `https://wa.me/?text=${encodeURIComponent(WA_MSG)}`
  const top3   = donors.slice(0, 3)
  const rest   = donors.slice(3)

  return (
    <Layout>
      <PageHeader
        title="Daata Wall of Honor"
        subtitle="Celebrating Gujarat's most dedicated blood donors. Every name here has saved lives."
      />

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-10">
          <StatCard label="Registered Donors" value={stats.donors}      color="blood" icon={<Droplets size={18} />} />
          <StatCard label="Total Donations"   value={stats.donations}   color="green" icon={<Heart size={18} />} />
          <StatCard label="Lives Saved"        value={stats.lives_saved} color="gold"  icon={<Crown size={18} />} />
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-white/30">Loading donors…</div>
      ) : donors.length === 0 ? (
        <div className="text-center py-20 text-white/35 space-y-2">
          <Crown size={48} className="mx-auto opacity-20" />
          <p>No donors on the wall yet.</p>
          <p className="text-sm">Donors must opt in from their portal settings.</p>
        </div>
      ) : (
        <div className="space-y-10">
          {/* Podium — top 3 */}
          {top3.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-4">Top Donors</h2>
              <div className={`grid gap-4 ${top3.length === 1 ? 'max-w-sm' : top3.length === 2 ? 'sm:grid-cols-2 max-w-xl' : 'sm:grid-cols-3'}`}>
                {top3.map((d, i) => <PodiumCard key={d.id} donor={d} rank={i} />)}
              </div>
            </section>
          )}

          {/* Full leaderboard */}
          {rest.length > 0 && (
            <section>
              <h2 className="font-heading font-bold text-white/70 text-sm uppercase tracking-widest mb-4">Full Leaderboard</h2>
              <div className="space-y-2">
                {rest.map((d, i) => (
                  <div key={d.id} className="glass-card p-4 flex items-center gap-4 slide-in" style={{ animationDelay: `${i * 40}ms` }}>
                    <span className="w-8 text-center font-heading font-black text-white/30 text-sm flex-shrink-0">
                      {i + 4}
                    </span>
                    <BloodGroupBadge group={d.blood_group} size="sm" />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white text-sm">{d.name}</p>
                      <p className="text-xs text-white/40">{d.city}</p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-heading font-bold text-white">{d.donations_count}</p>
                      <p className="text-[10px] text-white/35">donations</p>
                    </div>
                    <div className="text-right flex-shrink-0 min-w-[60px]">
                      <p className="font-heading font-bold text-blood-400">{d.donations_count * 3}</p>
                      <p className="text-[10px] text-white/35">lives saved</p>
                    </div>
                    <div className="flex gap-0.5 flex-shrink-0">
                      {d.badges?.slice(0,3).map(b => (
                        <span key={b.id} className="text-base">
                          {b.id==='first_drop'?'🩸':b.id==='life_saver'?'❤️':b.id==='legend'?'👑':b.id==='rare_blood'?'💎':'🏅'}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* WhatsApp awareness */}
          <section className="glass-card p-6 space-y-4 max-w-xl">
            <h3 className="font-heading font-bold text-white">Spread Awareness</h3>
            <pre className="wa-box text-xs">{WA_MSG}</pre>
            <a href={waLink} target="_blank" rel="noreferrer"
              className="flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white w-full"
              style={{ background:'linear-gradient(135deg,#25D366,#128C7E)' }}>
              <Share2 size={16} /> Share on WhatsApp
            </a>
          </section>
        </div>
      )}
    </Layout>
  )
}
