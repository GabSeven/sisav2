import type { ReactNode } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router'

import { login, type Credenciais } from '@/modules/auth/api'
import { LoginPage } from '@/modules/auth/LoginPage'
import { lerSessao, rotaInicialPorPerfil, salvarSessao } from '@/modules/auth/session'
import { Painel } from '@/modules/painel/Painel'
import { Layout } from '@/components/Layout'

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

      {/* Área do Aluno com Sidebar */}
      <Route
        element={
          <RequireAuth>
            <Layout perfil="aluno" />
          </RequireAuth>
        }
      >
        <Route
          path="/aluno"
          element={
            <Painel
              titulo="Painel do Aluno"
              descricao="Em breve: consulta de disciplinas, matrícula e declarações."
            />
          }
        />
        <Route
          path="/aluno/notas-faltas"
          element={
            <Painel
              titulo="Notas e Faltas"
              descricao="Boletim acadêmico, médias e projeção de notas."
            />
          }
        />
        <Route
          path="/aluno/horario"
          element={<Painel titulo="Horário de Aulas" descricao="Grade horária do semestre." />}
        />
        <Route
          path="/aluno/historico"
          element={<Painel titulo="Histórico Escolar" descricao="Notas e Faltas das disciplinas cursadas." />}
        />
        <Route
          path="/aluno/atividades"
          element={<Painel titulo="Atividades (AAC)" descricao="Atividades acadêmicas complementares." />}
        />
        <Route
          path="/aluno/solicitacoes"
          element={<Painel titulo="Solicitações" descricao="Requerimentos e protocolos acadêmicos." />}
        />
        <Route
          path="/aluno/mensagens"
          element={<Painel titulo="Mensagens" descricao="Comunicados e mensagens de Alunos e Professores" />}
        />
        <Route
          path="/aluno/perfil"
          element={<Painel titulo="Perfil" descricao="Dados cadastrais do aluno." />}
        />
      </Route>

      {/* Área do Professor com Sidebar */}
      <Route
        element={
          <RequireAuth>
            <Layout perfil="professor" />
          </RequireAuth>
        }
      >
        <Route
          path="/professor"
          element={
            <Painel
              titulo="Painel do Professor"
              descricao="Em breve: turmas, horários e lançamento de notas."
            />
          }
        />
        <Route
          path="/professor/turmas"
          element={<Painel titulo="Minhas Turmas" descricao="Turmas atribuídas no semestre." />}
        />
        <Route
          path="/professor/notas"
          element={<Painel titulo="Lançar Notas" descricao="Registro de avaliações por turma." />}
        />
        <Route
          path="/professor/faltas"
          element={<Painel titulo="Lançar Faltas" descricao="Chamada e controle de frequência." />}
        />
        <Route
          path="/professor/alunos-afastados"
          element={<Painel titulo="Alunos Afastados" descricao="Acompanhamento alunos em afastamento." />}
        />
        <Route
          path="/professor/alunos-risco"
          element={<Painel titulo="Alunos em Risco" descricao="Alertas de reprovação por nota ou falta." />}
        />
        <Route
          path="/professor/fechar-disciplina"
          element={<Painel titulo="Fechar Disciplina" descricao="Consolidação de médias e encerramento." />}
        />
        <Route
          path="/professor/criterios"
          element={<Painel titulo="Critérios de Avaliação" descricao="Configuração de pesos e avaliações." />}
        />
        <Route
          path="/professor/mensagens"
          element={<Painel titulo="Mensagens" descricao="Comunicação com as turmas." />}
        />
      </Route>

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