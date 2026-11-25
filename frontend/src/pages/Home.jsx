import { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, Feather, LibraryBig, LockKeyhole, Sparkles } from 'lucide-react'
import { Link } from 'react-router'
import { getFeaturedWork } from '../services/publicHomeApi'

const benefits = [
  {
    icon: Feather,
    title: 'Escrita com intenção',
    description: 'Registre o que aconteceu, reconheça padrões e transforme pensamentos dispersos em reflexões que você pode revisitar.',
  },
  {
    icon: LibraryBig,
    title: 'Referências com curadoria',
    description: 'Relacione suas reflexões a passagens filosóficas revisadas, preservando a fonte e o contexto de cada obra.',
  },
  {
    icon: LockKeyhole,
    title: 'Você decide o que compartilhar',
    description: 'Suas entradas permanecem pessoais. Quando quiser, compartilhe uma análise específica por um link temporário.',
  },
]

const steps = [
  ['01', 'Escreva com liberdade', 'Crie uma reflexão sobre o seu dia, uma escolha ou uma pergunta que continua com você.'],
  ['02', 'Descubra novas perspectivas', 'O Reflecta identifica temas relevantes e aproxima sua reflexão de passagens revisadas do catálogo.'],
  ['03', 'Acompanhe sua trajetória', 'Releia entradas, observe temas recorrentes e gere análises de diferentes períodos da sua vida.'],
  ['04', 'Amplie seu repertório', 'Conheça obras relacionadas aos temas das suas reflexões e encontre outras perspectivas para explorar.'],
  ['05', 'Compartilhe quando quiser', 'Crie um acesso temporário para dividir uma análise com um profissional ou alguém da sua confiança.'],
]

const fallbackFeaturedWork = {
  title: 'Meditações',
  author_name: 'Marco Aurélio',
  synopsis: 'Reflexões sobre escolhas, responsabilidade e a maneira como respondemos ao que acontece ao nosso redor.',
  cover_image_url: 'https://d25kcqqrg2unum.cloudfront.net/works/01M82GPDE08G7YB2NT8VFN614M/cover/01M82GPG7YQAXXGFMRWQY7S7QB.webp',
  themes: [{ theme_id: 'control', label: 'O que posso controlar', color: '#3F5B46' }],
  passage: {
    short_text: 'Se estiver em seu poder, corrija o que está errado; se não estiver, para que se queixar?',
    locator: 'pp. 111–112',
  },
}

export function Home() {
  const [featuredWork, setFeaturedWork] = useState(fallbackFeaturedWork)
  const [isDailyFeature, setIsDailyFeature] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    getFeaturedWork({ signal: controller.signal })
      .then((work) => {
        if (work?.passage?.short_text) {
          setFeaturedWork(work)
          setIsDailyFeature(true)
        }
      })
      .catch(() => undefined)
    return () => controller.abort()
  }, [])

  return (
    <div className="home-page">
      <header className="home-header">
        <Link to="/" className="home-brand" aria-label="Reflecta — página inicial">
          <BookOpen aria-hidden="true" strokeWidth={1.5} />
          <span>Reflecta</span>
        </Link>
        <nav className="home-nav" aria-label="Navegação principal">
          <a href="#como-funciona">Como funciona</a>
          <a href="#beneficios">Benefícios</a>
          <a href="#acervo">Acervo</a>
        </nav>
        <div className="home-header-actions">
          <Link className="home-login-link" to="/login">Entrar</Link>
          <Link className="home-primary-button" to="/cadastro">Criar conta</Link>
        </div>
      </header>

      <main>
        <section className="home-hero">
          <div className="home-hero-copy">
            <span className="home-eyebrow"><Sparkles size={15} aria-hidden="true" /> Diário reflexivo com referências filosóficas</span>
            <h1>Escreva para compreender.<br /><em>Releia para evoluir.</em></h1>
            <p>
              Um espaço pessoal para organizar pensamentos, reconhecer os temas que atravessam sua vida e encontrar novas perspectivas em obras que convidam à reflexão.
            </p>
            <div className="home-hero-actions">
              <Link className="home-primary-button home-large-button" to="/cadastro">Começar uma reflexão <ArrowRight size={17} aria-hidden="true" /></Link>
              <a className="home-secondary-button home-large-button" href="#como-funciona">Conhecer o Reflecta</a>
            </div>
            <small>Escrita privada · Conteúdo com curadoria · Compartilhamento sob seu controle</small>
          </div>

          <div className="home-reflection-preview" aria-label="Exemplo de reflexão no Reflecta">
            <div className="home-preview-topline"><span>Uma página do seu diário</span><span>Hoje</span></div>
            <h2>O peso de controlar tudo</h2>
            <p className="home-preview-text">
              Percebi que parte do meu cansaço vem da tentativa de prever cada resultado. Talvez eu possa cuidar melhor das minhas escolhas sem exigir controle sobre tudo o que acontece depois.
            </p>
            <div className="home-preview-theme"><i /> O que posso controlar</div>
            <div className="home-preview-passage">
              <BookOpen size={18} aria-hidden="true" />
              <div><span>Uma passagem para continuar</span><p>“Se estiver em seu poder, corrija o que está errado; se não estiver, para que se queixar?”</p><small>Marco Aurélio · Meditações · pp. 111–112</small></div>
            </div>
          </div>
        </section>

        <section id="como-funciona" className="home-section home-process-section">
          <div className="home-section-heading">
            <span>Como funciona</span>
            <h2>Da experiência à reflexão, sem perder sua própria voz.</h2>
            <p>A tecnologia organiza e aproxima perspectivas. O sentido da reflexão continua sendo construído por você.</p>
          </div>
          <div className="home-steps">
            {steps.map(([number, title, description]) => (
              <article key={number}>
                <span>{number}</span>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="beneficios" className="home-section home-benefits-section">
          <div className="home-section-heading home-section-heading-left">
            <span>Um diário que continua com você</span>
            <h2>Mais do que guardar textos: criar continuidade.</h2>
          </div>
          <div className="home-benefits-grid">
            {benefits.map(({ icon: Icon, title, description }) => (
              <article key={title}>
                <div><Icon size={23} aria-hidden="true" strokeWidth={1.5} /></div>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="acervo" className="home-section home-featured-section">
          <div className="home-section-heading">
            <span>Do acervo para sua reflexão</span>
            <h2>Uma obra para conhecer por outra perspectiva.</h2>
            <p>Todos os dias, um encontro com uma obra e os temas que ela pode ajudar você a explorar.</p>
          </div>
          <article className="home-featured-work">
            <div className="home-featured-cover">
              {featuredWork.cover_image_url
                ? <img src={featuredWork.cover_image_url} alt={`Capa de ${featuredWork.title}`} />
                : <div className="home-featured-cover-fallback"><BookOpen size={52} strokeWidth={1.25} aria-hidden="true" /><span>Obra do acervo</span></div>}
            </div>
            <div className="home-featured-copy">
              <span className="home-featured-kicker">{isDailyFeature ? 'Destaque do acervo de hoje' : 'Uma obra do acervo'}</span>
              <h3>{featuredWork.title}</h3>
              <p className="home-featured-author">{featuredWork.author_name}</p>
              <p className="home-featured-synopsis">{featuredWork.synopsis}</p>
              {!!featuredWork.themes?.length && <div className="home-featured-themes" aria-label="Temas relacionados à obra">
                {featuredWork.themes.slice(0, 3).map((theme) => <span key={theme.theme_id || theme.label} style={{ '--theme-color': theme.color }}>{theme.label}</span>)}
              </div>}
              <blockquote>
                <p>“{featuredWork.passage.short_text}”</p>
                <footer>{featuredWork.title} · {featuredWork.author_name}{featuredWork.passage.locator ? ` · ${featuredWork.passage.locator}` : ''}</footer>
              </blockquote>
              <Link className="home-secondary-button" to="/cadastro">Explorar o acervo no Reflecta <ArrowRight size={15} aria-hidden="true" /></Link>
            </div>
          </article>
        </section>

        <section className="home-closing">
          <div>
            <span>Seu próximo pensamento pode ser um começo.</span>
            <h2>Crie um espaço para ouvir com mais atenção o que você já tem a dizer.</h2>
          </div>
          <Link className="home-primary-button home-large-button" to="/cadastro">Criar meu diário <ArrowRight size={17} aria-hidden="true" /></Link>
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-brand"><BookOpen aria-hidden="true" strokeWidth={1.5} /><span>Reflecta</span></div>
        <div className="home-footer-links"><Link to="/uso-responsavel">Uso responsável e privacidade</Link></div>
        <span>© {new Date().getFullYear()} Reflecta</span>
        <p className="home-footer-disclaimer">O Reflecta apoia a escrita reflexiva e a ampliação de repertório cultural. Não realiza diagnóstico, tratamento ou atendimento psicológico e não substitui acompanhamento profissional.</p>
      </footer>
    </div>
  )
}
