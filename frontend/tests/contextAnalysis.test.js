const PERIOD = { start_date: '2026-10-20', end_date: '2026-10-26' }
import test from 'node:test'
import assert from 'node:assert/strict'
import { getContextAnalysis, submitContextAnalysis } from '../src/services/contextAnalysisApi.js'

test('context status only reads; generation requires an explicit authenticated POST', async () => {
  const oldFetch = globalThis.fetch
  const oldStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => ({ eligible: true, analysis: null }) }
  }
  try {
    const controller = new AbortController()
    await getContextAnalysis(PERIOD, { signal: controller.signal })
    assert.equal(calls.length, 1)
    assert.equal(calls[0].method, undefined)
    assert.equal(calls[0].signal, controller.signal)
    await submitContextAnalysis(PERIOD)
    assert.equal(calls[1].method, 'POST')
    for (const call of calls) {
      assert.equal(new URL(call.url).pathname, '/journal/context-analysis')
      assert.equal(call.headers.Authorization, 'Bearer owner-token')
      assert.equal(call.credentials, 'omit')
      if (call.method === 'POST') assert.deepEqual(JSON.parse(call.body), PERIOD)
      else assert.equal(call.body, undefined)
    }
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(getContextAnalysis(PERIOD), { status: 401 })
    await assert.rejects(submitContextAnalysis(PERIOD), { status: 401 })
    assert.equal(calls.length, 2)
  } finally {
    globalThis.fetch = oldFetch
    globalThis.sessionStorage = oldStorage
  }
})

test('insufficient history and provider failures remain errors without automatic retry', async () => {
  const oldFetch = globalThis.fetch
  const oldStorage = globalThis.sessionStorage
  let count = 0
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  try {
    for (const status of [409, 503]) {
      globalThis.fetch = async () => { count++; return { ok: false, status, json: async () => ({ detail: 'Tente novamente.' }) } }
      await assert.rejects(submitContextAnalysis(PERIOD), { status, message: 'Tente novamente.' })
    }
    assert.equal(count, 2)
  } finally {
    globalThis.fetch = oldFetch
    globalThis.sessionStorage = oldStorage
  }
})

test('analysis history sends authenticated paginated GET only and propagates errors', async () => {
  const { listContextAnalyses } = await import('../src/services/contextAnalysisApi.js')
  const oldFetch = globalThis.fetch
  const oldStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => ({ analyses: [], total: 0, limit: 5, offset: 10 }) }
  }
  try {
    const controller = new AbortController()
    const result = await listContextAnalyses({ limit: 5, offset: 10, signal: controller.signal })
    assert.deepEqual(result.analyses, [])
    assert.equal(new URL(calls[0].url).pathname, '/journal/context-analysis/history')
    assert.equal(new URL(calls[0].url).searchParams.get('offset'), '10')
    assert.equal(new URL(calls[0].url).searchParams.get('limit'), '5')
    assert.equal(calls[0].method, undefined)
    assert.equal(calls[0].signal, controller.signal)
    assert.equal(calls[0].headers.Authorization, 'Bearer owner-token')
    assert.equal(calls[0].body, undefined)
    globalThis.fetch = async () => ({ ok: false, status: 503, json: async () => ({ detail: 'Indisponível.' }) })
    await assert.rejects(listContextAnalyses(), { status: 503, message: 'Indisponível.' })
    globalThis.sessionStorage = { getItem: () => null }
    await assert.rejects(listContextAnalyses(), { status: 401 })
    assert.equal(calls.length, 1)
  } finally {
    globalThis.fetch = oldFetch
    globalThis.sessionStorage = oldStorage
  }
})
