import { ContextShareControls } from './ContextShareControls'
import { formatPeriodDate } from '../../services/contextPeriod'
import { Link } from 'react-router'

export function ContextAnalysisResult({ analysis, publicView = false }) {
  return <div className="space-y-4">
      <p className="text-sm text-muted-foreground">{analysis.period ? `Período: ${formatPeriodDate(analysis.period.start_date)} a ${formatPeriodDate(analysis.period.end_date)} (7 dias, horário de Brasília).` : 'Análise anterior à seleção de períodos de 7 dias.'}</p>
      <p className="text-sm text-muted-foreground">Gerada em {new Date(analysis.created_at).toLocaleString('pt-BR')} com {analysis.entry_count ?? analysis.entry_ids?.length} reflexões.</p>
      {!publicView && <details><summary className="cursor-pointer">Reflexões incluídas nesta análise</summary><ol className="list-decimal pl-5 space-y-1 mt-2">{analysis.entry_ids.map((id, index) => <li key={id}><Link className="underline" to={`/inicio/reflexoes/${encodeURIComponent(id)}`}>Consultar reflexão {index + 1}</Link></li>)}</ol></details>}
      <p className="whitespace-pre-wrap break-words">{analysis.result.summary}</p>
      {[
        ['recurring_patterns', 'Padrões observados'],
        ['changes_over_time', 'Mudanças ao longo do tempo'],
        ['reflection_questions', 'Perguntas para refletir'],
      ].map(([key, label]) => <div key={key}><h3 className="font-medium">{label}</h3><ul className="list-disc pl-5 space-y-2">{analysis.result[key].map((text, index) => <li className="whitespace-pre-wrap break-words" key={index}>{text}</li>)}</ul></div>)}
      <p className="text-sm text-muted-foreground">Interpretação gerada por IA, sem diagnóstico clínico.</p>
      {!publicView && <ContextShareControls key={analysis.id} analysis={analysis} />}
  </div>
}
