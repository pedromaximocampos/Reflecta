import { useEffect, useState } from 'react'
import { ContextAnalysisResult } from '../components/journal/ContextAnalysisResult'
import { resolveContextShare } from '../services/contextSharesApi'

export function AnaliseCompartilhada() {
  const [token] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get('token') || '')
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    const meta = document.createElement('meta')
    meta.name = 'referrer'
    meta.content = 'no-referrer'
    document.head.appendChild(meta)
    resolveContextShare(token, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setAnalysis(data)
    }).catch(err => {
      if (controller.signal.aborted) return
      setAnalysis(null)
      setError([400, 404, 422].includes(err.status) ? 'Este link é inválido, expirou, foi revogado ou não está mais disponível.' : 'Não foi possível carregar a análise. Tente novamente.')
    })
    return () => { controller.abort(); meta.remove() }
  }, [token, revision])
  useEffect(() => {
    if (!analysis) return
    const remaining = Date.parse(analysis.expires_at) - Date.now()
    const timer = setTimeout(() => { setAnalysis(null); setError('Este link expirou.') }, Math.max(0, remaining))
    // Recheck while open so revocation or deletion is reflected without reload.
    const refresh = setInterval(() => setRevision(value => value + 1), 60000)
    return () => { clearTimeout(timer); clearInterval(refresh) }
  }, [analysis])
  return <main className="max-w-3xl mx-auto p-5 md:p-8 space-y-5">
    <header><p className="text-primary">REFLECTA</p><h1 className="text-3xl">Análise compartilhada</h1></header>
    {error ? <div role="alert" className="border border-border rounded-xl p-5 space-y-3"><p>{error}</p><button className="underline" onClick={() => { setError(''); setAnalysis(null); setRevision(value => value + 1) }}>Consultar novamente</button></div> : !analysis ? <p role="status">Carregando análise...</p> : <section className="bg-card border border-border rounded-2xl p-5 md:p-8 space-y-5">
      <p className="text-sm text-muted-foreground">Acesso disponível até {new Date(analysis.expires_at).toLocaleString('pt-BR')}.</p>
      <ContextAnalysisResult analysis={analysis} publicView />
    </section>}
  </main>
}
