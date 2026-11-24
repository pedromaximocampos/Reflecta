import { useCallback, useState } from 'react'
import { Plus } from 'lucide-react'
import { ContextAnalysis } from '../components/journal/ContextAnalysis'
import { ContextAnalysisHistory } from '../components/journal/ContextAnalysisHistory'

export function HistoricoAnalises() {
  const [creating, setCreating] = useState(false)
  const [revision, setRevision] = useState(0)
  const closeCreator = useCallback(() => setCreating(false), [])

  return <div className="context-history-page max-w-5xl mx-auto p-5 md:p-8 space-y-6">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy">
        <h1 className="text-3xl">Análise do histórico</h1>
        <p>Consulte leituras de períodos anteriores ou escolha sete dias do seu diário para observar padrões e mudanças.</p>
      </div>
      <div className="catalog-header-actions">
        <button type="button" className="catalog-primary catalog-hover-primary" onClick={() => setCreating(true)}><Plus size={16} aria-hidden="true" />Nova análise</button>
      </div>
    </header>
    <ContextAnalysisHistory revision={revision} />
    {creating && <ContextAnalysis onClose={closeCreator} onCreated={() => setRevision((value) => value + 1)} />}
  </div>
}
