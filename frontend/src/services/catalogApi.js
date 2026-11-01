import { request } from './apiClient.js'

function adminRequest(path, options = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(`/catalog${path}`, { ...options, credentials: 'omit', headers: { Authorization: `Bearer ${token}`, ...options.headers } })
}

export function listThemes() { return adminRequest('/themes') }
export function getTheme(id) { return adminRequest(`/themes/${encodeURIComponent(id)}`) }
export function createTheme(theme) { return adminRequest('/themes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ themes: [theme] }) }) }
export function updateTheme(id, fields) { return adminRequest(`/themes/${encodeURIComponent(id)}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(fields) }) }
export function deleteTheme(id) { return adminRequest(`/themes/${encodeURIComponent(id)}`, { method: 'DELETE' }) }

const json = (method, fields) => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(fields) })
export function listWorks() { return adminRequest('/works') }
export function listWorkIngestions(limit = 50) {
  const query = new URLSearchParams({ limit: String(limit) })
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(`/ai-processing/work-ingestions?${query}`, {
    credentials: 'omit',
    headers: { Authorization: `Bearer ${token}` },
  })
}
export function getWork(id) { return adminRequest(`/works/${encodeURIComponent(id)}`) }
export function createWork(fields) { return adminRequest('/works', json('POST', fields)) }
export function uploadWorkCover(id, file) {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!file || !file.size || file.size > 5 * 1024 * 1024 || !allowedTypes.includes(file.type) || !/\.(jpe?g|png|webp)$/i.test(file.name)) return Promise.reject(new Error('Selecione uma imagem JPEG, PNG ou WebP não vazia, de até 5 MB.'))
  const body = new FormData()
  body.append('cover', file)
  return adminRequest(`/works/${encodeURIComponent(id)}/cover`, { method: 'PUT', body })
}
export function removeWorkCover(id) { return adminRequest(`/works/${encodeURIComponent(id)}/cover`, { method: 'DELETE' }) }
export function uploadWork(id, file) {
  if (!file || !file.size || file.type !== 'application/pdf' || !/\.pdf$/i.test(file.name)) return Promise.reject(new Error('Selecione um PDF não vazio, com extensão .pdf e tipo application/pdf.'))
  const body = new FormData()
  body.append('document', file)
  return adminRequest(`/works/${encodeURIComponent(id)}/ingestions`, { method: 'POST', body })
}
export function listPassages(filters = {}) {
  const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value))
  return adminRequest(`/passages?${query}`)
}
export function getPassage(id) { return adminRequest(`/passages/${encodeURIComponent(id)}`) }
export function createPassage(fields) { return adminRequest('/passages', json('POST', fields)) }
export function updatePassage(id, fields) { return adminRequest(`/passages/${encodeURIComponent(id)}`, json('PATCH', fields)) }
export function passageAction(id, action) {
  if (!['approve', 'reject', 'activate', 'deactivate'].includes(action)) throw new Error('Ação inválida.')
  return adminRequest(`/passages/${encodeURIComponent(id)}/${action}`, { method: 'POST' })
}
export function deletePassage(id) { return adminRequest(`/passages/${encodeURIComponent(id)}`, { method: 'DELETE' }) }
