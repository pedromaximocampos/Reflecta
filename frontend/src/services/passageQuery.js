export const PASSAGE_PAGE_SIZE = 20

export function readPassageFilters(searchParams) {
  return {
    status: searchParams.has('status') ? searchParams.get('status') : 'PENDING_REVIEW',
    work_id: searchParams.get('work_id') || '',
    ingestion_id: searchParams.get('ingestion_id') || '',
    work_title: searchParams.get('work_title') || '',
    author_name: searchParams.get('author_name') || '',
    confidence_range: searchParams.get('confidence_range') || '',
  }
}

export function buildPassageQuery(filters, page) {
  const query = {
    status: filters.status,
    work_id: filters.work_id,
    ingestion_id: filters.ingestion_id,
    work_title: filters.work_title,
    author_name: filters.author_name,
    limit: PASSAGE_PAGE_SIZE,
    offset: (page - 1) * PASSAGE_PAGE_SIZE,
  }
  if (filters.confidence_range === 'high') query.confidence_min = 0.8
  if (filters.confidence_range === 'medium') {
    query.confidence_min = 0.7
    query.confidence_max = 0.8
  }
  return query
}

export function serializePassageFilters(filters) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([name, value]) => {
    if (value || name === 'status') params.set(name, value)
  })
  return params
}
