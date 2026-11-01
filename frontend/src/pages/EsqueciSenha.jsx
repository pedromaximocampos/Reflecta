import { useState } from 'react'
import { BookOpen, Mail } from 'lucide-react'
import { Link } from 'react-router'
import { requestPasswordReset } from '../services/authApi'

export function EsqueciSenha() {
  const [email, setEmail] = useState('')
  const [enviado, setEnviado] = useState(false)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErro('')
    setEnviado(false)
    setCarregando(true)

    try {
      await requestPasswordReset(email)
      setEnviado(true)
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Não foi possível solicitar a recuperação.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-12">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="w-10 h-10 text-primary" strokeWidth={1.5} />
            <h1 className="text-4xl text-primary">Reflecta</h1>
          </div>
          <h2 className="text-xl text-foreground mb-2">Recuperar senha</h2>
          <p className="text-muted-foreground text-center max-w-sm">
            Informe seu e-mail para receber as instruções de recuperação.
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
                onChange={(event) => {
                  setEmail(event.target.value)
                  setEnviado(false)
                  setErro('')
                }}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="seu@email.com"
                required
              />
            </div>

            {enviado && (
              <div className="flex gap-3 p-4 bg-muted rounded-lg" role="status">
                <Mail className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <p className="text-sm text-muted-foreground">
                  Se o e-mail estiver cadastrado, você receberá as instruções para redefinir sua senha.
                </p>
              </div>
            )}

            {erro && (
              <p className="p-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm" role="alert">
                {erro}
              </p>
            )}

            <button disabled={carregando} type="submit" className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-60">
              {carregando ? 'Enviando...' : 'Enviar instruções'}
            </button>

            <div className="text-sm text-center">
              <Link to="/" className="text-primary hover:opacity-80 transition-opacity">
                Voltar para o login
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
