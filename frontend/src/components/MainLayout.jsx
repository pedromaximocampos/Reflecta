import { useEffect, useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router'
import { BookMarked, BookOpen, Compass, Home, User, List, ListChecks, LogOut, AlertTriangle, History, Share2, ShieldCheck } from 'lucide-react'
import { logout } from '../services/authApi'
import { listProfessionalActivities, PROFESSIONAL_ACTIVITIES_CHANGED } from '../services/professionalActivitiesApi'

export function MainLayout({ admin = false }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [loggingOut, setLoggingOut] = useState(false)
  const [pendingActivities, setPendingActivities] = useState(0)
  const homePath = admin ? '/dashboard' : '/inicio'
  const menuItems = [
    { path: homePath, icon: Home, label: admin ? 'Painel administrativo' : 'Dashboard' },
    ...(admin ? [
      { path: '/dashboard/falhas', icon: AlertTriangle, label: 'Falhas operacionais' },
      { path: '/dashboard/temas', icon: List, label: 'Temas' },
      { path: '/dashboard/obras', icon: BookOpen, label: 'Obras e PDFs' },
      { path: '/dashboard/passagens', icon: BookMarked, label: 'Passagens' },
      { path: '/dashboard/administradores', icon: ShieldCheck, label: 'Administradores' },
    ] : []),
    ...(!admin ? [
      { path: '/inicio/diario', icon: BookMarked, label: 'Nova reflexão' },
      { path: '/inicio/reflexoes', icon: BookOpen, label: 'Minhas reflexões' },
      { path: '/inicio/analises', icon: History, label: 'Análise do histórico' },
      { path: '/inicio/orientacoes', icon: ListChecks, label: 'Orientações', badge: pendingActivities },
      { path: '/inicio/recomendacoes', icon: Compass, label: 'Recomendações' },
      { path: '/inicio/compartilhamentos', icon: Share2, label: 'Compartilhamentos' },
    ] : []),
    { path: '/auth/perfil', icon: User, label: 'Perfil' },
  ]

  useEffect(() => {
    if (admin) return undefined
    const controller = new AbortController()
    const loadPending = () => {
      listProfessionalActivities({ status: 'pending', limit: 1, signal: controller.signal })
        .then(data => setPendingActivities(data.total || 0))
        .catch(error => {
          if (error.name !== 'AbortError') setPendingActivities(0)
        })
    }
    loadPending()
    window.addEventListener(PROFESSIONAL_ACTIVITIES_CHANGED, loadPending)
    return () => {
      controller.abort()
      window.removeEventListener(PROFESSIONAL_ACTIVITIES_CHANGED, loadPending)
    }
  }, [admin])

  const handleLogout = async () => {
    if (loggingOut) return
    setLoggingOut(true)
    try {
      await logout()
    } finally {
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="flex flex-col md:flex-row min-h-screen md:h-screen md:overflow-hidden bg-background">
      <aside className="flex w-full md:w-64 shrink-0 bg-sidebar border-r border-sidebar-border flex-col md:h-screen md:sticky md:top-0">
        <div className="p-6 border-b border-sidebar-border">
          <Link to={homePath} className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-sidebar-primary" strokeWidth={1.5} />
            <h1 className="text-2xl text-sidebar-foreground">Reflecta</h1>
          </Link>
        </div>

        <nav aria-label={admin ? 'Menu administrativo' : 'Menu do usuário'} className="flex md:block overflow-x-auto md:overflow-x-hidden md:overflow-y-auto flex-1 p-4 md:space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
              || (item.path !== homePath && location.pathname.startsWith(`${item.path}/`))

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                }`}
              >
                <Icon className="w-5 h-5" strokeWidth={1.5} />
                <span>{item.label}</span>
                {item.badge > 0 && <span className="sidebar-menu-badge" aria-label={`${item.badge} orientações pendentes`}>{item.badge > 99 ? '99+' : item.badge}</span>}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-sidebar-border">
          <button
            type="button"
            onClick={handleLogout}
            disabled={loggingOut}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            <LogOut className="w-5 h-5" strokeWidth={1.5} aria-hidden="true" />
            <span>{loggingOut ? 'Saindo…' : 'Sair da conta'}</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0 overflow-visible md:h-screen md:overflow-y-auto md:overscroll-contain">
        <Outlet />
      </main>
    </div>
  )
}
