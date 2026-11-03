function normalizeSearch(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

function containsText(value, query) {
  return normalizeSearch(value).includes(normalizeSearch(query).trim())
}

function highestThemeConfidence(passage) {
  const values = (Array.isArray(passage?.themes) ? passage.themes : [])
    .map((theme) => Number(theme.confidence))
    .filter(Number.isFinite)
  return values.length ? Math.max(...values) : null
}

function matchesConfidenceRange(passage, range) {
  if (!range) return true
  const confidence = highestThemeConfidence(passage)
  if (confidence === null) return false
  if (range === 'high') return confidence >= 0.8
  if (range === 'medium') return confidence >= 0.7 && confidence < 0.8
  return true
}

export function filterPassages(passages, filters, works = []) {
  const items = Array.isArray(passages) ? passages : []
  const worksById = new Map((Array.isArray(works) ? works : []).map((work) => [work.id, work]))
  const status = filters?.status || ''
  const workId = filters?.work_id || ''
  const ingestionId = filters?.ingestion_id || ''
  const workTitle = filters?.work_title || ''
  const authorName = filters?.author_name || ''
  const confidenceRange = filters?.confidence_range || ''

  return items.filter((passage) => {
    const work = worksById.get(passage.work_id)
    return (
      (!status || passage.status === status)
      && (!workId || containsText(passage.work_id, workId))
      && (!ingestionId || containsText(passage.ingestion_id, ingestionId))
      && (!workTitle || containsText(work?.title, workTitle))
      && (!authorName || containsText(work?.author?.name, authorName))
      && matchesConfidenceRange(passage, confidenceRange)
    )
  })
}
