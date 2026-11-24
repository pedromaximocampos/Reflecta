import { useEffect, useState } from 'react'
import { BookOpen, Plus, Share2, Sparkles } from 'lucide-react'
import { ContextAnalysisResult } from '../components/journal/ContextAnalysisResult'
import { ProfessionalActivityModal } from '../components/journal/ProfessionalActivityModal'
import { SharedJournalEntries } from '../components/journal/SharedJournalEntries'
import { resolveContextShare } from '../services/contextSharesApi'

export function AnaliseCompartilhada() {
  const [token] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get('token') || '')
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [activityModalOpen, setActivityModalOpen] = useState(false)
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
  return <div className="shared-analysis-shell">
    <aside className="shared-analysis-sidebar">
      <div className="shared-analysis-brand">
        <BookOpen size={32} strokeWidth={1.5} aria-hidden="true" />
        <span>Reflecta</span>
      </div>
      <div className="shared-analysis-sidebar-item" aria-current="page">
        <Share2 size={19} strokeWidth={1.5} aria-hidden="true" />
        <span>Análise compartilhada</span>
      </div>
      <p>Conteúdo disponibilizado em modo somente leitura.</p>
    </aside>

    <main className="shared-analysis-main">
      <header className="catalog-page-header catalog-page-intro shared-analysis-page-header">
        <div className="catalog-page-intro-copy">
          <h1 className="text-3xl">Análise compartilhada</h1>
          <p>Uma visão contextual do período e das reflexões autorizadas.</p>
        </div>
        {analysis && <div className="shared-analysis-header-actions">
          <button type="button" className="catalog-primary catalog-hover-primary" onClick={() => setActivityModalOpen(true)}><Plus size={15} />Nova orientação</button>
          <p className="shared-analysis-expiration">Acesso até <strong>{new Date(analysis.expires_at).toLocaleString('pt-BR')}</strong></p>
        </div>}
      </header>

      {error ? <div role="alert" className="shared-analysis-feedback">
        <p>{error}</p>
        <button className="catalog-button catalog-hover-secondary" onClick={() => { setError(''); setAnalysis(null); setRevision(value => value + 1) }}>Consultar novamente</button>
      </div> : !analysis ? <p className="shared-analysis-feedback" role="status">Carregando análise...</p> : <div className="shared-analysis-workspace">
        <section className="shared-analysis-panel" aria-labelledby="shared-context-title">
          <header className="shared-analysis-panel-heading">
            <Sparkles size={19} aria-hidden="true" />
            <div><h2 id="shared-context-title">Análise do período</h2><p>Síntese, padrões, mudanças e perguntas para reflexão.</p></div>
          </header>
          <div className="shared-analysis-panel-body"><ContextAnalysisResult analysis={analysis} publicView /></div>
        </section>

        <section className="shared-analysis-panel shared-analysis-reflections-panel">
          <SharedJournalEntries entries={analysis.entries} />
        </section>
      </div>}
    </main>
    {activityModalOpen && <ProfessionalActivityModal token={token} onClose={() => setActivityModalOpen(false)} />}
  </div>
}
