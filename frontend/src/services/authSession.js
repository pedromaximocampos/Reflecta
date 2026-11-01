import { useSyncExternalStore } from 'react'

const EVENT = 'auth-session-changed'
export const SESSION_EXPIRED_EVENT = 'auth-session-expired'
const AUTH_STORAGE_KEYS = ['access_token', 'auth_user']
let expirationNotified = false

function removeAuthData() {
  for (const storage of [
    typeof sessionStorage === 'undefined' ? null : sessionStorage,
    typeof localStorage === 'undefined' ? null : localStorage,
  ]) {
    if (!storage) continue
    for (const key of AUTH_STORAGE_KEYS) storage.removeItem(key)
  }
}

function subscribe(callback) {
  window.addEventListener(EVENT, callback)
  window.addEventListener('storage', callback)
  return () => {
    window.removeEventListener(EVENT, callback)
    window.removeEventListener('storage', callback)
  }
}

export function saveSession(response) {
  expirationNotified = false
  sessionStorage.setItem('access_token', response.access_token)
  sessionStorage.setItem('auth_user', JSON.stringify(response.user))
  window.dispatchEvent(new Event(EVENT))
}

export function clearSession() {
  removeAuthData()
  window.dispatchEvent(new Event(EVENT))
}

export function hasStoredSession() {
  const token = sessionStorage.getItem('access_token')
  const user = readUser(sessionStorage.getItem('auth_user'))
  return Boolean(token && user)
}

export function expireSession(message = 'Suas credenciais expiraram. Entre novamente para continuar.') {
  removeAuthData()
  window.dispatchEvent(new Event(EVENT))
  if (expirationNotified) return
  expirationNotified = true
  window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT, {
    detail: { message },
  }))
}

export function updateSessionProfile(profile) {
  const user = readUser(sessionStorage.getItem('auth_user'))
  if (!user) return
  const { name, surname, date_of_birth, avatar_url } = profile
  sessionStorage.setItem('auth_user', JSON.stringify({
    ...user, name, surname, date_of_birth, avatar_url,
  }))
  window.dispatchEvent(new Event(EVENT))
}

function readUser(raw) {
  try {
    const user = JSON.parse(raw)
    return user && typeof user === 'object' && !Array.isArray(user) ? user : null
  } catch {
    return null
  }
}

export function useAuth() {
  const raw = useSyncExternalStore(subscribe, () => sessionStorage.getItem('auth_user'))
  const token = useSyncExternalStore(subscribe, () => sessionStorage.getItem('access_token'))
  const user = readUser(raw)
  const role = token && ['ADMIN', 'USER'].includes(user?.role) ? user.role : null
  // Used for presentation only. The server must enforce authorization.
  return { user, role, isAdmin: role === 'ADMIN', isAuthenticated: Boolean(token && user) }
}
