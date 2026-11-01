import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { BookOpen, ShieldCheck } from 'lucide-react'
import { signup } from '../services/authApi'

export function Cadastro() {
  const [nome, setNome] = useState('')
  const [sobrenome, setSobrenome] = useState('')
  const [nomeUsuario, setNomeUsuario] = useState('')
  const [dataNascimento, setDataNascimento] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErro('')

    if (senha !== confirmarSenha) {
      setErro('As senhas não coincidem.')
      return
    }

    setCarregando(true)

    try {
      await signup({
        email,
        username: nomeUsuario,
        name: nome,
        surname: sobrenome,
        date_of_birth: dataNascimento,
        password: senha,
        password_confirm: confirmarSenha,
      })
      navigate('/', { state: { mensagem: 'Conta criada. Verifique seu e-mail antes de entrar.' } })
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Não foi possível criar a conta.')
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
          <h2 className="text-xl text-foreground mb-2">Criar conta</h2>
          <p className="text-muted-foreground text-center max-w-sm">
            Comece sua jornada de autoconhecimento
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-card rounded-2xl shadow-sm border border-border p-8">
          <div className="space-y-5">
            <div>
              <label htmlFor="nome" className="block mb-2 text-foreground">Nome</label>
              <input
                id="nome"
                type="text"
                value={nome}
                onChange={(event) => setNome(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Seu nome"
                required
              />
            </div>

            <div>
              <label htmlFor="sobrenome" className="block mb-2 text-foreground">Sobrenome</label>
              <input
                id="sobrenome"
                type="text"
                value={sobrenome}
                onChange={(event) => setSobrenome(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Seu sobrenome"
                required
              />
            </div>

            <div>
              <label htmlFor="nome-usuario" className="block mb-2 text-foreground">Nome de usuário</label>
              <input
                id="nome-usuario"
                type="text"
                value={nomeUsuario}
                onChange={(event) => setNomeUsuario(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="nome_usuario"
                minLength={3}
                required
              />
            </div>

            <div>
              <label htmlFor="data-nascimento" className="block mb-2 text-foreground">Data de nascimento</label>
              <input
                id="data-nascimento"
                type="date"
                value={dataNascimento}
                onChange={(event) => setDataNascimento(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                required
              />
            </div>

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
                minLength={12}
                required
              />
              <p className="text-sm text-muted-foreground mt-2">
                Use pelo menos 12 caracteres, incluindo maiúscula, minúscula, número e símbolo.
              </p>
            </div>

            <div>
              <label htmlFor="confirmar" className="block mb-2 text-foreground">Confirmação de senha</label>
              <input
                id="confirmar"
                type="password"
                value={confirmarSenha}
                onChange={(event) => setConfirmarSenha(event.target.value)}
                className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="••••••••"
                minLength={12}
                required
              />
            </div>

            <div className="flex gap-3 p-4 bg-muted rounded-lg">
              <ShieldCheck className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                Seus registros são privados e protegidos.
              </p>
            </div>

            <button disabled={carregando} type="submit" className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-60">
              {carregando ? 'Criando conta...' : 'Criar conta'}
            </button>

            {erro && (
              <p className="p-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm" role="alert">
                {erro}
              </p>
            )}

            <div className="text-sm text-center">
              <span className="text-muted-foreground">Já tem uma conta? </span>
              <Link to="/" className="text-primary hover:opacity-80 transition-opacity">
                Fazer login
              </Link>
              <Link to="/auth/request-recovery" className="block mt-3 text-primary hover:opacity-80 transition-opacity">
                Recuperar conta excluída
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
