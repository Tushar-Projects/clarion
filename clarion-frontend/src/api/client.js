import axios from 'axios'

// point this to your Flask base URL
export const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  withCredentials: true
})

// Attach token if you decide to return JWTs from Flask
api.interceptors.request.use(cfg=>{
  const token = localStorage.getItem('clarion-token')
  if(token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
