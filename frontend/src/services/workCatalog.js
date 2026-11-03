export function summarizeWorks(works = []) {
  return {
    total: works.length,
    active: works.filter((work) => work.status === 'ACTIVE').length,
    passages: works.reduce((total, work) => total + Number(work.passage_counts?.total || 0), 0),
  }
}

export function formatCatalogDate(value) {
  if (!value) return 'Data não informada'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Data não informada'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

export function formatCatalogDateTime(value) {
  if (!value) return 'Data não informada'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Data não informada'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}

const ingestionLabels = {
  pending: 'Aguardando processamento',
  processing: 'Em processamento',
  failed: 'Processamento interrompido',
  pending_review: 'Aguardando revisão',
  completed: 'Concluída',
}

export function describeIngestion(ingestion = {}) {
  const status = ingestion.failure ? 'failed' : ingestion.status
  const progress = ingestion.progress || {}
  const total = Number(progress.total || 0)
  const completed = Number(progress.completed || 0)
  const percentage = total > 0
    ? Math.min(100, Math.max(0, Number(progress.percentage ?? Math.round(completed * 100 / total))))
    : null
  let detail = total > 0 ? `${completed} de ${total} chunks concluídos` : 'Aguardando a criação dos chunks'
  if (status === 'pending') detail = 'Na fila para processamento'
  if (status === 'processing' && total === 0) detail = 'Preparando e dividindo o documento'
  if (status === 'pending_review') detail = 'Análise da IA concluída; passagens aguardam revisão'
  if (status === 'completed') detail = 'Todas as passagens desta ingestão foram revisadas'
  if (status === 'failed') detail = ingestion.failure?.message || (total > 0
    ? `${completed} de ${total} chunks concluídos antes da falha`
    : 'O processamento ainda não produziu chunks concluídos')
  return {
    status,
    label: ingestionLabels[status] || status || 'Estado desconhecido',
    detail,
    percentage,
  }
}
