import type { ReactNode } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router'

import { login, type Credenciais } from '@/modules/auth/api'
import { LoginPage } from '@/modules/auth/LoginPage'
import { lerSessao, rotaInicialPorPerfil, salvarSessao } from '@/modules/auth/session'
import { Painel } from '@/modules/painel/Painel'

function RequireAuth({ children }: { children: ReactNode }) {
  if (lerSessao() === null) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function LoginRoute() {
  const navegar = useNavigate()

  async function autenticar(credenciais: Credenciais) {
    const sessao = await login(credenciais)
    salvarSessao(sessao)
    navegar(rotaInicialPorPerfil[sessao.perfil], { replace: true })
  }

  return <LoginPage onSubmit={autenticar} />
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route
        path="/aluno"
        element={
          <RequireAuth>
            <Painel
              titulo="Painel do Aluno"
              descricao="Em breve: consulta de disciplinas, matrícula e declarações."
            />
          </RequireAuth>
        }
      />
      <Route
        path="/professor"
        element={
          <RequireAuth>
            <Painel
              titulo="Painel do Professor"
              descricao="Em breve: turmas, horários e lançamento de notas."
            />
          </RequireAuth>
        }
      />
      <Route
        path="/gestor"
        element={
          <RequireAuth>
            <Painel
              titulo="Painel do Gestor"
              descricao="Em breve: gestão acadêmica e relatórios."
            />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
