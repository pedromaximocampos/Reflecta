import {
  clearSession,
  expireSession,
  hasStoredSession,
  saveSession,
} from './authSession.js'

const API_URL = (import.meta.env?.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
let refreshInFlight = null

async function readResponse(response) {
  return response.json().catch(() => null)
}

function responseError(response, data) {
  const domainError = data?.errors?.[0]
  const validationError = Array.isArray(data?.detail) ? data.detail[0] : null
  const message = domainError?.data
    || domainError?.title
    || validationError?.msg
    || (typeof data?.detail === 'string' ? data.detail : null)
    || data?.message
    || data?.error
    || 'Não foi possível concluir a solicitação.'

  const error = new Error(typeof message === 'string' ? message : 'Não foi possível concluir a solicitação.')
  error.status = response.status
  error.details = domainError?.details ?? null
  return error
}

function bearerToken(options) {
  const authorization = options.headers?.Authorization ?? options.headers?.authorization
  return typeof authorization === 'string' && authorization.startsWith('Bearer ')
}

async function refreshAccessToken() {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  const data = await readResponse(response)
  if (!response.ok || typeof data?.access_token !== 'string' || !data?.user) {
    throw responseError(response, data)
  }
  saveSession(data)
  return data.access_token
}

async function getRefreshedAccessToken() {
  if (!refreshInFlight) {
    refreshInFlight = refreshAccessToken().finally(() => {
      refreshInFlight = null
    })
  }
  return refreshInFlight
}

export async function restoreSessionFromCookie() {
  const hadStoredSession = hasStoredSession()
  try {
    await getRefreshedAccessToken()
    return true
  } catch {
    if (hadStoredSession) expireSession()
    else clearSession()
    return false
  }
}

export async function request(path, options = {}, alreadyRetried = false) {
  const response = await fetch(`${API_URL}${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      ...options.headers,
    },
  })

  const data = await readResponse(response)

  if (response.status === 401 && bearerToken(options) && alreadyRetried) {
    expireSession()
    const error = new Error('Sua sessão expirou. Entre novamente.')
    error.status = 401
    throw error
  }

  if (response.status === 401 && bearerToken(options)) {
    let accessToken
    try {
      accessToken = await getRefreshedAccessToken()
    } catch {
      expireSession()
      const error = new Error('Sua sessão expirou. Entre novamente.')
      error.status = 401
      throw error
    }

    return request(
      path,
      {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${accessToken}`,
        },
      },
      true,
    )
  }

  if (!response.ok) {
    throw responseError(response, data)
  }

  return data
}

function downloadFilename(response) {
  const disposition = response.headers.get('Content-Disposition') || ''
  const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match) {
    try {
      return decodeURIComponent(utf8Match[1])
    } catch {
      return utf8Match[1]
    }
  }
  return disposition.match(/filename="([^"]+)"/i)?.[1]
    || disposition.match(/filename=([^;]+)/i)?.[1]?.trim()
    || null
}

export async function requestBlob(path, options = {}, alreadyRetried = false) {
  const response = await fetch(`${API_URL}${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      ...options.headers,
    },
  })

  if (response.status === 401 && bearerToken(options) && alreadyRetried) {
    expireSession()
    const error = new Error('Sua sessão expirou. Entre novamente.')
    error.status = 401
    throw error
  }

  if (response.status === 401 && bearerToken(options)) {
    let accessToken
    try {
      accessToken = await getRefreshedAccessToken()
    } catch {
      expireSession()
      const error = new Error('Sua sessão expirou. Entre novamente.')
      error.status = 401
      throw error
    }
    return requestBlob(
      path,
      {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${accessToken}`,
        },
      },
      true,
    )
  }

  if (!response.ok) {
    throw responseError(response, await readResponse(response))
  }

  return {
    blob: await response.blob(),
    filename: downloadFilename(response),
  }
}

