import test from 'node:test'
import assert from 'node:assert/strict'
import {
  describeIngestion,
  formatCatalogDate,
  formatCatalogDateTime,
  summarizeWorks,
} from '../src/services/workCatalog.js'

test('summarizeWorks counts works, active works and all associated passages', () => {
  assert.deepEqual(summarizeWorks([
    { status: 'ACTIVE', passage_counts: { total: 4 } },
    { status: 'INACTIVE', passage_counts: { total: 7 } },
    { status: 'INACTIVE' },
  ]), { total: 3, active: 1, passages: 11 })
})

test('formatCatalogDate handles valid and absent catalog dates', () => {
  assert.notEqual(formatCatalogDate('2026-10-31T12:00:00Z'), 'Data não informada')
  assert.equal(formatCatalogDate('invalid'), 'Data não informada')
  assert.equal(formatCatalogDate(null), 'Data não informada')
})

test('ingestion presentation distinguishes processing from administrative review', () => {
  assert.deepEqual(describeIngestion({
    status: 'processing',
    progress: { total: 25, completed: 17, percentage: 68 },
  }), {
    status: 'processing',
    label: 'Em processamento',
    detail: '17 de 25 chunks concluídos',
    percentage: 68,
  })
  assert.equal(describeIngestion({
    status: 'processing',
    progress: { total: 0 },
  }).detail, 'Preparando e dividindo o documento')
  assert.equal(describeIngestion({
    status: 'pending_review',
    progress: { total: 25, completed: 25 },
  }).detail, 'Análise da IA concluída; passagens aguardam revisão')
  assert.equal(describeIngestion({
    status: 'completed',
    progress: { total: 25, completed: 25 },
  }).label, 'Concluída')
  assert.deepEqual(describeIngestion({
    status: 'pending',
    progress: { total: 0 },
    failure: { message: 'As credenciais AWS expiraram.' },
  }), {
    status: 'failed',
    label: 'Processamento interrompido',
    detail: 'As credenciais AWS expiraram.',
    percentage: null,
  })
})

test('formatCatalogDateTime handles valid and absent timestamps', () => {
  assert.notEqual(formatCatalogDateTime('2026-10-31T12:30:00Z'), 'Data não informada')
  assert.equal(formatCatalogDateTime('invalid'), 'Data não informada')
})
