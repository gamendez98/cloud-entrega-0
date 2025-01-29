import axios from 'axios'

const api = axios.create({
  baseURL: 'YOUR_API_BASE_URL'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authService = {
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/users/login', formData)
  },
  logout: () => api.post('/users/logout'),
  uploadImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/users/upload-image', formData)
  }
}

export const taskService = {
  create: (task) => api.post('/users/', task),
  delete: (taskId) => api.delete(`/users/${taskId}`),
  getUserTasks: (username) => api.get(`/usersuser/${username}`)
}

export const categoryService = {
  getAll: () => api.get('/categories/'),
  create: (category) => api.post('/categories/', category),
  update: (categoryId, category) => api.put(`/categories/${categoryId}`, category),
  delete: (categoryId) => api.delete(`/categories/${categoryId}`)
}

export default api