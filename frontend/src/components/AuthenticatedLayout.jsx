import { Navigate } from 'react-router'
import { useAuth } from '../services/authSession'
import { MainLayout } from './MainLayout'

export function AuthenticatedLayout() {
  const { isAuthenticated, isAdmin } = useAuth()

  if (!isAuthenticated) return <Navigate to="/login" replace />

  return <MainLayout admin={isAdmin} />
}
