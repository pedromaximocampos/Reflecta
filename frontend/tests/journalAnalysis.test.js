import test from 'node:test'
import assert from 'node:assert/strict'
import { contextualPassages } from '../src/services/journalAnalysis.js'

test('contextual passages expose the persisted catalog snapshot without changing journal text', () => {
  const analysis = {
    sentences: [{
      id: 'sentence-1',
      sentence_text: 'Posso escolher como responder.',
      themes: [{ id: 'theme-1', label: 'Escolher como responder' }],
      passages: [{
        id: 'association-1',
        passage_id: 'passage-1',
        confidence: 0.91,
        reason: 'A passagem reforça uma resposta consciente.',
        payload_snapshot: {
          short_text: 'Não são as coisas que perturbam, mas os juízos sobre elas.',
          paraphrase: 'Nossa interpretação influencia a resposta aos acontecimentos.',
          interpretation_note: 'Associação com julgamento e escolha.',
          locator: 'Enchiridion, 5',
          work: { title: 'Manual de Epicteto', author_name: 'Epicteto' },
        },
      }],
    }],
  }

  assert.deepEqual(contextualPassages(analysis), [{
    id: 'association-1',
    passage_id: 'passage-1',
    sentence_text: 'Posso escolher como responder.',
    themes: [{ id: 'theme-1', label: 'Escolher como responder' }],
    confidence: 0.91,
    reason: 'A passagem reforça uma resposta consciente.',
    short_text: 'Não são as coisas que perturbam, mas os juízos sobre elas.',
    paraphrase: 'Nossa interpretação influencia a resposta aos acontecimentos.',
    interpretation_note: 'Associação com julgamento e escolha.',
    locator: 'Enchiridion, 5',
    work_title: 'Manual de Epicteto',
    author_name: 'Epicteto',
  }])
})

test('contextual passages ignore absent or malformed snapshots', () => {
  assert.deepEqual(contextualPassages(null), [])
  assert.deepEqual(contextualPassages({ sentences: [{ passages: [{ payload_snapshot: null }] }] }), [])
  assert.deepEqual(contextualPassages({ sentences: [{ passages: [{ payload_snapshot: { short_text: '  ' } }] }] }), [])
})

test('contextual passages expose only themes persisted as matches for navigation', () => {
  const analysis = {
    sentences: [{
      id: 'sentence-1',
      sentence_text: 'Posso escolher como responder ao que não controlo.',
      themes: [
        { id: 'control', label: 'O que posso controlar' },
        { id: 'acceptance', label: 'Aceitar o que não posso mudar' },
      ],
      passages: [{
        id: 'association-1',
        passage_id: 'passage-1',
        confidence: 0.93,
        reason: 'A passagem trata diretamente daquilo que depende de nós.',
        payload_snapshot: {
          short_text: 'Algumas coisas dependem de nós e outras não.',
          theme_matches: [{ theme_id: 'control', confidence: 0.95 }],
        },
      }],
    }],
  }

  assert.deepEqual(
    contextualPassages(analysis)[0].themes,
    [{ id: 'control', label: 'O que posso controlar' }],
  )
})
