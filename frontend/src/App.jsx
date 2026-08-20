import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

// Pages
import Home          from './pages/Home'
import FindBlood     from './pages/FindBlood'
import Eligibility   from './pages/Eligibility'
import Analytics     from './pages/Analytics'
import DaataWall     from './pages/DaataWall'
import Login         from './pages/Login'
import Register      from './pages/Register'
import Admin         from './pages/Admin'
import DonorPortal   from './pages/portals/DonorPortal'
import HospitalPortal from './pages/portals/HospitalPortal'
import BloodBankPortal from './pages/portals/BloodBankPortal'
import CampPortal    from './pages/portals/CampPortal'
import Layout        from './components/layout/Layout'

function ProtectedRoute({ children, role }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role && user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

function NotFound() {
  return (
    <Layout>
      <div className="text-center py-32 space-y-4">
        <p className="text-8xl font-heading font-black text-blood-900">404</p>
        <h1 className="text-2xl font-heading font-bold text-white">Page not found</h1>
        <p className="text-white/40 text-sm">The page you're looking for doesn't exist.</p>
        <a href="/" className="inline-block mt-4 px-6 py-2.5 rounded-xl bg-blood-700/30 text-blood-300 border border-blood-700/40 text-sm font-semibold hover:bg-blood-700/50 transition-colors cursor-pointer">
          Go Home
        </a>
      </div>
    </Layout>
  )
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/"            element={<Layout><Home /></Layout>} />
      <Route path="/find-blood"  element={<FindBlood />} />
      <Route path="/eligibility" element={<Eligibility />} />
      <Route path="/analytics"   element={<Analytics />} />
      <Route path="/daata-wall"  element={<DaataWall />} />
      <Route path="/login"       element={<Login />} />
      <Route path="/register"    element={<Register />} />

      {/* Portals */}
      <Route path="/portal/donor"      element={<DonorPortal />} />
      <Route path="/portal/hospital"   element={<HospitalPortal />} />
      <Route path="/portal/blood-bank" element={<BloodBankPortal />} />
      <Route path="/portal/camp"       element={<CampPortal />} />

      {/* Admin */}
      <Route path="/admin" element={
        <ProtectedRoute role="admin"><Admin /></ProtectedRoute>
      } />

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
