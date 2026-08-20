import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach token automatically
api.interceptors.request.use(cfg => {
  const tok = localStorage.getItem('bs_token')
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`
  return cfg
})

// On 401 clear token
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
