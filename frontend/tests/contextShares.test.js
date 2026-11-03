import test from 'node:test'
import assert from 'node:assert/strict'
import { createContextShare, listContextShares, revokeContextShare, resolveContextShare, buildContextShareLink } from '../src/services/contextSharesApi.js'

test('owner confirms creation, lists metadata and revokes with authenticated requests', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => { calls.push({ url, ...options }); return { ok: true, json: async () => ({}) } }
  try {
    await createContextShare('analysis/id')
    assert.deepEqual(JSON.parse(calls[0].body), { confirmed: true })
    assert.equal(calls[0].method, 'POST')
    await listContextShares('analysis/id')
    await revokeContextShare('analysis/id', 'share/id')
    assert.equal(calls[2].method, 'DELETE')
    assert.match(calls[2].url, /analysis%2Fid\/shares\/share%2Fid$/)
    for (const call of calls) {
      assert.equal(call.credentials, 'omit')
      assert.equal(call.cache, 'no-store')
      assert.equal(call.headers.Authorization, 'Bearer owner-token')
    }
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(createContextShare('id'), { status: 401 })
    await assert.rejects(listContextShares('id'), { status: 401 })
    await assert.rejects(revokeContextShare('id', 'id'), { status: 401 })
    assert.equal(calls.length, 3)
  } finally { globalThis.fetch = previousFetch; globalThis.sessionStorage = previousStorage }
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
