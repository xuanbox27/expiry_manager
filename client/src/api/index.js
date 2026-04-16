import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateSettings: (data) => api.put('/auth/settings', data)
}

export const itemsApi = {
  getAll: (params) => api.get('/items', { params }),
  getOne: (id) => api.get(`/items/${id}`),
  create: (data) => api.post('/items', data),
  update: (id, data) => api.put(`/items/${id}`, data),
  delete: (id) => api.delete(`/items/${id}`),
  scan: (barcode) => api.get(`/items/scan/${barcode}`),
  getBarcodes: () => api.get('/items/barcodes')
}

export const familyApi = {
  getMembers: () => api.get('/family/members'),
  join: (familyCode) => api.post('/family/join', { family_code: familyCode }),
  leave: () => api.post('/family/leave'),
  getInvite: () => api.post('/family/invite'),
  getItems: () => api.get('/family/items')
}

export const notificationsApi = {
  getAll: (unreadOnly) => api.get('/notifications', { params: { unread_only: unreadOnly } }),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
  delete: (id) => api.delete(`/notifications/${id}`)
}

export default api
