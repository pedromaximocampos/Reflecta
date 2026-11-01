import { Link } from 'react-router'

export function JournalError({ error, onRetry }) {
  if (!error) return null
  const message = error.status === 401 ? 'Sua sessão expirou. Entre novamente para acessar suas reflexões.'
    : error.status === 404 ? 'Esta reflexão não foi encontrada ou não está mais disponível.'
    : error.status === 403 ? 'Você não tem permissão para acessar esta reflexão.'
    : error instanceof TypeError ? 'Não foi possível conectar ao servidor. Verifique sua conexão.'
    : error.message || 'Não foi possível concluir a solicitação.'
  return <div className="rounded-xl border border-destructive/30 bg-card p-4 space-y-3">
    <p role="alert" className="text-destructive">{message}</p>
    {error.status === 401 ? <Link to="/" className="text-primary underline">Ir para o login</Link>
      : onRetry && <button type="button" onClick={onRetry} className="text-primary underline">Tentar novamente</button>}
  </div>
}

export function EntryMeta({ entry }) {
  const labels = { draft: 'Rascunho', pending_analysis: 'Aguardando análise', analyzed: 'Analisada', analysis_failed: 'Falha na análise' }
  const date = new Date(entry.created_at)
  return <p className="text-sm text-muted-foreground">
    {Number.isNaN(date.getTime()) ? 'Data indisponível' : date.toLocaleString('pt-BR', { dateStyle: 'medium', timeStyle: 'short' })}
    {' · '}{labels[entry.status] ?? 'Salva'}
  </p>
}
