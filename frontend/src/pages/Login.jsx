import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { LogIn, Droplets } from 'lucide-react'
import { Input } from '../components/ui/Input'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import { useAuth } from '../context/AuthContext'

const ROLE_INFO = {
  donor:      { label: 'Donor',      color: '#e74c3c', desc: 'Register and manage your donation profile' },
  hospital:   { label: 'Hospital',   color: '#3b82f6', desc: 'Update blood inventory and manage donors'   },
  blood_bank: { label: 'Blood Bank', color: '#2ecc71', desc: 'Track stock and confirm donations'           },
  camp:       { label: 'Blood Camp', color: '#f0c040', desc: 'Manage your blood drive and donors'          },
}

export default function Login() {
  const { login, loading } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const initRole  = location.state?.role || ''

  const [form, setForm] = useState({ username: '', password: '' })
  const [err,  setErr]  = useState('')

  const handleSubmit = async e => {
    e.preventDefault(); setErr('')
    const res = await login(form.username, form.password)
    if (!res.ok) { setErr(res.message); return }
    const from = location.state?.from || '/'
    navigate(from, { replace: true })
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-sm space-y-8">
        {/* Brand */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="heartbeat">
              <Droplets size={44} className="text-blood-400" />
            </div>
          </div>
          <div>
            <h1 className="font-heading font-black text-3xl text-white">BloodSetu</h1>
            <p className="text-white/35 text-sm mt-1">Sign in to your account</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-card p-7 space-y-5">
          <Input
            label="Username"
            placeholder="Enter your username"
            value={form.username}
            onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
            autoComplete="username"
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="Enter your password"
            value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            autoComplete="current-password"
            required
          />
          {err && <Alert type="error" message={err} />}
          <Button type="submit" loading={loading} fullWidth size="lg" icon={<LogIn size={16} />}>
            Sign In
          </Button>
        </form>

        {/* Register links */}
        <div className="space-y-3">
          <p className="text-center text-xs text-white/35">Don't have an account? Register as:</p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(ROLE_INFO).map(([role, info]) => (
              <Link
                key={role}
                to="/register"
                state={{ role }}
                className="flex flex-col items-center gap-1 p-3 rounded-xl border border-white/8 bg-white/3 hover:bg-white/6 hover:border-white/15 transition-all cursor-pointer text-center"
              >
                <span className="text-xs font-semibold" style={{ color: info.color }}>{info.label}</span>
                <span className="text-[10px] text-white/30 leading-tight">{info.desc}</span>
              </Link>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-white/20">
          Blood seekers don't need an account.{' '}
          <Link to="/find-blood" className="text-blood-400 hover:text-blood-300">Find blood directly →</Link>
        </p>
      </div>
    </div>
  )
}
