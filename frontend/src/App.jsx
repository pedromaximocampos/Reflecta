import { AnaliseCompartilhada } from './pages/AnaliseCompartilhada'
import { AdminFalhas } from './pages/AdminFalhas'
import { BrowserRouter, Route, Routes } from 'react-router'
import { MainLayout } from './components/MainLayout'
import { AuthenticatedLayout } from './components/AuthenticatedLayout'
import { Cadastro } from './pages/Cadastro'
import { Dashboard } from './pages/Dashboard'
import { AdminDashboard } from './pages/AdminDashboard'
import { Journaling } from './pages/Journaling'
import { Reflexoes } from './pages/Reflexoes'
import { Reflexao } from './pages/Reflexao'
import { EsqueciSenha } from './pages/EsqueciSenha'
import { ResetarSenha } from './pages/ResetarSenha'
import { Login } from './pages/Login'
import { Perfil } from './pages/Perfil'
import { RecuperarConta } from './pages/RecuperarConta'
import { ConfirmarRecuperacao } from './pages/ConfirmarRecuperacao'
import { ConfirmarExclusao } from './pages/ConfirmarExclusao'
import { AdminTemas } from './pages/AdminTemas'
import { AdminGuard } from './components/AdminGuard'
import { AdminObras } from './pages/AdminObras'
import { AdminObraCadastro } from './pages/AdminObraCadastro'
import { AdminObraDetalhe } from './pages/AdminObraDetalhe'
import { AdminObraPDF } from './pages/AdminObraPDF'
import { AdminPassagens } from './pages/AdminPassagens'
import { VerificarEmail } from './pages/VerificarEmail'
import { SessionExpiredModal } from './components/SessionExpiredModal'
import { SessionBootstrap } from './components/SessionBootstrap'

function App() {
  return (
    <BrowserRouter>
      <SessionExpiredModal />
      <SessionBootstrap>
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
            <Route path="/inicio/reflexoes/:id" element={<Reflexao />} />
            <Route path="/inicio/reflexoes/:id/editar" element={<Reflexao editing />} />
            <Route path="/auth/perfil" element={<Perfil />} />
          </Route>
          <Route path="/auth">
            <Route path="verify-email" element={<VerificarEmail />} />
            <Route path="request-recovery" element={<RecuperarConta />} />
            <Route path="recovery" element={<ConfirmarRecuperacao />} />
            <Route path="delete" element={<ConfirmarExclusao />} />
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
          </Route>
          </Route>
        </Routes>
      </SessionBootstrap>
    </BrowserRouter>
  )
}

export default App
