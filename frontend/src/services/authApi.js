import { request } from './apiClient.js'
import { clearSession } from './authSession.js'

function encodeBasicCredentials(email, password) {
  const bytes = new TextEncoder().encode(`${email}:${password}`)
  let binary = ''

  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte)
  })

  return btoa(binary)
}

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    headers: {
      Authorization: `Basic ${encodeBasicCredentials(email, password)}`,
    },
  })
}

export async function logout() {
  try {
    await request('/auth/logoff', {
      method: 'POST',
      credentials: 'include',
    })
  } finally {
    clearSession()
  }
}

export function signup(user) {
  return request('/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(user),
  })
}

export function verifyEmail(code) {
  if (typeof code !== 'string' || !code.trim()) {
    const error = new Error('Abra o link de confirmação recebido por e-mail.')
    error.status = 400
    throw error
  }
  return request(`/auth/verify-email?${new URLSearchParams({ code: code.trim() })}`, {
    method: 'POST',
    credentials: 'omit',
  })
}

export function updateUserInfo(fields) {
  const token = sessionStorage.getItem('access_token')
  if (!token) {
    const error = new Error('Sua sessão expirou. Entre novamente para salvar o perfil.')
    error.status = 401
    throw error
  }
  return request('/auth/user-info', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(fields),
  })
}

function getAccessToken(message) {
  const token = sessionStorage.getItem('access_token')
  if (!token) {
    const error = new Error(message)
    error.status = 401
    throw error
  }
  return token
}

export function getUserProfile() {
  const token = getAccessToken('Sua sessão expirou. Entre novamente para acessar o perfil.')
  return request('/auth/user-info', {
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  })
}

export function uploadUserAvatar(file) {
  const token = getAccessToken('Sua sessão expirou. Entre novamente para alterar a foto.')
  const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp'])
  const allowedExtensions = /\.(jpe?g|png|webp)$/i
  if (!(file instanceof Blob) || !allowedTypes.has(file.type)
    || !allowedExtensions.test(file.name || '') || file.size <= 0 || file.size > 5 * 1024 * 1024) {
    const error = new Error('Escolha uma imagem JPEG, PNG ou WebP de até 5 MB.')
    error.status = 400
    throw error
  }
  const formData = new FormData()
  formData.append('avatar', file, file.name)
  return request('/auth/user-info/avatar', {
    method: 'PUT',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
}

export function removeUserAvatar() {
  const token = getAccessToken('Sua sessão expirou. Entre novamente para remover a foto.')
  return request('/auth/user-info/avatar', {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
}

export function requestPasswordReset(email) {
  return request('/auth/request-reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  })
}

export function resetPassword(resetToken, newPassword, repeatedPassword) {
  if (typeof resetToken !== 'string' || !resetToken.trim()) {
    const error = new Error('O link de redefinição está incompleto.')
    error.status = 400
    throw error
  }
  return request('/auth/reset-password', {
    method: 'POST',
    credentials: 'omit',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      reset_token: resetToken.trim(),
      new_password: newPassword,
      repeated_password: repeatedPassword,
    }),
  })
}

export function requestAccountRecovery(email) {
  return request('/auth/request-recovery', {
    method: 'POST',
    credentials: 'omit',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim() }),
  })
}

export function confirmAccountRecovery(code) {
  if (typeof code !== 'string' || !code.trim()) {
    const error = new Error('Abra o link de recuperação recebido por e-mail.')
    error.status = 400
    throw error
  }
  return request(`/auth/recovery?${new URLSearchParams({ code: code.trim() })}`, {
    method: 'POST',
    credentials: 'omit',
  })
}

export function requestAccountDeletion() {
  const token = sessionStorage.getItem('access_token')
  if (!token) {
    const error = new Error('Sua sessão expirou. Entre novamente para solicitar a exclusão.')
    error.status = 401
    throw error
  }
  return request('/auth/request-delete', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
}

export function confirmAccountDeletion(code) {
  if (typeof code !== 'string' || !code.trim()) {
    const error = new Error('Abra o link de confirmação recebido por e-mail.')
    error.status = 400
    throw error
  }
  return request(`/auth/delete?${new URLSearchParams({ code: code.trim() })}`, {
    method: 'DELETE',
    credentials: 'omit',
  })
}
