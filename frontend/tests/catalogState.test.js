import test from 'node:test'
import assert from 'node:assert/strict'

import {
  readCatalog,
  rememberCatalog,
  replaceCatalog,
} from '../src/services/catalogState.js'

function storageMock() {
  const values = new Map()
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
  }
}

test('catalog cache distinguishes missing data from a loaded empty catalog', () => {
  const previousStorage = globalThis.localStorage
  globalThis.localStorage = storageMock()
  try {
    assert.deepEqual(readCatalog().loaded, { themes: false, works: false, ingestions: false })
    replaceCatalog('themes', [])
    assert.deepEqual(readCatalog().loaded, { themes: true, works: false, ingestions: false })
    replaceCatalog('works', [])
    assert.deepEqual(readCatalog().loaded, { themes: true, works: true, ingestions: false })
    replaceCatalog('ingestions', [])
    assert.deepEqual(readCatalog().loaded, { themes: true, works: true, ingestions: true })
  } finally {
    globalThis.localStorage = previousStorage
  }
})

test('catalog cache replaces collections and remembers individual updates', () => {
  const previousStorage = globalThis.localStorage
  globalThis.localStorage = storageMock()
  try {
    replaceCatalog('themes', [{ id: 'theme-1', label: 'Original' }])
    replaceCatalog('works', [{ id: 'work-1', title: 'Original' }])
    replaceCatalog('ingestions', [{ ingestion_id: 'ingestion-1', status: 'pending' }])
    rememberCatalog('themes', { id: 'theme-1', label: 'Atualizado' })
    rememberCatalog('works', { id: 'work-1', title: 'Atualizada' })
    rememberCatalog('ingestions', { ingestion_id: 'ingestion-1', status: 'completed' })

    const catalog = readCatalog()
    assert.deepEqual(catalog.themes, [{ id: 'theme-1', label: 'Atualizado' }])
    assert.deepEqual(catalog.works, [{ id: 'work-1', title: 'Atualizada' }])
    assert.deepEqual(catalog.ingestions, [{ ingestion_id: 'ingestion-1', status: 'completed' }])
    assert.equal(typeof catalog.updated_at, 'string')
  } finally {
    globalThis.localStorage = previousStorage
  }
})
