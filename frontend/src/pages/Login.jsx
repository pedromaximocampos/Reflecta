import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { BookOpen } from 'lucide-react'
import { login } from '../services/authApi'
import { saveSession, useAuth } from '../services/authSession'

export function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, isAdmin } = useAuth()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErro('')
    setCarregando(true)

    try {
      const response = await login(email, senha)
      saveSession(response)
      navigate(response.user?.role === 'ADMIN' ? '/deshboard' : '/inicio', { replace: true })
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Não foi possível realizar o login.')
    } finally {
      setCarregando(false)
    }
  }

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? '/deshboard' : '/inicio'} replace />
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-12">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="w-10 h-10 text-primary" strokeWidth={1.5} />
            <h1 className="text-4xl text-primary">Reflecta</h1>
          </div>
          <p className="text-muted-foreground text-center max-w-sm">
            Um espaço para organizar pensamentos e compreender sua jornada.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-card rounded-2xl shadow-sm border border-border p-8">
          <div className="space-y-6">
            <div>
              <label htmlFor="email" className="block mb-2 text-foreground">E-mail</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <label htmlFor="senha" className="block mb-2 text-foreground">Senha</label>
              <input
                id="senha"
                type="password"
                value={senha}
                onChange={(event) => setSenha(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="••••••••"
                required
              />
            </div>

            {location.state?.mensagem && (
              <p className="p-3 rounded-lg bg-muted text-foreground text-sm" role="status">
                {location.state.mensagem}
              </p>
            )}

            <button disabled={carregando} type="submit" className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-60">
              {carregando ? 'Entrando...' : 'Entrar'}
            </button>

            {erro && (
              <p className="p-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm" role="alert">
                {erro}
              </p>
            )}

            <div className="flex flex-col gap-2 text-sm text-center">
              <Link to="/esqueci-senha" className="text-muted-foreground hover:text-foreground transition-colors">
                Esqueci minha senha
              </Link>
              <Link to="/cadastro" className="text-primary hover:opacity-80 transition-opacity">
                Criar conta
              </Link>
              <Link to="/auth/request-recovery" className="text-primary hover:opacity-80 transition-opacity">
                Recuperar conta excluída
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
