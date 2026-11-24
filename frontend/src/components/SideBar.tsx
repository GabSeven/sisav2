import type { ReactNode } from 'react'

export type PerfilSidebar = 'aluno' | 'professor'

export type RotaAlunoId =
  | 'inicio'
  | 'notas-faltas'
  | 'horario'
  | 'historico'
  | 'atividades'
  | 'solicitacoes'
  | 'mensagens'
  | 'perfil'

export type RotaProfessorId =
  | 'inicio'
  | 'minhas-turmas'
  | 'lancar-notas'
  | 'lancar-faltas'
  | 'alunos-afastados'
  | 'alunos-risco'
  | 'fechar-disciplina'
  | 'criterios-avaliacao'
  | 'mensagens'

export type RotaSidebarId = RotaAlunoId | RotaProfessorId

export interface ItemMenuSidebar {
    id: RotaSidebarId
    label: string
    path: string
    icone: ReactNode
}

export interface UsuarioSidebar {
    nome: string
    identificacao: string
    perfil?: string
}

interface SidebarProps {
    perfil?: PerfilSidebar
    itemAtivo?: RotaSidebarId
    onSelectItem?: (item: ItemMenuSidebar) => void
    onSair?: () => void
    usuario?: UsuarioSidebar
}

const ITENS_MENU_ALUNO: ItemMenuSidebar[] = [
  {
    id: 'inicio',
    label: 'Início',
    path: '/aluno',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10.5L12 3l9 7.5" />
        <path d="M5 9.5V19a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5" />
        <path d="M9.5 20v-6h5v6" />
      </svg>
    ),
  },
  {
    id: 'notas-faltas',
    label: 'Notas e Faltas',
    path: '/aluno/notas-faltas',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <line x1="6" y1="19" x2="6" y2="13" />
        <line x1="12" y1="19" x2="12" y2="6" />
        <line x1="18" y1="19" x2="18" y2="10" />
      </svg>
    ),
  },
  {
    id: 'horario',
    label: 'Horário de Aulas',
    path: '/aluno/horario',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="17" rx="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
  {
    id: 'historico',
    label: 'Histórico Escolar',
    path: '/aluno/historico',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      </svg>
    ),
  },
  {
    id: 'atividades',
    label: 'Atividades (AAC)',
    path: '/aluno/atividades',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  },
  {
    id: 'solicitacoes',
    label: 'Solicitações',
    path: '/aluno/solicitacoes',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="8" y1="13" x2="16" y2="13" />
        <line x1="8" y1="17" x2="13" y2="17" />
      </svg>
    ),
  },
  {
    id: 'mensagens',
    label: 'Mensagens',
    path: '/aluno/mensagens',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
  },
  {
    id: 'perfil',
    label: 'Perfil',
    path: '/aluno/perfil',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="8" r="4" />
        <path d="M5 20a7 7 0 0 1 14 0" />
      </svg>
    ),
  },
]

const ITENS_MENU_PROFESSOR: ItemMenuSidebar[] = [
  {
    id: 'inicio',
    label: 'Início',
    path: '/professor',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10.5L12 3l9 7.5" />
        <path d="M5 9.5V19a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5" />
        <path d="M9.5 20v-6h5v6" />
      </svg>
    ),
  },
  {
    id: 'minhas-turmas',
    label: 'Minhas Turmas',
    path: '/professor/turmas',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    id: 'lancar-notas',
    label: 'Lançar Notas',
    path: '/professor/notas',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
      </svg>
    ),
  },
  {
    id: 'lancar-faltas',
    label: 'Lançar Faltas',
    path: '/professor/faltas',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
    ),
  },
  {
    id: 'alunos-afastados',
    label: 'Alunos Afastados',
    path: '/professor/alunos-afastados',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
  },
  {
    id: 'alunos-risco',
    label: 'Alunos em Risco',
    path: '/professor/alunos-risco',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
  {
    id: 'fechar-disciplina',
    label: 'Fechar Disciplina',
    path: '/professor/fechar-disciplina',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
    ),
  },
  {
    id: 'criterios-avaliacao',
    label: 'Critérios de Avaliação',
    path: '/professor/criterios',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <line x1="6" y1="19" x2="6" y2="13" />
        <line x1="12" y1="19" x2="12" y2="6" />
        <line x1="18" y1="19" x2="18" y2="10" />
      </svg>
    ),
  },
  {
    id: 'mensagens',
    label: 'Mensagens',
    path: '/professor/mensagens',
    icone: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
  },
]

const USUARIO_PADRAO_POR_PERFIL: Record<PerfilSidebar, Required<UsuarioSidebar>> = {
  aluno: {
    nome: 'João Vitor',
    identificacao: 'ra139617',
    perfil: 'UEM · Aluno',
  },
  professor: {
    nome: 'Renato Balancieri',
    identificacao: 'rbalancieri',
    perfil: 'UEM · Professor',
  },
}

function obterIniciais(nome: string): string {
    const partes = nome.trim().split(/\s+/)
    if (partes.length === 0) return 'US'
    if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase()
    return `${partes[0][0]}${partes[partes.length - 1][0]}`.toUpperCase()
}

export function Sidebar({
    perfil = 'aluno',
    itemAtivo = 'inicio',
    onSelectItem,
    onSair,
    usuario
}: SidebarProps) {
    const itensMenu = perfil === 'professor' ? ITENS_MENU_PROFESSOR : ITENS_MENU_ALUNO
    const dadosPadrao = USUARIO_PADRAO_POR_PERFIL[perfil]
    const nomeExibido = usuario?.nome ?? dadosPadrao.nome
    const identificacaoExibida = usuario?.identificacao ?? dadosPadrao.identificacao
    const subtituloExibido = usuario?.perfil ?? dadosPadrao.perfil

  return (
    <aside className="w-64 min-h-screen bg-[#0F172A] text-slate-300 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Cabeçalho Institucional */}
        <div className="px-5 py-6 border-b border-slate-800/80 flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#1D4ED8] flex items-center justify-center text-white shrink-0 shadow-sm">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3L2 8.5L12 14L22 8.5L12 3Z" />
              <path d="M2 14L12 19.5L22 14L19.6 12.7L12 16.9L4.4 12.7L2 14Z" />
            </svg>
          </div>

          <div className="min-w-0">
            <h1 className="font-heading text-base font-semibold text-white leading-tight tracking-tight">
              SISAV 2
            </h1>
            <p className="text-xs text-slate-400 mt-0.5 truncate">
              {subtituloExibido}
            </p>
          </div>
        </div>

        {/* Navegação Principal */}
        <nav aria-label="Menu principal" className="px-3 py-5 space-y-1">
          {itensMenu.map((item) => {
            const ativo = item.id === itemAtivo

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectItem?.(item)}
                className={`w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-sm font-medium transition-colors cursor-pointer ${
                  ativo
                    ? 'bg-[#1D4ED8] text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
              >
                <span className={ativo ? 'text-white' : 'text-slate-400'}>
                  {item.icone}
                </span>
                <span className="truncate">{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Rodapé do Usuário e Logout */}
      <div className="px-5 py-5 border-t border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#1D4ED8] flex items-center justify-center text-white font-semibold text-sm shrink-0">
            {obterIniciais(nomeExibido)}
          </div>

          <div className="min-w-0">
            <p className="text-sm font-semibold text-white leading-tight truncate">
              {nomeExibido}
            </p>
            <p className="text-xs text-slate-400 mt-0.5 truncate">
              @{identificacaoExibida}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onSair}
          className="mt-5 w-full flex items-center gap-3.5 px-1 py-1.5 text-sm font-medium text-slate-400 hover:text-red-400 transition-colors cursor-pointer"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          <span>Sair</span>
        </button>
      </div>
    </aside>
  )
}