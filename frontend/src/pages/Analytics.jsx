import { useEffect, useState } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { TrendingUp, AlertCircle, Info } from 'lucide-react'
import Layout, { PageHeader } from '../components/layout/Layout'
import { StatCard } from '../components/ui/Card'
import Alert from '../components/ui/Alert'
import api from '../api/client'

const BLOOD_COLORS = {
  'A+':'#e74c3c','A-':'#c0392b','B+':'#e67e22','B-':'#d35400',
  'O+':'#3b82f6','O-':'#1d4ed8','AB+':'#9b59b6','AB-':'#7d3c98',
}
const STATUS_COLORS = { '🔴 Critical':'#e74c3c', '🟡 Low':'#f0c040', '🟢 Good':'#2ecc71' }

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-3 py-2 text-xs border border-white/10">
      <p className="text-white/60 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || p.fill }}>{p.name}: <strong>{p.value}</strong></p>
      ))}
    </div>
  )
}

export default function Analytics() {
  const [stats,     setStats]     = useState(null)
  const [shortage,  setShortage]  = useState(null)
  const [bloodDist, setBloodDist] = useState([])
  const [hospCity,  setHospCity]  = useState([])
  const [trend,     setTrend]     = useState([])
  const [activeSos, setActiveSos] = useState([])

  useEffect(() => {
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
    api.get('/analytics/shortage').then(r => setShortage(r.data)).catch(() => {})
    api.get('/analytics/blood-distribution').then(r => setBloodDist(r.data)).catch(() => {})
    api.get('/analytics/hospitals-by-city').then(r => setHospCity(r.data)).catch(() => {})
    api.get('/analytics/donations-trend').then(r => setTrend(r.data)).catch(() => {})
    api.get('/sos/active').then(r => setActiveSos(r.data)).catch(() => {})
  }, [])

  const shortageData = shortage
    ? Object.entries(shortage).map(([group, d]) => ({
        group,
        probability: d.probability,
        status: d.status,
        fill: STATUS_COLORS[d.status] || '#2ecc71',
      }))
    : []

  return (
    <Layout>
      <PageHeader
        title="Analytics"
        subtitle="Live platform statistics and AI-powered blood shortage predictions."
      />

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-10">
          <StatCard label="Donors"      value={stats.donors}      color="blood"  icon={<TrendingUp size={18} />} />
          <StatCard label="Hospitals"   value={stats.hospitals}   color="blue"   icon={<TrendingUp size={18} />} />
          <StatCard label="Blood Banks" value={stats.blood_banks} color="green"  icon={<TrendingUp size={18} />} />
          <StatCard label="Camps"       value={stats.camps}       color="gold"   icon={<TrendingUp size={18} />} />
          <StatCard label="Donations"   value={stats.donations}   color="purple" icon={<TrendingUp size={18} />} />
          <StatCard label="Lives Saved" value={stats.lives_saved} color="blood"  icon={<TrendingUp size={18} />} />
        </div>
      )}

      {/* Active SOS alert */}
      {activeSos.length > 0 && (
        <Alert type="error" message={`${activeSos.length} active SOS request${activeSos.length>1?'s':''} right now across Gujarat.`} className="mb-8" />
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Shortage Prediction */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h2 className="font-heading font-bold text-white mb-1">Blood Shortage Forecast</h2>
            <p className="text-xs text-white/40">AI prediction for next month (Random Forest model)</p>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={shortageData} barSize={28}>
              <XAxis dataKey="group" tick={{ fill:'rgba(255,255,255,0.5)', fontSize:11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill:'rgba(255,255,255,0.4)', fontSize:10 }} axisLine={false} tickLine={false} domain={[0,100]} unit="%" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="probability" name="Shortage Risk %" radius={[6,6,0,0]}>
                {shortageData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 text-xs text-white/40 flex-wrap">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm inline-block bg-[#e74c3c]" /> Critical</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm inline-block bg-[#f0c040]" /> Low</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm inline-block bg-[#2ecc71]" /> Good</span>
          </div>
        </div>

        {/* Blood Group Distribution */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h2 className="font-heading font-bold text-white mb-1">Donor Blood Group Distribution</h2>
            <p className="text-xs text-white/40">Registered donors by blood group</p>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={bloodDist} dataKey="count" nameKey="blood_group"
                cx="50%" cy="50%" outerRadius={90} innerRadius={50}
                paddingAngle={3} label={({ blood_group, percent }) => `${blood_group} ${(percent*100).toFixed(0)}%`}
                labelLine={{ stroke:'rgba(255,255,255,0.2)' }}>
                {bloodDist.map((entry, i) => (
                  <Cell key={i} fill={BLOOD_COLORS[entry.blood_group] || '#888'} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Hospitals by City */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h2 className="font-heading font-bold text-white mb-1">Verified Hospitals by City</h2>
            <p className="text-xs text-white/40">Coverage across Gujarat</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={hospCity} layout="vertical" barSize={16}>
              <XAxis type="number" tick={{ fill:'rgba(255,255,255,0.4)', fontSize:10 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="city" type="category" tick={{ fill:'rgba(255,255,255,0.5)', fontSize:11 }} axisLine={false} tickLine={false} width={80} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Hospitals" fill="#3b82f6" radius={[0,6,6,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Donation Trend */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h2 className="font-heading font-bold text-white mb-1">Monthly Donation Trend</h2>
            <p className="text-xs text-white/40">Confirmed donations over time</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trend}>
              <XAxis dataKey="month" tick={{ fill:'rgba(255,255,255,0.4)', fontSize:10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill:'rgba(255,255,255,0.4)', fontSize:10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="count" name="Donations" stroke="#e74c3c"
                strokeWidth={2} dot={{ fill:'#e74c3c', r:4 }} activeDot={{ r:6 }} />
            </LineChart>
          </ResponsiveContainer>
          {trend.length === 0 && <p className="text-xs text-white/30 text-center">Donation data will appear as confirmed donations accumulate.</p>}
        </div>
      </div>

      {/* Model explanations */}
      <div className="grid sm:grid-cols-2 gap-4 mt-8">
        <div className="glass-card p-5 flex gap-4">
          <div className="w-10 h-10 rounded-xl bg-blood-900/40 flex items-center justify-center flex-shrink-0">
            <Info size={18} className="text-blood-400" />
          </div>
          <div>
            <p className="font-semibold text-white text-sm mb-1">KNN Donor Ranking</p>
            <p className="text-xs text-white/40 leading-relaxed">
              When blood is needed, donors are ranked using a K-Nearest Neighbours distance proxy.
              Donors in the same area are ranked first, then sorted by experience (donation count).
              This puts the most experienced, closest donor at the top.
            </p>
          </div>
        </div>
        <div className="glass-card p-5 flex gap-4">
          <div className="w-10 h-10 rounded-xl bg-blue-900/40 flex items-center justify-center flex-shrink-0">
            <TrendingUp size={18} className="text-blue-400" />
          </div>
          <div>
            <p className="font-semibold text-white text-sm mb-1">Random Forest Shortage Prediction</p>
            <p className="text-xs text-white/40 leading-relaxed">
              A Random Forest classifier trained on 12 months of synthetic data predicts shortage risk
              for each blood group. Features include month, group index, donor count, and request
              volume. Probabilities above 65% are flagged as Critical.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
