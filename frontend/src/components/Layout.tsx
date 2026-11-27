import { Outlet, useLocation, useNavigate } from 'react-router'
import { Sidebar } from './SideBar'
import type { PerfilSidebar, RotaSidebarId, UsuarioSidebar } from './SideBar'

interface LayoutProps {
  perfil: PerfilSidebar
  usuario?: UsuarioSidebar
}

const MAPA_ROTAS_SIDEBAR: Record<string, RotaSidebarId> = {
  '/aluno': 'inicio',
  '/aluno/notas-faltas': 'notas-faltas',
  '/aluno/horario': 'horario',
  '/aluno/historico': 'historico',
  '/aluno/atividades': 'atividades',
  '/aluno/solicitacoes': 'solicitacoes',
  '/aluno/mensagens': 'mensagens',
  '/aluno/perfil': 'perfil',

  '/professor': 'inicio',
  '/professor/turmas': 'minhas-turmas',
  '/professor/notas': 'lancar-notas',
  '/professor/faltas': 'lancar-faltas',
  '/professor/alunos-afastados': 'alunos-afastados',
  '/professor/alunos-risco': 'alunos-risco',
  '/professor/fechar-disciplina': 'fechar-disciplina',
  '/professor/criterios': 'criterios-avaliacao',
  '/professor/mensagens': 'mensagens',
}

export function Layout({ perfil, usuario }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()

  // Remove barra final (ex: "/aluno/" -> "/aluno") e descobre o item ativo
  const caminhoAtual = location.pathname.replace(/\/+$/, '') || '/'
  const itemAtivo: RotaSidebarId = MAPA_ROTAS_SIDEBAR[caminhoAtual] ?? 'inicio'

  const handleSair = () => {
    localStorage.removeItem('@SISAV:token')
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-[#f1f5f9]">
      {/* Coluna fixa à esquerda */}
      <Sidebar
        perfil={perfil}
        itemAtivo={itemAtivo}
        usuario={usuario}
        onSelectItem={(item) => navigate(item.path)}
        onSair={handleSair}
      />

      {/* Área dinâmica à direita onde cada página será renderizada */}
      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  )
}