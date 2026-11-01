import { Navigate, Outlet, Link } from 'react-router'
import { useAuth } from '../services/authSession'
export function AdminGuard() {
  const { isAuthenticated, isAdmin } = useAuth()
  if (!isAuthenticated) return <Navigate to="/" replace />
  if (!isAdmin) return <div className="p-8"><h1>Acesso restrito a administradores</h1><Link to="/inicio">Voltar ao início</Link></div>
  return <Outlet />
}
