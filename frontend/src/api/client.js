import axios from 'axios'

// In development Vite proxies /api → localhost:8000.
// On Vercel both the static frontend and /api/* serverless function
// live on the same domain, so relative /api works in both environments.
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Attach Bearer token automatically
api.interceptors.request.use(cfg => {
  const tok = localStorage.getItem('bs_token')
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`
  return cfg
})

// On 401 clear local auth state
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('bs_token')
      localStorage.removeItem('bs_user')
    }
    return Promise.reject(err)
  }
)

export default api
