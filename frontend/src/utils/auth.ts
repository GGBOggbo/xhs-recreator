/**
 * 认证工具 — Token 管理 + axios 拦截器 + auth API 封装
 */

import axios from 'axios'

// ---------- Token 管理 ----------

const TOKEN_KEY = 'xhs_token'
const USER_KEY = 'xhs_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated(): boolean {
  return !!getToken()
}

export function getCurrentUser(): Record<string, unknown> | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function login(token: string, user: Record<string, unknown>): void {
  setToken(token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function logout(): void {
  removeToken()
  sessionStorage.removeItem('xhs_current_step')
  window.location.reload()
}

// ---------- axios 实例 + 拦截器 ----------

export const api = axios.create()

// 请求拦截：自动带 Token
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 → 清 Token + 刷新页面
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken()
      sessionStorage.removeItem('xhs_current_step')
      window.location.reload()
    }
    return Promise.reject(error)
  },
)

// ---------- auth API 封装 ----------

export const authApi = {
  register(data: { username: string; password: string }) {
    return axios.post('/api/auth/register', data)
  },

  login(data: { username: string; password: string }) {
    return axios.post('/api/auth/login', data)
  },

  getMe() {
    return api.get('/api/auth/me')
  },

  saveCookie(data: { cookies: string }) {
    return api.put('/api/auth/cookie', data)
  },

  checkCookie() {
    return api.post('/api/auth/cookie/check')
  },

  getCookieStatus() {
    return api.get('/api/auth/cookie')
  },
}
