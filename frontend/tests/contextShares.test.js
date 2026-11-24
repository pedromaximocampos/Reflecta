import test from 'node:test'
import assert from 'node:assert/strict'
import { buildContextShareLink, createContextShare, createProfessionalActivities, listContextShares, listOwnerContextShares, resolveContextShare, revokeContextShare, rotateContextShareToken } from '../src/services/contextSharesApi.js'

test('owner confirms creation, lists metadata and revokes with authenticated requests', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => { calls.push({ url, ...options }); return { ok: true, json: async () => ({}) } }
  try {
    await createContextShare('analysis/id')
    assert.deepEqual(JSON.parse(calls[0].body), { confirmed: true, include_journals: false })
    assert.equal(calls[0].method, 'POST')
    await listContextShares('analysis/id')
    await revokeContextShare('analysis/id', 'share/id')
    assert.equal(calls[2].method, 'DELETE')
    assert.match(calls[2].url, /analysis%2Fid\/shares\/share%2Fid$/)
    await rotateContextShareToken('analysis/id', 'share/id')
    assert.equal(calls[3].method, 'POST')
    assert.match(calls[3].url, /analysis%2Fid\/shares\/share%2Fid\/rotate$/)
    for (const call of calls) {
      assert.equal(call.credentials, 'omit')
      assert.equal(call.cache, 'no-store')
      assert.equal(call.headers.Authorization, 'Bearer owner-token')
    }
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(createContextShare('id'), { status: 401 })
    await assert.rejects(listContextShares('id'), { status: 401 })
    await assert.rejects(revokeContextShare('id', 'id'), { status: 401 })
    assert.equal(calls.length, 4)
  } finally { globalThis.fetch = previousFetch; globalThis.sessionStorage = previousStorage }
})

test('owner must explicitly request journal snapshots in a shared analysis', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let body
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (_url, options) => {
    body = JSON.parse(options.body)
    return { ok: true, json: async () => ({}) }
  }
  try {
    await createContextShare('analysis-id', { includeJournals: true })
    assert.deepEqual(body, { confirmed: true, include_journals: true })
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('receiver resolves without credentials; token is in fragment and POST body, never request URL', async () => {
  const previousFetch = globalThis.fetch
  const calls = []
  const token = 'a'.repeat(43)
  globalThis.fetch = async (url, options) => { calls.push({ url, ...options }); return { ok: true, json: async () => ({ result: {} }) } }
  try {
    const link = new URL(buildContextShareLink(token, 'https://reflecta.example'))
    assert.equal(link.pathname, '/compartilhamento')
    assert.equal(link.search, '')
    assert.equal(new URLSearchParams(link.hash.slice(1)).get('token'), token)
    await resolveContextShare(token)
    assert.equal(calls[0].url.includes(token), false)
    assert.deepEqual(JSON.parse(calls[0].body), { token })
    assert.equal(calls[0].headers.Authorization, undefined)
    assert.equal(calls[0].credentials, 'omit')
    assert.equal(calls[0].referrerPolicy, 'no-referrer')
  } finally { globalThis.fetch = previousFetch }
})

test('unavailable links remain errors with no automatic generation or send action', async () => {
  const previousFetch = globalThis.fetch
  let calls = 0
  globalThis.fetch = async () => { calls++; return { ok: false, status: 404, json: async () => ({ detail: 'Compartilhamento indisponível.' }) } }
  try {
    await assert.rejects(resolveContextShare('x'.repeat(43)), { status: 404 })
    assert.equal(calls, 1)
  } finally { globalThis.fetch = previousFetch }
})

test('professional guidance batches activities in one private POST', async () => {
  const previousFetch = globalThis.fetch
  const token = 'a'.repeat(43)
  let call
  globalThis.fetch = async (url, options) => {
    call = { url, ...options }
    return new Response(JSON.stringify({ count: 2, activities: [] }), { status: 201 })
  }
  try {
    await createProfessionalActivities(token, [
      {
        kind: 'activity',
        title: 'Observar escolhas',
        description: 'Observe uma escolha possível.',
        dueDate: '',
      },
      {
        kind: 'guided_reflection',
        title: 'Refletir sobre escolhas',
        description: 'Escreva sobre uma escolha possível.',
        dueDate: '2026-11-15',
      },
    ])
    assert.equal(new URL(call.url).pathname, '/shared/professional-activities')
    assert.equal(call.url.includes(token), false)
    assert.equal(call.method, 'POST')
    assert.equal(call.credentials, 'omit')
    assert.equal(call.referrerPolicy, 'no-referrer')
    assert.deepEqual(JSON.parse(call.body), {
      token,
      activities: [
        {
          kind: 'activity',
          title: 'Observar escolhas',
          description: 'Observe uma escolha possível.',
          due_date: null,
        },
        {
          kind: 'guided_reflection',
          title: 'Refletir sobre escolhas',
          description: 'Escreva sobre uma escolha possível.',
          due_date: '2026-11-15',
        },
      ],
    })
  } finally { globalThis.fetch = previousFetch }
})

test('owner lists all shares with server-side status and pagination', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let call
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => {
    call = { url, ...options }
    return new Response(JSON.stringify({ shares: [], total: 0 }))
  }
  try {
    await listOwnerContextShares({ state: 'active', limit: 6, offset: 12 })
    const url = new URL(call.url)
    assert.equal(url.pathname, '/journal/context-shares')
    assert.equal(url.searchParams.get('state'), 'active')
    assert.equal(url.searchParams.get('limit'), '6')
    assert.equal(url.searchParams.get('offset'), '12')
    assert.equal(call.headers.Authorization, 'Bearer owner-token')
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})
