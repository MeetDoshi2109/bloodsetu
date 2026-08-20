import { createContext, useContext, useState, useCallback } from 'react'
import api from '../api/client'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(() => {
    try { return JSON.parse(localStorage.getItem('bs_user')) } catch { return null }
  })
  const [donor, setDonor]     = useState(null)
  const [loading, setLoading] = useState(false)

  const login = useCallback(async (username, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { username, password })
      localStorage.setItem('bs_token', data.token)
      localStorage.setItem('bs_user',  JSON.stringify(data.user))
      setUser(data.user)
      if (data.donor_data) setDonor(data.donor_data)
      return { ok: true }
    } catch (e) {
      return { ok: false, message: e.response?.data?.detail || 'Login failed' }
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (username, password, role, phone) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', { username, password, role, phone })
      return { ok: true, user_id: data.user_id }
    } catch (e) {
      return { ok: false, message: e.response?.data?.detail || 'Registration failed' }
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try { await api.post('/auth/logout') } catch {}
    localStorage.removeItem('bs_token')
    localStorage.removeItem('bs_user')
    setUser(null)
    setDonor(null)
  }, [])

  const refreshDonor = useCallback(async () => {
    try {
      const { data } = await api.get('/donor/profile')
      setDonor(data)
    } catch {}
  }, [])

  return (
    <AuthCtx.Provider value={{ user, donor, loading, login, register, logout, refreshDonor, setDonor }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuth = () => useContext(AuthCtx)
