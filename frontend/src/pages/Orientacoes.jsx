import { CalendarDays, Check, CheckCircle2, ChevronLeft, ChevronRight, ClipboardList, ListFilter, MessageCircleQuestion } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { clearSession } from '../services/authSession'
import { PageLoading } from '../components/PageLoading'
import {
  completeProfessionalActivity,
  listProfessionalActivities,
  notifyProfessionalActivitiesChanged,
} from '../services/professionalActivitiesApi'

const PAGE_SIZE = 6
const STATUS_LABELS = { pending: 'Pendente', completed: 'Concluída' }
const KIND_LABELS = { activity: 'Atividade', guided_reflection: 'Reflexão guiada' }

function formatDate(value) {
  if (!value) return null
  const date = value.length === 10 ? new Date(`${value}T12:00:00`) : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date.toLocaleDateString('pt-BR')
}

function isOverdue(activity) {
  if (activity.status !== 'pending' || !activity.due_date) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(`${activity.due_date}T12:00:00`) < today
}

function ActivityDates({ activity }) {
  const overdue = isOverdue(activity)
  return <dl className="professional-activity-dates">
    <div><dt>Recebida em</dt><dd>{formatDate(activity.created_at) || 'Data indisponível'}</dd></div>
    <div><dt><CalendarDays size={14} />Realizar até</dt><dd className={overdue ? 'is-overdue' : ''}>{formatDate(activity.due_date) || 'Sem prazo definido'}{overdue && ' · prazo vencido'}</dd></div>
    {activity.completed_at && <div><dt>Concluída em</dt><dd>{formatDate(activity.completed_at)}</dd></div>}
  </dl>
}

function ActivityDetails({ activity, onClose }) {
  const dialog = useRef(null)

  useEffect(() => {
    const element = dialog.current
    element.showModal()
    return () => element.close()
  }, [])

  return <dialog ref={dialog} aria-labelledby="activity-detail-title"
    onCancel={(event) => { event.preventDefault(); onClose() }}
    className="m-auto max-h-[90vh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto rounded-2xl border border-border bg-card p-6 text-foreground shadow-xl backdrop:bg-black/40">
    <div className="professional-activity-card-heading">
      <span className="professional-activity-kind">{KIND_LABELS[activity.kind] || 'Orientação'}</span>
      <span className={`professional-activity-status is-${activity.status}`}><i />{STATUS_LABELS[activity.status]}</span>
    </div>
    <h2 id="activity-detail-title" className="mt-4 break-words text-2xl">{activity.title}</h2>
    <p className="my-4 whitespace-pre-wrap break-words">{activity.description}</p>
    <ActivityDates activity={activity} />
    <div className="mt-6 flex justify-end">
      <button type="button" autoFocus className="catalog-button catalog-hover-secondary" onClick={onClose}>Fechar</button>
    </div>
  </dialog>
}

export function Orientacoes() {
  const [status, setStatus] = useState('pending')
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ activities: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState('')
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [selectedActivity, setSelectedActivity] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    listProfessionalActivities({
      status,
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
      signal: controller.signal,
    }).then(setData).catch((requestError) => {
      if (requestError.name === 'AbortError') return
      if (requestError.status === 401) clearSession()
      setError(requestError.message || 'Não foi possível carregar suas orientações.')
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false)
    })
    return () => controller.abort()
  }, [status, page, revision])

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE))
  const changeStatus = (value) => {
    setStatus(value)
    setPage(1)
    setError('')
    setLoading(true)
  }
  const changePage = (value) => {
    setPage(value)
    setError('')
    setLoading(true)
  }
  const complete = async (activity) => {
    if (busyId || activity.status === 'completed') return
    setBusyId(activity.id)
    setError('')
    try {
      await completeProfessionalActivity(activity.id)
      notifyProfessionalActivitiesChanged()
      setLoading(true)
      setRevision(value => value + 1)
    } catch (requestError) {
      if (requestError.status === 401) clearSession()
      setError(requestError.message || 'Não foi possível concluir esta orientação.')
    } finally {
      setBusyId('')
    }
  }

  return <div className="admin-fixed-shell min-h-screen bg-background p-5 md:p-8">
    <div className="admin-fixed-page max-w-6xl mx-auto">
      <header className="catalog-page-header catalog-page-intro">
        <div className="catalog-page-intro-copy"><h1 className="text-3xl">Orientações</h1><p>Atividades e reflexões guiadas recebidas por meio dos seus compartilhamentos.</p></div>
        <div className="profile-sharing-filter">
          <button type="button" className="catalog-button catalog-hover-secondary profile-sharing-filter-trigger" aria-haspopup="true"><ListFilter size={15} />Filtrar{status && <span aria-label={`Filtro ativo: ${status === 'pending' ? 'Pendentes' : 'Concluídas'}`} />}</button>
          <div className="profile-sharing-filter-popover">
            <label htmlFor="activity-status">Status</label>
            <select id="activity-status" value={status} onChange={(event) => changeStatus(event.target.value)}>
              <option value="">Todas</option>
              <option value="pending">Pendentes</option>
              <option value="completed">Concluídas</option>
            </select>
          </div>
        </div>
      </header>

      <div className="admin-scroll-region professional-activities-scroll-region">
        <div className="professional-activities-toolbar">
          <span>{data.total} {data.total === 1 ? 'orientação encontrada' : 'orientações encontradas'}</span>
          <nav className="theme-pagination" aria-label="Paginação das orientações"><button type="button" aria-label="Página anterior" disabled={page <= 1} onClick={() => changePage(page - 1)}><ChevronLeft size={15} /></button><span>{totalPages > 1 ? `Página ${page} de ${totalPages}` : 'Página 1'}</span><button type="button" aria-label="Próxima página" disabled={page >= totalPages} onClick={() => changePage(page + 1)}><ChevronRight size={15} /></button></nav>
        </div>

        {error && <p role="alert" className="text-destructive">{error}</p>}
        {loading ? <PageLoading variant="cards" label="Carregando orientações…" /> : !data.activities.length ? <div className="professional-activities-empty"><ClipboardList size={32} aria-hidden="true" /><h2>Nenhuma orientação encontrada</h2><p>{status === 'pending' ? 'Você não possui atividades ou reflexões guiadas pendentes.' : status === 'completed' ? 'Você ainda não concluiu nenhuma orientação.' : 'Quando uma orientação for enviada, ela aparecerá nesta página.'}</p></div> : <div className="professional-activities-grid">{data.activities.map((activity) => {
          const KindIcon = activity.kind === 'guided_reflection' ? MessageCircleQuestion : ClipboardList
          return <article className={`professional-activity-card is-${activity.status}`} key={activity.id}>
            <div className="professional-activity-card-heading"><span className="professional-activity-kind"><KindIcon size={16} aria-hidden="true" />{KIND_LABELS[activity.kind] || 'Orientação'}</span><span className={`professional-activity-status is-${activity.status}`}><i />{STATUS_LABELS[activity.status]}</span></div>
            <div><h2>{activity.title}</h2><p>{activity.description}</p></div>
            <ActivityDates activity={activity} />
            <div className="professional-activity-card-actions flex-wrap gap-2">
              <button type="button" className="catalog-button catalog-hover-secondary" onClick={() => setSelectedActivity(activity)}>Abrir orientação</button>
              {activity.status === 'pending' ? <button type="button" className="catalog-primary catalog-hover-primary" disabled={busyId === activity.id} onClick={() => complete(activity)}><Check size={15} />{busyId === activity.id ? 'Concluindo...' : 'Marcar como concluída'}</button> : <span><CheckCircle2 size={16} />Orientação concluída</span>}
            </div>
          </article>
        })}</div>}
      </div>
    </div>
    {selectedActivity && <ActivityDetails activity={selectedActivity} onClose={() => setSelectedActivity(null)} />}
  </div>
}
