import { useEffect, useState } from 'react'
import { CalendarDays, Check, ChevronLeft, ChevronRight, ClipboardList, Lightbulb, MessageCircleQuestion, Plus, Send, X } from 'lucide-react'
import { createProfessionalActivities } from '../../services/contextSharesApi'

const STEPS = ['Escolher tipo', 'Escrever orientação', 'Revisar e enviar']
const TYPES = [
  {
    value: 'activity',
    title: 'Atividade',
    description: 'Uma prática concreta para realizar fora do diário.',
    icon: ClipboardList,
  },
  {
    value: 'guided_reflection',
    title: 'Reflexão guiada',
    description: 'Uma pergunta ou roteiro para aprofundar uma reflexão.',
    icon: MessageCircleQuestion,
  },
]

function typeLabel(kind) {
  return kind === 'guided_reflection' ? 'Reflexão guiada' : 'Atividade'
}

export function ProfessionalActivityModal({ token, onClose }) {
  const [step, setStep] = useState(1)
  const [kind, setKind] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [created, setCreated] = useState(null)
  const [prepared, setPrepared] = useState([])

  useEffect(() => {
    function closeOnEscape(event) {
      if (event.key === 'Escape' && !busy) onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [busy, onClose])

  const contentValid = title.trim().length >= 3 && description.trim().length >= 10

  function currentActivity() {
    return {
      kind,
      title: title.trim(),
      description: description.trim(),
      dueDate,
    }
  }

  function resetEditor() {
    setStep(1)
    setKind('')
    setTitle('')
    setDescription('')
    setDueDate('')
    setError('')
  }

  function addAnother() {
    if (!kind || !contentValid || prepared.length >= 19) return
    setPrepared(items => [...items, currentActivity()])
    resetEditor()
  }

  async function submit() {
    if (busy || !kind || !contentValid) return
    setBusy(true)
    setError('')
    try {
      const result = await createProfessionalActivities(token, [
        ...prepared,
        currentActivity(),
      ])
      setCreated(result)
    } catch (err) {
      setError([400, 404, 409, 422].includes(err.status)
        ? err.message
        : 'Não foi possível enviar a orientação. Tente novamente.')
    } finally {
      setBusy(false)
    }
  }

  return <div className="context-analysis-backdrop" role="presentation" onMouseDown={(event) => {
    if (event.target === event.currentTarget && !busy) onClose()
  }}>
    <section className="context-analysis-modal professional-activity-modal" role="dialog" aria-modal="true" aria-labelledby="professional-activity-title" aria-busy={busy}>
      <button type="button" className="context-analysis-close" onClick={onClose} disabled={busy} aria-label="Fechar nova orientação"><X size={18} /></button>
      <header className="context-analysis-modal-heading">
        <span>ACOMPANHAMENTO COMPARTILHADO</span>
        <h2 id="professional-activity-title">Nova atividade ou reflexão guiada</h2>
        <p>Registre uma orientação para a pessoa que autorizou este acesso.</p>
      </header>

      {!created && <ol className="context-analysis-steps" aria-label="Etapas da nova orientação">
        {STEPS.map((label, index) => {
          const number = index + 1
          const active = number <= step
          return <li key={label} className={active ? 'is-active' : ''} aria-current={number === step ? 'step' : undefined}>
            <span>{number < step ? <Check size={15} aria-hidden="true" /> : number}</span>
            <small>{label}</small>
          </li>
        })}
      </ol>}

      {created ? <div className="context-analysis-step">
        <div className="context-analysis-success"><Check size={20} aria-hidden="true" /><div><h3>Orientações enviadas</h3><p>{created.count} {created.count === 1 ? 'orientação foi salva' : 'orientações foram salvas'} e uma única notificação por e-mail entrou na fila de envio.</p></div></div>
        <div className="context-analysis-actions is-right"><button type="button" className="catalog-primary catalog-hover-primary" onClick={onClose}>Concluir</button></div>
      </div> : <>
        {step === 1 && <div className="context-analysis-step">
          <div className="context-analysis-step-copy"><Lightbulb size={22} aria-hidden="true" /><div><h3>O que você deseja sugerir?</h3><p>Escolha o formato que melhor representa a orientação.</p></div></div>
          <div className="professional-activity-types">{TYPES.map((item) => {
            const Icon = item.icon
            return <button type="button" key={item.value} className={kind === item.value ? 'is-selected' : ''} onClick={() => setKind(item.value)}>
              <Icon size={21} aria-hidden="true" />
              <span><strong>{item.title}</strong><small>{item.description}</small></span>
              <i aria-hidden="true">{kind === item.value && <Check size={14} />}</i>
            </button>
          })}</div>
          <div className="context-analysis-actions">
            <button type="button" className="catalog-button catalog-hover-secondary" onClick={onClose}>Cancelar</button>
            <button type="button" className="catalog-primary catalog-hover-primary" disabled={!kind} onClick={() => setStep(2)}>Continuar<ChevronRight size={16} /></button>
          </div>
        </div>}

        {step === 2 && <div className="context-analysis-step">
          <div className="context-analysis-step-copy"><ClipboardList size={22} aria-hidden="true" /><div><h3>Escreva a orientação</h3><p>Use linguagem clara, respeitosa e adequada ao contexto compartilhado.</p></div></div>
          <div className="professional-activity-fields">
            <label><span>Título</span><input value={title} maxLength={160} onChange={(event) => setTitle(event.target.value)} placeholder={kind === 'guided_reflection' ? 'Ex.: O que está ao seu alcance hoje?' : 'Ex.: Observar reações automáticas'} /></label>
            <label><span>Orientação</span><textarea value={description} maxLength={4000} rows={7} onChange={(event) => setDescription(event.target.value)} placeholder="Descreva a atividade ou apresente as perguntas que devem guiar a reflexão." /></label>
            <label className="professional-activity-due-date"><span><CalendarDays size={15} />Prazo sugerido <small>(opcional)</small></span><input type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} /></label>
            <small className="professional-activity-counter">{description.length}/4000 caracteres</small>
          </div>
          <div className="context-analysis-actions">
            <button type="button" className="catalog-button catalog-hover-secondary" onClick={() => setStep(1)}><ChevronLeft size={16} />Voltar</button>
            <button type="button" className="catalog-primary catalog-hover-primary" disabled={!contentValid} onClick={() => setStep(3)}>Revisar<ChevronRight size={16} /></button>
          </div>
        </div>}

        {step === 3 && <div className="context-analysis-step">
          <div className="context-analysis-step-copy"><Send size={22} aria-hidden="true" /><div><h3>Revise antes de enviar</h3><p>Depois do envio, a pessoa receberá uma notificação por e-mail.</p></div></div>
          {prepared.length > 0 && <div className="professional-activity-prepared">
            <strong>{prepared.length} {prepared.length === 1 ? 'orientação preparada' : 'orientações preparadas'}</strong>
            <ol>{prepared.map((item, index) => <li key={`${item.kind}-${item.title}-${index}`}><span>{typeLabel(item.kind)}</span><strong>{item.title}</strong></li>)}</ol>
          </div>}
          <dl className="context-analysis-review professional-activity-review">
            <div><dt>Tipo</dt><dd>{typeLabel(kind)}</dd></div>
            <div><dt>Título</dt><dd>{title.trim()}</dd></div>
            <div><dt>Orientação</dt><dd>{description.trim()}</dd></div>
            <div><dt>Prazo</dt><dd>{dueDate ? new Date(`${dueDate}T12:00:00`).toLocaleDateString('pt-BR') : 'Sem prazo definido'}</dd></div>
          </dl>
          <div className="context-analysis-step-copy"><Plus size={22} aria-hidden="true" /><div><h3>Gostaria de adicionar mais alguma orientação?</h3><p>Você pode preparar outra atividade ou reflexão guiada antes de enviar. Todas serão notificadas em um único e-mail.</p></div></div>
          <p className="context-analysis-consent">As orientações ficarão vinculadas a este acesso compartilhado. Não inclua diagnósticos, dados de terceiros ou informações que não sejam necessárias para o acompanhamento.</p>
          {error && <div className="context-analysis-error" role="alert"><p>{error}</p></div>}
          <div className="context-analysis-actions">
            <button type="button" className="catalog-button catalog-hover-secondary" disabled={busy} onClick={() => setStep(2)}><ChevronLeft size={16} />Voltar</button>
            <button type="button" className="catalog-button catalog-hover-secondary" disabled={busy || prepared.length >= 19} onClick={addAnother}><Plus size={15} />Adicionar outra</button>
            <button type="button" className="catalog-primary catalog-hover-primary" disabled={busy} onClick={submit}>{busy ? 'Enviando...' : `Enviar ${prepared.length + 1} ${prepared.length === 0 ? 'orientação' : 'orientações'}`}<Send size={15} /></button>
          </div>
        </div>}
      </>}
    </section>
  </div>
}

