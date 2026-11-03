import test from 'node:test'
import assert from 'node:assert/strict'
import { defaultContextPeriod, shiftDate } from '../src/services/contextPeriod.js'

test('date selection maintains exactly seven inclusive calendar days across months and leap day', () => {
  assert.equal(shiftDate('2024-02-26', 6), '2024-03-03')
  assert.equal(shiftDate('2024-03-03', -6), '2024-02-26')
  assert.equal(shiftDate('2026-12-29', 6), '2027-01-04')
})

test('default period uses the date in Sao Paulo even when UTC is already next day', () => {
  assert.deepEqual(defaultContextPeriod(new Date('2026-10-30T01:00:00Z')), {
    start_date: '2026-10-23', end_date: '2026-10-29',
  })
})
