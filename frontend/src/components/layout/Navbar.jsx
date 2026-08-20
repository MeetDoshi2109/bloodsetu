import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Menu, X, Droplets, LogOut, User, ChevronDown } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { clsx } from 'clsx'

const NAV_LINKS = [
  { to: '/',            label: 'Home'        },
  { to: '/find-blood',  label: 'Find Blood'  },
  { to: '/eligibility', label: 'Eligibility' },
  { to: '/analytics',   label: 'Analytics'   },
  { to: '/daata-wall',  label: 'Daata Wall'  },
]

const ROLE_PORTAL = {
  donor:      { to: '/portal/donor',      label: 'Donor Portal'      },
  hospital:   { to: '/portal/hospital',   label: 'Hospital Portal'   },
  blood_bank: { to: '/portal/blood-bank', label: 'Blood Bank Portal' },
  camp:       { to: '/portal/camp',       label: 'Camp Portal'       },
  admin:      { to: '/admin',             label: 'Admin Panel'        },
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const [open, setOpen]     = useState(false)
  const [dropdown, setDropdown] = useState(false)

  const portal = user ? ROLE_PORTAL[user.role] : null

  const handleLogout = async () => {
    await logout()
    setDropdown(false)
    navigate('/')
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-40">
      <div className="mx-auto max-w-7xl px-4 pt-3">
        <nav
          className="flex items-center justify-between px-5 py-3 rounded-2xl border border-white/8"
          style={{ background: 'rgba(10,3,3,0.85)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)' }}
          aria-label="Main navigation"
        >
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" aria-label="BloodSetu home">
            <BloodDropIcon />
            <div>
              <span className="font-heading font-black text-lg text-white tracking-tight">BloodSetu</span>
              <span className="hidden sm:block text-[9px] text-white/30 uppercase tracking-widest font-semibold -mt-1 block">
                Connect Blood. Save Lives.
              </span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center gap-1">
            {NAV_LINKS.map(l => (
              <Link
                key={l.to}
                to={l.to}
                className={clsx(
                  'px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer',
                  location.pathname === l.to
                    ? 'bg-blood-700/20 text-blood-300 border border-blood-700/30'
                    : 'text-white/60 hover:text-white hover:bg-white/5'
                )}
              >
                {l.label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="hidden lg:flex items-center gap-2">
            {/* Emergency SOS */}
            <Link
              to="/find-blood"
              className="px-4 py-2 rounded-xl text-sm font-bold text-white cursor-pointer transition-all duration-200 sos-pulse"
              style={{ background: 'linear-gradient(135deg, #c0392b, #7b241c)', boxShadow: '0 0 16px rgba(192,57,43,0.4)' }}
            >
              Emergency SOS
            </Link>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropdown(d => !d)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/8 transition-all cursor-pointer"
                  aria-expanded={dropdown}
                  aria-haspopup="true"
                >
                  <div className="w-6 h-6 rounded-full bg-blood-700/50 flex items-center justify-center">
                    <User size={13} className="text-blood-300" />
                  </div>
                  <span className="text-sm text-white/80 max-w-[100px] truncate">{user.username}</span>
                  <ChevronDown size={13} className={clsx('text-white/40 transition-transform', dropdown && 'rotate-180')} />
                </button>
                {dropdown && (
                  <div className="absolute right-0 top-full mt-2 w-52 glass-card py-1 shadow-card slide-in"
                    role="menu">
                    <div className="px-3 py-2 border-b border-white/5">
                      <p className="text-xs text-white/40 uppercase tracking-wider">Signed in as</p>
                      <p className="text-sm font-semibold text-white truncate">{user.username}</p>
                      <p className="text-xs text-blood-400 capitalize">{user.role}</p>
                    </div>
                    {portal && (
                      <Link
                        to={portal.to}
                        role="menuitem"
                        onClick={() => setDropdown(false)}
                        className="flex items-center gap-2 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
                      >
                        <User size={14} />
                        {portal.label}
                      </Link>
                    )}
                    <button
                      role="menuitem"
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-950/20 transition-colors cursor-pointer"
                    >
                      <LogOut size={14} />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/15 hover:border-blood-600/50 text-white/70 hover:text-white bg-white/3 hover:bg-blood-950/30 transition-all cursor-pointer"
              >
                Sign in
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            className="lg:hidden p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/5 cursor-pointer"
            onClick={() => setOpen(o => !o)}
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </nav>
      </div>

      {/* Mobile menu */}
      {open && (
        <div
          className="lg:hidden mx-4 mt-1 rounded-2xl border border-white/8 p-4 slide-in"
          style={{ background: 'rgba(10,3,3,0.95)', backdropFilter: 'blur(20px)' }}
        >
          <nav className="flex flex-col gap-1" aria-label="Mobile navigation">
            {NAV_LINKS.map(l => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className={clsx(
                  'px-4 py-3 rounded-xl text-sm font-medium transition-colors cursor-pointer',
                  location.pathname === l.to
                    ? 'bg-blood-700/20 text-blood-300'
                    : 'text-white/60 hover:text-white hover:bg-white/5'
                )}
              >
                {l.label}
              </Link>
            ))}
            <Link
              to="/find-blood"
              onClick={() => setOpen(false)}
              className="mt-2 px-4 py-3 rounded-xl text-sm font-bold text-white text-center cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #c0392b, #7b241c)' }}
            >
              Emergency SOS
            </Link>
            {portal && (
              <Link
                to={portal.to}
                onClick={() => setOpen(false)}
                className="px-4 py-3 rounded-xl text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 border border-white/10 text-center cursor-pointer"
              >
                {portal.label}
              </Link>
            )}
            {user ? (
              <button
                onClick={() => { setOpen(false); handleLogout() }}
                className="px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-950/20 text-center cursor-pointer"
              >
                Sign out
              </button>
            ) : (
              <Link
                to="/login"
                onClick={() => setOpen(false)}
                className="px-4 py-3 rounded-xl text-sm font-medium text-white/70 border border-white/10 text-center cursor-pointer"
              >
                Sign in
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  )
}

function BloodDropIcon() {
  return (
    <svg width="34" height="40" viewBox="0 0 80 96" fill="none" aria-hidden="true"
      style={{ filter: 'drop-shadow(0 0 10px rgba(231,76,60,0.7))' }}>
      <path d="M40 8C40 8 8 44 8 64C8 82 22 88 40 88C58 88 72 82 72 64C72 44 40 8 40 8Z"
        fill="url(#ng)" />
      <circle cx="30" cy="60" r="5.5" fill="white" opacity=".9"/>
      <circle cx="50" cy="60" r="5.5" fill="white" opacity=".9"/>
      <circle cx="31.5" cy="58.5" r="2.2" fill="#1a0505"/>
      <circle cx="51.5" cy="58.5" r="2.2" fill="#1a0505"/>
      <path d="M30 70 Q40 78 50 70" stroke="white" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
      <circle cx="24" cy="66" r="4.5" fill="#ff9999" opacity=".4"/>
      <circle cx="56" cy="66" r="4.5" fill="#ff9999" opacity=".4"/>
      <defs>
        <linearGradient id="ng" x1="40" y1="8" x2="40" y2="88" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#ff4b4b"/>
          <stop offset="50%" stopColor="#e74c3c"/>
          <stop offset="100%" stopColor="#7b241c"/>
        </linearGradient>
      </defs>
    </svg>
  )
}
