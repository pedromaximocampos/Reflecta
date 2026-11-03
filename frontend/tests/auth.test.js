import { test, beforeEach } from 'node:test'
import assert from 'node:assert/strict'
import {
  confirmAccountDeletion,
  confirmAccountRecovery,
  getUserProfile,
  login,
  logout,
  removeUserAvatar,
  requestAccountDeletion,
  requestAccountRecovery,
  resetPassword,
  updateUserInfo,
  uploadUserAvatar,
  verifyEmail,
} from '../src/services/authApi.js'
import {
  clearSession,
  expireSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
  updateSessionProfile,
} from '../src/services/authSession.js'
import { restoreSessionFromCookie } from '../src/services/apiClient.js'

beforeEach(() => {
  const data = new Map()
  globalThis.sessionStorage = {
    getItem: (key) => data.get(key) ?? null,
    setItem: (key, value) => data.set(key, value),
    removeItem: (key) => data.delete(key),
  }
  const localData = new Map()
  globalThis.localStorage = {
    getItem: (key) => localData.get(key) ?? null,
    setItem: (key, value) => localData.set(key, value),
    removeItem: (key) => localData.delete(key),
  }
  globalThis.window = new EventTarget()
})

test('expired session clears only authentication data and emits one global notification', () => {
  saveSession({
    access_token: 'access-token',
    user: { name: 'Ana', role: 'USER' },
  })
  localStorage.setItem('access_token', 'legacy-access-token')
  localStorage.setItem('auth_user', '{"name":"Legacy"}')
  localStorage.setItem('unrelated_preference', 'keep-me')
  let notifications = 0
  let message = ''
  window.addEventListener(SESSION_EXPIRED_EVENT, (event) => {
    notifications += 1
    message = event.detail.message
  })

  expireSession()
  expireSession()

  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
  assert.equal(localStorage.getItem('access_token'), null)
  assert.equal(localStorage.getItem('auth_user'), null)
  assert.equal(localStorage.getItem('unrelated_preference'), 'keep-me')
  assert.equal(notifications, 1)
  assert.match(message, /credenciais expiraram/i)
})

test('application bootstrap restores a session using only the HttpOnly refresh cookie', async () => {
  let refreshCalls = 0
  globalThis.fetch = async (url, options) => {
    refreshCalls += 1
    assert.equal(url, 'http://localhost:8000/auth/refresh')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'include')
    assert.equal(options.headers, undefined)
    return new Response(JSON.stringify({
      access_token: 'restored-access-token',
      user: { name: 'Ana', role: 'ADMIN' },
    }))
  }

  assert.equal(await restoreSessionFromCookie(), true)
  assert.equal(refreshCalls, 1)
  assert.equal(sessionStorage.getItem('access_token'), 'restored-access-token')
  assert.equal(JSON.parse(sessionStorage.getItem('auth_user')).role, 'ADMIN')
})

test('application bootstrap fails silently when no previous local session exists', async () => {
  let notifications = 0
  window.addEventListener(SESSION_EXPIRED_EVENT, () => {
    notifications += 1
  })
  globalThis.fetch = async () => new Response(
    JSON.stringify({ error: 'Refresh cookie not found' }),
    { status: 401 },
  )

  assert.equal(await restoreSessionFromCookie(), false)
  assert.equal(notifications, 0)
  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('application bootstrap reports expiration when a previous local session cannot be restored', async () => {
  saveSession({
    access_token: 'stale-access-token',
    user: { name: 'Ana', role: 'USER' },
  })
  let notifications = 0
  window.addEventListener(SESSION_EXPIRED_EVENT, () => {
    notifications += 1
  })
  globalThis.fetch = async () => new Response(
    JSON.stringify({ error: 'Invalid refresh token' }),
    { status: 401 },
  )

  assert.equal(await restoreSessionFromCookie(), false)
  assert.equal(notifications, 1)
  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('recovery request sends only email without credentials and does not create a session', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'http://localhost:8000/auth/request-recovery')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'omit')
    assert.equal(options.headers.Authorization, undefined)
    assert.deepEqual(JSON.parse(options.body), { email: 'ana@example.com' })
    return new Response('{}', { status: 202 })
  }
  await requestAccountRecovery(' ana@example.com ')
  assert.equal(sessionStorage.getItem('access_token'), null)
})

test('recovery confirmation encodes the email code and does not authenticate automatically', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(new URL(url).pathname, '/auth/recovery')
    assert.equal(new URL(url).searchParams.get('code'), 'a+b&c=?')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'omit')
    assert.equal(options.headers.Authorization, undefined)
    return new Response('{}')
  }
  await confirmAccountRecovery('a+b&c=?')
  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('missing recovery codes never call the API', () => {
  globalThis.fetch = () => assert.fail('Should not call API')
  for (const code of [undefined, null, '', '  ']) {
    assert.throws(() => confirmAccountRecovery(code), { status: 400 })
  }
})

test('recovery validation and server failures remain errors', async () => {
  for (const status of [400, 422, 500]) {
    globalThis.fetch = async () => new Response('{}', { status })
    await assert.rejects(confirmAccountRecovery('expired'), { status })
    await assert.rejects(requestAccountRecovery('ana@example.com'), { status })
  }
})

test('profile PATCH sends the access token and partial JSON body', async () => {
  sessionStorage.setItem('access_token', 'access-test')
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'http://localhost:8000/auth/user-info')
    assert.equal(options.method, 'PATCH')
    assert.equal(options.headers.Authorization, 'Bearer access-test')
    assert.deepEqual(JSON.parse(options.body), { surname: 'Silva' })
    return new Response(JSON.stringify({ name: 'Ana', surname: 'Silva' }))
  }
  assert.equal((await updateUserInfo({ surname: 'Silva' })).surname, 'Silva')
})

test('expired access token refreshes once and retries the protected request', async () => {
  saveSession({
    access_token: 'expired-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  let protectedCalls = 0
  let refreshCalls = 0
  globalThis.fetch = async (url, options) => {
    const path = new URL(url).pathname
    if (path === '/auth/refresh') {
      refreshCalls += 1
      assert.equal(options.method, 'POST')
      assert.equal(options.credentials, 'include')
      assert.equal(options.headers, undefined)
      return new Response(JSON.stringify({
        access_token: 'renewed-token',
        user: { name: 'Ana', surname: 'Silva', role: 'USER', avatar_url: null },
      }))
    }
    assert.equal(path, '/auth/user-info')
    protectedCalls += 1
    if (protectedCalls === 1) {
      assert.equal(options.headers.Authorization, 'Bearer expired-token')
      return new Response(JSON.stringify({ detail: 'Expired' }), { status: 401 })
    }
    assert.equal(options.headers.Authorization, 'Bearer renewed-token')
    return new Response(JSON.stringify({
      name: 'Ana Maria', surname: 'Silva', date_of_birth: '2000-01-01', avatar_url: null,
    }))
  }

  const profile = await updateUserInfo({ name: 'Ana Maria' })

  assert.equal(profile.name, 'Ana Maria')
  assert.equal(refreshCalls, 1)
  assert.equal(protectedCalls, 2)
  assert.equal(sessionStorage.getItem('access_token'), 'renewed-token')
  assert.equal(JSON.parse(sessionStorage.getItem('auth_user')).role, 'USER')
})

test('concurrent unauthorized requests share one refresh rotation', async () => {
  saveSession({
    access_token: 'expired-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  let refreshCalls = 0
  globalThis.fetch = async (url, options) => {
    const path = new URL(url).pathname
    if (path === '/auth/refresh') {
      refreshCalls += 1
      await new Promise((resolve) => setTimeout(resolve, 5))
      return new Response(JSON.stringify({
        access_token: 'renewed-token',
        user: { name: 'Ana', surname: 'Silva', role: 'USER' },
      }))
    }
    if (options.headers.Authorization === 'Bearer expired-token') {
      return new Response('{}', { status: 401 })
    }
    return new Response(JSON.stringify({
      name: 'Ana', surname: 'Silva', date_of_birth: '2000-01-01', avatar_url: null,
    }))
  }

  await Promise.all([getUserProfile(), getUserProfile()])

  assert.equal(refreshCalls, 1)
})

test('failed refresh clears the local session without retry loop', async () => {
  saveSession({
    access_token: 'expired-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  let calls = 0
  globalThis.fetch = async (url) => {
    calls += 1
    if (new URL(url).pathname === '/auth/refresh') {
      return new Response(JSON.stringify({ error: 'Invalid refresh token' }), { status: 401 })
    }
    return new Response('{}', { status: 401 })
  }

  await assert.rejects(getUserProfile(), {
    status: 401,
    message: 'Sua sessão expirou. Entre novamente.',
  })

  assert.equal(calls, 2)
  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('a rejected retried request clears the session without a second refresh', async () => {
  saveSession({
    access_token: 'expired-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  let refreshCalls = 0
  let protectedCalls = 0
  globalThis.fetch = async (url) => {
    if (new URL(url).pathname === '/auth/refresh') {
      refreshCalls += 1
      return new Response(JSON.stringify({
        access_token: 'renewed-token',
        user: { name: 'Ana', surname: 'Silva', role: 'USER' },
      }))
    }
    protectedCalls += 1
    return new Response('{}', { status: 401 })
  }

  await assert.rejects(getUserProfile(), {
    status: 401,
    message: 'Sua sessão expirou. Entre novamente.',
  })

  assert.equal(refreshCalls, 1)
  assert.equal(protectedCalls, 2)
  assert.equal(sessionStorage.getItem('access_token'), null)
})

test('an application error after a successful refresh is not treated as session expiration', async () => {
  saveSession({
    access_token: 'expired-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  let protectedCalls = 0
  globalThis.fetch = async (url) => {
    if (new URL(url).pathname === '/auth/refresh') {
      return new Response(JSON.stringify({
        access_token: 'renewed-token',
        user: { name: 'Ana', surname: 'Silva', role: 'USER' },
      }))
    }
    protectedCalls += 1
    return protectedCalls === 1
      ? new Response('{}', { status: 401 })
      : new Response(JSON.stringify({ error: 'Profile service unavailable' }), { status: 503 })
  }

  await assert.rejects(getUserProfile(), {
    status: 503,
    message: 'Profile service unavailable',
  })

  assert.equal(sessionStorage.getItem('access_token'), 'renewed-token')
  assert.equal(JSON.parse(sessionStorage.getItem('auth_user')).role, 'USER')
})

test('logout sends the refresh cookie and always clears the local session', async () => {
  saveSession({
    access_token: 'access-token',
    user: { name: 'Ana', surname: 'Silva', role: 'USER' },
  })
  globalThis.fetch = async (url, options) => {
    assert.equal(new URL(url).pathname, '/auth/logoff')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'include')
    assert.equal(options.headers.Authorization, undefined)
    return new Response(JSON.stringify({ message: 'ok' }))
  }

  await logout()

  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('profile avatar uses authenticated multipart upload and removal endpoints', async () => {
  sessionStorage.setItem('access_token', 'access-test')
  const calls = []
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })
    return new Response(JSON.stringify({
      name: 'Ana', surname: 'Silva', date_of_birth: '2000-01-01', avatar_url: null,
    }))
  }
  const file = new File([new Uint8Array([1, 2, 3])], 'avatar.png', { type: 'image/png' })

  await getUserProfile()
  await uploadUserAvatar(file)
  await removeUserAvatar()

  assert.equal(calls[0].url, 'http://localhost:8000/auth/user-info')
  assert.equal(calls[0].options.method, 'GET')
  assert.equal(calls[1].url, 'http://localhost:8000/auth/user-info/avatar')
  assert.equal(calls[1].options.method, 'PUT')
  assert.equal(calls[1].options.headers.Authorization, 'Bearer access-test')
  assert.ok(calls[1].options.body instanceof FormData)
  assert.equal(calls[1].options.body.get('avatar').name, 'avatar.png')
  assert.equal(calls[1].options.headers['Content-Type'], undefined)
  assert.equal(calls[2].options.method, 'DELETE')
  assert.equal(calls[2].options.headers.Authorization, 'Bearer access-test')
})

test('profile avatar rejects invalid files before contacting the API', () => {
  sessionStorage.setItem('access_token', 'access-test')
  globalThis.fetch = () => assert.fail('Should not call API')

  const invalid = new File([new Uint8Array([1])], 'avatar.svg', { type: 'image/svg+xml' })
  assert.throws(() => uploadUserAvatar(invalid), { status: 400 })
})

test('missing session does not send a request', () => {
  globalThis.fetch = () => assert.fail('Should not call API')
  assert.throws(() => updateUserInfo({ name: 'Ana' }), { status: 401 })
})

test('validation errors and expired sessions preserve HTTP status', async () => {
  for (const status of [401, 422, 500]) {
    sessionStorage.setItem('access_token', 'access-test')
    globalThis.fetch = async () => new Response(JSON.stringify({ detail: [{ msg: 'Falha' }] }), { status })
    const expectedMessage = status === 401 ? 'Sua sessão expirou. Entre novamente.' : 'Falha'
    await assert.rejects(updateUserInfo({ name: 'Ana' }), { status, message: expectedMessage })
  }
})

test('profile updates preserve identity and role and cannot promote the user', () => {
  saveSession({ access_token: 'token', user: { email: 'ana@example.com', role: 'USER', name: 'Ana' } })
  updateSessionProfile({ name: 'Ana Maria', surname: 'Silva', role: 'ADMIN' })
  const user = JSON.parse(sessionStorage.getItem('auth_user'))
  assert.equal(user.name, 'Ana Maria')
  assert.equal(user.email, 'ana@example.com')
  assert.equal(user.role, 'USER')
  clearSession()
  assert.equal(sessionStorage.getItem('access_token'), null)
  assert.equal(sessionStorage.getItem('auth_user'), null)
})

test('deletion request authenticates the current user without a client-supplied identity', async () => {
  sessionStorage.setItem('access_token', 'access-test')
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'http://localhost:8000/auth/request-delete')
    assert.equal(options.method, 'POST')
    assert.equal(options.headers.Authorization, 'Bearer access-test')
    assert.equal(options.body, undefined)
    return new Response('{}', { status: 202 })
  }
  await requestAccountDeletion()
  assert.equal(sessionStorage.getItem('access_token'), 'access-test')
})

test('deletion request without a session does not call the API', () => {
  globalThis.fetch = () => assert.fail('Should not call API')
  assert.throws(() => requestAccountDeletion(), { status: 401 })
})

test('deletion confirmation uses the encoded email code and works without login', async () => {
  globalThis.fetch = async (url, options) => {
    const parsed = new URL(url)
    assert.equal(parsed.pathname, '/auth/delete')
    assert.equal(parsed.searchParams.get('code'), 'code+with&special=?')
    assert.equal(options.method, 'DELETE')
    assert.equal(options.credentials, 'omit')
    assert.equal(options.headers.Authorization, undefined)
    return new Response('{}', { status: 200 })
  }
  await confirmAccountDeletion('code+with&special=?')
})

test('missing deletion codes never trigger a request', () => {
  globalThis.fetch = () => assert.fail('Should not call API')
  for (const code of [undefined, null, '', '  ']) {
    assert.throws(() => confirmAccountDeletion(code), { status: 400 })
  }
})

test('invalid or reused deletion codes and service failures remain errors', async () => {
  for (const status of [400, 500]) {
    globalThis.fetch = async () => new Response('{}', { status })
    await assert.rejects(confirmAccountDeletion('expired'), { status })
  }
})

test('login preserves role and birth date for navigation and profile editing', async () => {
  const user = { name: 'Ana', surname: 'Silva', email: 'ana@example.com', username: 'ana', role: 'ADMIN', date_of_birth: '2000-01-01', avatar_url: null }
  globalThis.fetch = async (url, options) => {
    assert.equal(new URL(url).pathname, '/auth/login')
    assert.equal(options.method, 'POST')
    assert.equal(options.headers.Authorization, `Basic ${btoa('ana@example.com:test-password')}`)
    return new Response(JSON.stringify({ access_token: 'token', user }))
  }
  saveSession(await login('ana@example.com', 'test-password'))
  assert.deepEqual(JSON.parse(sessionStorage.getItem('auth_user')), user)
  updateSessionProfile({ name: 'Ana Maria', surname: 'Silva', date_of_birth: '2001-02-03', avatar_url: null })
  const updated = JSON.parse(sessionStorage.getItem('auth_user'))
  assert.equal(updated.role, 'ADMIN')
  assert.equal(updated.date_of_birth, '2001-02-03')
})

test('API errors support domain, FastAPI and refresh response formats', async () => {
  const failures = [
    [400, { errors: [{ title: 'Invalid code', data: 'Código expirado' }] }, 'Código expirado'],
    [401, { detail: 'Invalid or expired token' }, 'Invalid or expired token'],
    [422, { detail: [{ msg: 'E-mail inválido' }] }, 'E-mail inválido'],
    [401, { error: 'Token de atualização não fornecido.' }, 'Token de atualização não fornecido.'],
  ]
  for (const [status, body, message] of failures) {
    globalThis.fetch = async () => new Response(JSON.stringify(body), { status })
    await assert.rejects(confirmAccountRecovery('code'), { status, message })
  }
})

test('password reset sends URL code as reset_token and both password fields', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'http://localhost:8000/auth/reset-password')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'omit')
    assert.deepEqual(JSON.parse(options.body), {
      reset_token: 'code-from-email',
      new_password: 'new-password-123',
      repeated_password: 'new-password-123',
    })
    return new Response(JSON.stringify({ message: 'Password has been reset successfully.' }))
  }
  await resetPassword(' code-from-email ', 'new-password-123', 'new-password-123')
})

test('password reset rejects a missing code before contacting the API', async () => {
  globalThis.fetch = () => assert.fail('Missing reset code must not call the API')
  assert.throws(() => resetPassword('  ', 'new-password-123', 'new-password-123'), { status: 400 })
})


test('email verification posts an encoded code without session credentials', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(new URL(url).pathname, '/auth/verify-email')
    assert.equal(new URL(url).searchParams.get('code'), 'a+b&c=?')
    assert.equal(options.method, 'POST')
    assert.equal(options.credentials, 'omit')
    assert.equal(options.headers.Authorization, undefined)
    return new Response(JSON.stringify({ message: 'Email verified successfully' }))
  }
  await verifyEmail('a+b&c=?')
  assert.equal(sessionStorage.getItem('access_token'), null)
})

test('email verification rejects missing codes without calling the API', () => {
  globalThis.fetch = () => assert.fail('Should not call API')
  for (const code of [undefined, null, '', '  ']) assert.throws(() => verifyEmail(code))
})
