import { useEffect } from 'react'
import { ArrowLeft, BookOpen, Home as HomeIcon } from 'lucide-react'
import { Link, useNavigate } from 'react-router'

export function NotFound() {
  const navigate = useNavigate()

  useEffect(() => {
    document.title = 'Página não encontrada | Reflecta'
  }, [])

  return (
    <div className="home-page not-found-page">
      <header className="home-header not-found-header">
        <Link to="/" className="home-brand" aria-label="Reflecta — página inicial">
          <BookOpen aria-hidden="true" strokeWidth={1.5} />
          <span>Reflecta</span>
        </Link>
        <div className="home-header-actions">
          <Link className="home-login-link" to="/login">Entrar</Link>
          <Link className="home-primary-button" to="/cadastro">Criar conta</Link>
        </div>
      </header>

      <main className="not-found-main">
        <section className="not-found-copy" aria-labelledby="not-found-title">
          <span className="home-eyebrow">Erro 404 · Página não encontrada</span>
          <h1 id="not-found-title">Esta página não faz parte deste diário.</h1>
          <p>
            O endereço pode ter mudado, estar incompleto ou não existir. Você pode voltar à página anterior ou continuar pela página inicial do Reflecta.
          </p>
          <div className="not-found-actions">
            <Link className="home-primary-button home-large-button" to="/">
              <HomeIcon size={17} aria-hidden="true" /> Ir para o início
            </Link>
            <button className="home-secondary-button home-large-button" type="button" onClick={() => navigate(-1)}>
              <ArrowLeft size={17} aria-hidden="true" /> Voltar
            </button>
          </div>
        </section>

        <div className="not-found-illustration" aria-hidden="true">
          <span>404</span>
          <div className="not-found-page-sheet">
            <BookOpen strokeWidth={1.25} />
            <i />
            <i />
            <i />
          </div>
        </div>
      </main>
    </div>
  )
}
