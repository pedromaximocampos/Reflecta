import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router'
import { MainLayout } from './components/MainLayout'
import { AuthenticatedLayout } from './components/AuthenticatedLayout'
import { AdminGuard } from './components/AdminGuard'
import { SessionExpiredModal } from './components/SessionExpiredModal'
import { SessionBootstrap } from './components/SessionBootstrap'
import { PageLoading } from './components/PageLoading'

const lazyPage = (loader, exportName) => lazy(() => loader().then((module) => ({ default: module[exportName] })))

const AnaliseCompartilhada = lazyPage(() => import('./pages/AnaliseCompartilhada'), 'AnaliseCompartilhada')
const AdminDashboard = lazyPage(() => import('./pages/AdminDashboard'), 'AdminDashboard')
const AdminFalhas = lazyPage(() => import('./pages/AdminFalhas'), 'AdminFalhas')
const AdminObraCadastro = lazyPage(() => import('./pages/AdminObraCadastro'), 'AdminObraCadastro')
const AdminObraDetalhe = lazyPage(() => import('./pages/AdminObraDetalhe'), 'AdminObraDetalhe')
const AdminObraPDF = lazyPage(() => import('./pages/AdminObraPDF'), 'AdminObraPDF')
const AdminObras = lazyPage(() => import('./pages/AdminObras'), 'AdminObras')
const AdminPassagens = lazyPage(() => import('./pages/AdminPassagens'), 'AdminPassagens')
const AdminTemas = lazyPage(() => import('./pages/AdminTemas'), 'AdminTemas')
const AdminAdministradores = lazyPage(() => import('./pages/AdminAdministradores'), 'AdminAdministradores')
const Cadastro = lazyPage(() => import('./pages/Cadastro'), 'Cadastro')
const Compartilhamentos = lazyPage(() => import('./pages/Compartilhamentos'), 'Compartilhamentos')
const ConfirmarExclusao = lazyPage(() => import('./pages/ConfirmarExclusao'), 'ConfirmarExclusao')
const ConfirmarRecuperacao = lazyPage(() => import('./pages/ConfirmarRecuperacao'), 'ConfirmarRecuperacao')
const Dashboard = lazyPage(() => import('./pages/Dashboard'), 'Dashboard')
const EsqueciSenha = lazyPage(() => import('./pages/EsqueciSenha'), 'EsqueciSenha')
const HistoricoAnalises = lazyPage(() => import('./pages/HistoricoAnalises'), 'HistoricoAnalises')
const Journaling = lazyPage(() => import('./pages/Journaling'), 'Journaling')
const Login = lazyPage(() => import('./pages/Login'), 'Login')
const ObraRecomendada = lazyPage(() => import('./pages/ObraRecomendada'), 'ObraRecomendada')
const Orientacoes = lazyPage(() => import('./pages/Orientacoes'), 'Orientacoes')
const Perfil = lazyPage(() => import('./pages/Perfil'), 'Perfil')
const Recomendacoes = lazyPage(() => import('./pages/Recomendacoes'), 'Recomendacoes')
const RecuperarConta = lazyPage(() => import('./pages/RecuperarConta'), 'RecuperarConta')
const Reflexao = lazyPage(() => import('./pages/Reflexao'), 'Reflexao')
const Reflexoes = lazyPage(() => import('./pages/Reflexoes'), 'Reflexoes')
const ResetarSenha = lazyPage(() => import('./pages/ResetarSenha'), 'ResetarSenha')
const VerificarEmail = lazyPage(() => import('./pages/VerificarEmail'), 'VerificarEmail')
const AceitarConviteAdmin = lazyPage(() => import('./pages/AceitarConviteAdmin'), 'AceitarConviteAdmin')

function RouteLoading() {
  return <div className="route-loading-shell"><PageLoading variant="detail" label="Preparando a página…" /></div>
}

function App() {
  return (
    <BrowserRouter>
      <SessionExpiredModal />
      <SessionBootstrap>
        <Suspense fallback={<RouteLoading />}>
        <Routes>
          <Route path="/compartilhamento" element={<AnaliseCompartilhada />} />
          <Route path="/" element={<Login />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/esqueci-senha" element={<EsqueciSenha />} />
          <Route path="/auth/reset-password" element={<ResetarSenha />} />
          <Route element={<AuthenticatedLayout />}>
            <Route path="/inicio" element={<Dashboard />} />
            <Route path="/inicio/diario" element={<Journaling />} />
            <Route path="/inicio/reflexoes" element={<Reflexoes />} />
            <Route path="/inicio/analises" element={<HistoricoAnalises />} />
            <Route path="/inicio/compartilhamentos" element={<Compartilhamentos />} />
            <Route path="/inicio/recomendacoes" element={<Recomendacoes />} />
            <Route path="/inicio/recomendacoes/:workId" element={<ObraRecomendada />} />
            <Route path="/inicio/orientacoes" element={<Orientacoes />} />
            <Route path="/inicio/reflexoes/:id" element={<Reflexao />} />
            <Route path="/inicio/reflexoes/:id/editar" element={<Reflexao editing />} />
            <Route path="/auth/perfil" element={<Perfil />} />
          </Route>
          <Route path="/auth">
            <Route path="verify-email" element={<VerificarEmail />} />
            <Route path="request-recovery" element={<RecuperarConta />} />
            <Route path="recovery" element={<ConfirmarRecuperacao />} />
            <Route path="delete" element={<ConfirmarExclusao />} />
            <Route path="admin-invitation" element={<AceitarConviteAdmin />} />
          </Route>
          <Route element={<AdminGuard />}><Route path="/deshboard" element={<MainLayout admin />}>
            <Route index element={<AdminDashboard />} />
            <Route path="falhas" element={<AdminFalhas />} />
            <Route path="temas" element={<AdminTemas />} />
            <Route path="obras" element={<AdminObras />} />
            <Route path="obras/nova" element={<AdminObraCadastro />} />
            <Route path="obras/:workId" element={<AdminObraDetalhe />} />
            <Route path="obras/:workId/pdf" element={<AdminObraPDF />} />
            <Route path="passagens" element={<AdminPassagens />} />
            <Route path="administradores" element={<AdminAdministradores />} />
          </Route>
          </Route>
        </Routes>
        </Suspense>
      </SessionBootstrap>
    </BrowserRouter>
  )
}

export default App
