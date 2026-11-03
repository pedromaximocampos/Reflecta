import { request } from './apiClient.js'

function contextualRequest(options = {}, path = '') {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(`/journal/context-analysis${path}`, { ...options, credentials: 'omit', headers: { Authorization: `Bearer ${token}`, ...options.headers } })
}

export function getContextAnalysis(period, { signal } = {}) {
  return contextualRequest({ signal }, `?${new URLSearchParams(period)}`)
}
export function submitContextAnalysis(period) {
  return contextualRequest({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(period) })
}

export function listContextAnalyses({ limit = 5, offset = 0, signal } = {}) {
  return contextualRequest({ signal }, `/history?${new URLSearchParams({ limit, offset })}`)
}
