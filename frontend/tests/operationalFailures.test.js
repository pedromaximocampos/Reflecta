import test from 'node:test'
import assert from 'node:assert/strict'
import { listOperationalFailures, getOperationalFailure, getAnalysisProcessingSettings, reprocessOperationalFailure } from '../src/services/operationalFailuresApi.js'

test('admin failures authenticates, filters safely and requests encoded details', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'admin-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => ({ failures: [], total: 0 }) }
  }
  try {
    const controller = new AbortController()
    await listOperationalFailures({ source: 'journal', state: 'analysis_failed', entity_id: 'a/b', since: '2026-10-27T12:00:00Z', limit: 20, offset: 40, ignored: 'secret', until: '' }, { signal: controller.signal })
    const url = new URL(calls[0].url)
    assert.equal(url.pathname, '/admin/operational-failures')
    assert.equal(url.searchParams.get('entity_id'), 'a/b')
    assert.equal(url.searchParams.get('offset'), '40')
    assert.equal(url.searchParams.get('source'), 'journal')
    assert.equal(url.searchParams.has('ignored'), false)
    assert.equal(url.searchParams.has('until'), false)
    assert.equal(calls[0].signal, controller.signal)
    await getOperationalFailure('inbox', 'consumer:event/id', { signal: controller.signal })
    assert.match(calls[1].url, /\/inbox\/consumer%3Aevent%2Fid$/)
    for (const call of calls) {
      assert.equal(call.headers.Authorization, 'Bearer admin-token')
      assert.equal(call.credentials, 'omit')
      assert.equal(call.method, undefined)
      assert.equal(call.body, undefined)
    }
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(listOperationalFailures(), { status: 401 })
    await assert.rejects(getOperationalFailure('journal', 'id'), { status: 401 })
    assert.equal(calls.length, 2)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('forbidden, unavailable and missing failures remain errors with no automatic retry', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let calls = 0
  globalThis.sessionStorage = { getItem: () => 'token' }
  try {
    for (const status of [403, 503, 404]) {
      globalThis.fetch = async () => { calls++; return { ok: false, status, json: async () => ({ detail: 'Consulta recusada.' }) } }
      await assert.rejects(getOperationalFailure('journal', 'id'), { status, message: 'Consulta recusada.' })
    }
    assert.equal(calls, 3)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('admin reprocessing uses an explicit authenticated POST and encodes failure id', async () => {
  const { reprocessOperationalFailure } = await import('../src/services/operationalFailuresApi.js')
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'admin-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => ({ status: 'pending_analysis', already_pending: false }) }
  }
  try {
    assert.equal((await reprocessOperationalFailure('failure/id')).status, 'pending_analysis')
    assert.match(calls[0].url, /\/journal\/failure%2Fid\/reprocess$/)
    assert.equal(calls[0].method, 'POST')
    assert.equal(calls[0].headers.Authorization, 'Bearer admin-token')
    assert.equal(calls[0].credentials, 'omit')
    assert.equal(calls[0].body, undefined)
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(reprocessOperationalFailure('id'), { status: 401 })
    assert.equal(calls.length, 1)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('admin retry sends validated settings as JSON and never forwards a key', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  const settings = { model: 'gpt-6-luna', timeout_seconds: 60, max_output_tokens: 12000, reasoning_effort: 'low' }
  globalThis.sessionStorage = { getItem: () => 'admin-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => settings }
  }
  try {
    assert.deepEqual(await getAnalysisProcessingSettings(), settings)
    assert.match(calls[0].url, /\/analysis-settings$/)
    await reprocessOperationalFailure('failure', { ...settings, api_key: 'must-not-be-forwarded' })
    assert.equal(calls[1].headers['Content-Type'], 'application/json')
    assert.equal(calls[1].headers.Authorization, 'Bearer admin-token')
    assert.deepEqual(JSON.parse(calls[1].body), settings)
    assert.equal(calls.length, 2)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})
