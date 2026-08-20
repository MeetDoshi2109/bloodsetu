import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { UserPlus, Droplets, Building2, Heart, CalendarDays } from 'lucide-react'
import { Input, Select } from '../components/ui/Input'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import { useAuth } from '../context/AuthContext'

const ROLES = [
  { id: 'donor',      label: 'Donor',      icon: <Heart size={20} />,         color: '#e74c3c', desc: 'Register to donate and appear in emergency searches.' },
  { id: 'hospital',   label: 'Hospital',   icon: <Building2 size={20} />,     color: '#3b82f6', desc: 'Manage blood inventory and confirm donations.' },
  { id: 'blood_bank', label: 'Blood Bank', icon: <Droplets size={20} />,      color: '#2ecc71', desc: 'Track stock and manage donor visits.' },
  { id: 'camp',       label: 'Blood Camp', icon: <CalendarDays size={20} />,  color: '#f0c040', desc: 'Organise donation drives and manage RSVPs.' },
]

export default function Register() {
  const { register, login, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const initRole = location.state?.role || ''

  const [role,   setRole]   = useState(initRole)
  const [form,   setForm]   = useState({ username: '', password: '', confirm: '', phone: '' })
  const [err,    setErr]    = useState('')
  const [done,   setDone]   = useState(false)

  const handleSubmit = async e => {
    e.preventDefault(); setErr('')
    if (form.password !== form.confirm) { setErr('Passwords do not match'); return }
    if (form.phone.length !== 10 || !/^\d+$/.test(form.phone)) { setErr('Enter a valid 10-digit phone number'); return }
    if (!role) { setErr('Please select a role'); return }

    const res = await register(form.username, form.password, role, form.phone)
    if (!res.ok) { setErr(res.message); return }

    // Auto login
    const lr = await login(form.username, form.password)
    if (lr.ok) {
      const portalMap = { donor: '/portal/donor', hospital: '/portal/hospital', blood_bank: '/portal/blood-bank', camp: '/portal/camp' }
      navigate(portalMap[role] || '/')
    } else {
      setDone(true)
    }
  }

  if (done) return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center space-y-4 max-w-sm">
        <div className="text-5xl">✅</div>
        <h2 className="font-heading font-bold text-2xl text-white">Account Created!</h2>
        <p className="text-white/50 text-sm">Sign in to complete your profile.</p>
        <Button onClick={() => navigate('/login')}>Sign In Now</Button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="heartbeat flex justify-center mb-3">
            <Droplets size={40} className="text-blood-400" />
          </div>
          <h1 className="font-heading font-black text-3xl text-white">Create Account</h1>
          <p className="text-white/35 text-sm mt-1">Join BloodSetu and make a difference</p>
        </div>

        {/* Role picker */}
        {!role ? (
          <div className="space-y-4">
            <p className="text-center text-sm text-white/50">What best describes you?</p>
            <div className="grid grid-cols-2 gap-3">
              {ROLES.map(r => (
                <button
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className="glass-card p-5 flex flex-col items-center gap-3 hover:-translate-y-1 transition-all cursor-pointer text-center"
                  style={{ borderColor: `${r.color}30` }}
                >
                  <span style={{ color: r.color }}>{r.icon}</span>
                  <div>
                    <p className="font-semibold text-white text-sm">{r.label}</p>
                    <p className="text-[11px] text-white/35 mt-1 leading-tight">{r.desc}</p>
                  </div>
                </button>
              ))}
            </div>
            <p className="text-center text-xs text-white/25">
              Already have an account?{' '}
              <Link to="/login" className="text-blood-400 hover:text-blood-300">Sign in</Link>
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {/* Selected role badge */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {(() => {
                  const r = ROLES.find(x => x.id === role)
                  return r ? (
                    <>
                      <span style={{ color: r.color }}>{r.icon}</span>
                      <span className="text-sm font-semibold text-white">Registering as {r.label}</span>
                    </>
                  ) : null
                })()}
              </div>
              <button onClick={() => setRole('')}
                className="text-xs text-white/35 hover:text-white/70 cursor-pointer transition-colors">
                Change
              </button>
            </div>

            <form onSubmit={handleSubmit} className="glass-card p-7 space-y-5">
              <Input
                label="Username"
                placeholder="Choose a unique username"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                autoComplete="username"
                required
              />
              <Input
                label="Password"
                type="password"
                placeholder="At least 8 characters"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                autoComplete="new-password"
                required
              />
              <Input
                label="Confirm Password"
                type="password"
                placeholder="Repeat your password"
                value={form.confirm}
                onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))}
                required
              />
              <Input
                label="Phone Number"
                placeholder="10-digit mobile number"
                value={form.phone}
                onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                maxLength={10}
                inputMode="numeric"
                required
              />
              {err && <Alert type="error" message={err} />}
              <Button type="submit" loading={loading} fullWidth size="lg" icon={<UserPlus size={16} />}>
                Create Account
              </Button>
              <p className="text-center text-xs text-white/25">
                Already have an account?{' '}
                <Link to="/login" className="text-blood-400 hover:text-blood-300">Sign in</Link>
              </p>
            </form>

            {(role === 'hospital' || role === 'blood_bank' || role === 'camp') && (
              <p className="text-xs text-white/30 text-center leading-relaxed">
                Provider accounts require admin verification before becoming publicly visible.
                This usually takes under 24 hours.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
