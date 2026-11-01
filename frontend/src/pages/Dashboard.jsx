import { AlertCircle, BookOpen, Calendar, CheckCircle, Clock, FileText, Plus, TrendingUp } from 'lucide-react'
import { Link } from 'react-router'
import { useEffect, useState } from 'react'
import { listJournalEntries } from '../services/journalApi'
import { clearSession } from '../services/authSession'

const temasRecorrentes = [
  { nome: 'Crescimento pessoal', frequencia: 12 },
  { nome: 'Relacionamentos', frequencia: 8 },
  { nome: 'Mudança', frequencia: 6 },
  { nome: 'Gratidão', frequencia: 5 },
]

function getStatus(status) {
  if (['analyzed', 'completed'].includes(status)) return { icon: <CheckCircle className="w-5 h-5 text-primary" />, label: 'Analisada' }
  if (['analysis_failed', 'failed', 'error'].includes(status)) return { icon: <AlertCircle className="w-5 h-5 text-destructive" />, label: 'Falha na análise' }
  if (status === 'draft') return { icon: <BookOpen className="w-5 h-5 text-muted-foreground" />, label: 'Rascunho' }
  return { icon: <Clock className="w-5 h-5 text-secondary" />, label: 'Aguardando análise' }
}

function getUserName() {
  try {
    const user = JSON.parse(sessionStorage.getItem('auth_user'))
    return user?.name || user?.username || 'visitante'
  } catch {
    return 'visitante'
  }
}

export function Dashboard() {
  const userName = getUserName()
  const [entries, setEntries] = useState([])
  const [loadingEntries, setLoadingEntries] = useState(true)
  const [entriesError, setEntriesError] = useState(null)

  useEffect(() => {
    listJournalEntries({ limit: 5 }).then((data) => setEntries(data.entries || []))
      .catch((error) => { if (error.status === 401) clearSession(); setEntriesError(error) })
      .finally(() => setLoadingEntries(false))
  }, [])

  return (
    <div className="p-5 md:p-8 max-w-7xl mx-auto">
      <div className="flex md:hidden items-center gap-3 mb-8">
        <BookOpen className="w-8 h-8 text-primary" strokeWidth={1.5} />
        <span className="text-2xl text-primary">Reflecta</span>
      </div>

      <header className="catalog-page-header catalog-page-intro mb-8">
        <div className="catalog-page-intro-copy">
          <h1 className="text-3xl">Bem-vindo de volta, {userName}</h1>
          <p>Continue sua jornada de autoconhecimento.</p>
        </div>
        <div className="catalog-header-actions">
          <Link to="/inicio/diario" className="catalog-primary catalog-hover-primary"><Plus size={16} aria-hidden="true" />Nova reflexão</Link>
          <Link to="/inicio/reflexoes" className="catalog-button catalog-hover-secondary"><FileText size={15} aria-hidden="true" />Minhas reflexões</Link>
        </div>
      </header>

      <p role="note" className="mb-6 text-sm text-muted-foreground">Suas reflexões mais recentes.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <section className="lg:col-span-2 bg-card rounded-2xl border border-border p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl">Histórico de reflexões</h2>
            <Calendar className="w-5 h-5 text-muted-foreground" />
          </div>

          {loadingEntries ? <p role="status">Carregando histórico...</p> : entriesError ? <p role="alert" className="text-destructive">Não foi possível carregar o histórico.</p> : !entries.length ? <p className="text-muted-foreground">Suas reflexões salvas aparecerão aqui.</p> : <div className="space-y-4">
            {entries.map((entry) => {
              const status = getStatus(entry.status)
              const date = entry.created_at ? new Date(entry.created_at).toLocaleDateString('pt-BR') : ''
              return (
                <Link to={`/inicio/reflexoes/${entry.id}`} key={entry.id} className="block p-4 bg-muted rounded-xl hover:bg-accent transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="mb-1">{entry.title || 'Reflexão sem título'}</h3>
                      <p className="text-sm text-muted-foreground mb-2">{date}</p>
                      <div className="flex flex-wrap gap-2">
                        {(entry.context_tags?.domains || []).map((tag) => (
                          <span key={tag.label} className="inline-block px-3 py-1 bg-secondary/20 text-secondary-foreground text-sm rounded-full">
                            {tag.label}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {status.icon}
                      <span className="hidden sm:inline whitespace-nowrap">{status.label}</span>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>}
        </section>

        <div className="space-y-6">
          <section className="bg-card rounded-2xl border border-border p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h3>Evolução pessoal</h3>
            </div>
            <div className="space-y-3">
              {[['Reflexões este mês', '12', '60%', 'bg-primary'], ['Temas explorados', '8', '40%', 'bg-secondary']].map(([label, value, width, color]) => (
                <div key={label}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">{label}</span><span>{value}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden"><div className={`h-full ${color}`} style={{ width }} /></div>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-card rounded-2xl border border-border p-6">
            <h3 className="mb-4">Temas recorrentes</h3>
            <div className="space-y-3">
              {temasRecorrentes.map((tema) => (
                <div key={tema.nome}>
                  <div className="flex justify-between text-sm mb-1"><span>{tema.nome}</span><span className="text-muted-foreground">{tema.frequencia}x</span></div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-accent" style={{ width: `${(tema.frequencia / 12) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl border border-border p-6">
            <div className="flex items-center gap-3 mb-3"><BookOpen className="w-5 h-5 text-primary" /><h3>Referência recente</h3></div>
            <blockquote className="text-sm italic mb-3 text-muted-foreground">“O homem não é nada além daquilo que a educação faz dele.”</blockquote>
            <p className="text-sm"><span className="text-muted-foreground">— Immanuel Kant,</span> Sobre a Pedagogia</p>
          </section>
        </div>
      </div>
    </div>
  )
}
