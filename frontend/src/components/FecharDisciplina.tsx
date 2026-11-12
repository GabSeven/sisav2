import { useState } from 'react'
import { ModalFecharDisciplina } from './ModalFecharDisciplina'
import { Header } from './Header'

export interface AlunoConsolidacao {
  id: number
  nome: string
  ra: string
  av1: string
  av2: string
  mediaFinal: string
  faltas: string
  situacao: 'Aprovado' | 'Exame Final' | 'Reprovado' | 'Rep. por Falta' | 'Pendente'
}

interface FecharDisciplinaProps {
  nomeTurma?: string
  codigoTurma?: string
  alunos: AlunoConsolidacao[]
}

export function FecharDisciplina({
  nomeTurma = 'Banco de Dados',
  codigoTurma = 'DINO512-T01',
  alunos,
}: FecharDisciplinaProps) {
  const [turmaSelecionada, setTurmaSelecionada] = useState('Construção de Software')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDisciplinaBloqueada, setIsDisciplinaBloqueada] = useState(false)
  const [isEncerrando, setIsEncerrando] = useState(false)

  // Métricas calculadas para os cards
  const aprovados = alunos.filter((a) => a.situacao === 'Aprovado').length
  const exameFinal = alunos.filter((a) => a.situacao === 'Exame Final').length
  const reprovados = alunos.filter((a) => a.situacao === 'Reprovado').length
  const pendentes = alunos.filter((a) => a.situacao === 'Pendente').length

  const handleConfirmarEncerramento = () => {
    setIsEncerrando(true)
    // Simulação da chamada para a API
    setTimeout(() => {
      setIsEncerrando(false)
      setIsDisciplinaBloqueada(true)
      setIsModalOpen(false)
    }, 1000)
  }

  const getSituacaoBadge = (situacao: AlunoConsolidacao['situacao']) => {
    switch (situacao) {
      case 'Aprovado':
        return 'bg-emerald-100 text-emerald-700'
      case 'Exame Final':
        return 'bg-amber-100 text-amber-700'
      case 'Reprovado':
        return 'bg-red-100 text-red-700'
      case 'Rep. por Falta':
        return 'bg-[#FCE7F3] text-[#9D174D]'
      default:
        return 'bg-slate-100 text-slate-600'
    }
  }

  const getNotaColor = (nota: string) => {
    if (nota === '!') return 'text-red-500 font-semibold'
    const val = parseFloat(nota)
    if (isNaN(val)) return 'text-slate-700'
    if (val >= 7.0) return 'text-emerald-600 font-medium'
    if (val >= 5.0) return 'text-amber-600 font-medium'
    return 'text-red-600 font-medium'
  }

  return (
    <div className="min-h-screen bg-[#f1f5f9] text-slate-800">
      <Header
        titulo="Fechar Disciplina"
        subtitulo="Consolidar notas finais e encerrar o lançamento da turma"
      />

      <main className="px-6 pb-6 pt-1">
        {/* Bar de Seleção e Botão Escuro */}
        <div className="px-0 py-3 flex items-end justify-between">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2">
              TURMA
            </label>
            <select
              value={turmaSelecionada}
              onChange={(e) => setTurmaSelecionada(e.target.value)}
              disabled={isDisciplinaBloqueada}
              className="w-72 border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-700 bg-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
            >
              <option value="Construção de Software">Construção de Software</option>
              <option value="Banco de Dados">Banco de Dados</option>
            </select>
          </div>

          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            disabled={isDisciplinaBloqueada}
            className="bg-[#0F172A] hover:bg-slate-900 text-white font-medium text-sm px-6 py-2.5 rounded-lg transition-colors flex items-center gap-2.5 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            {isDisciplinaBloqueada ? 'Disciplina Fechada' : 'Fechar Disciplina'}
          </button>
        </div>

        {/* Cards de Métricas (Aprovados, Exame Final, Reprovados, Pendentes) */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-[#DCFCE7] rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-[#16A34A] uppercase tracking-wider mb-1">APROVADOS</p>
            <span className="text-3xl font-semibold font-[DM_sans] text-[#16A34A]">{aprovados}</span>
          </div>

          <div className="bg-[#FEF3C7]/70 rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-[#D97706] uppercase tracking-wider mb-1">EXAME FINAL</p>
            <span className="text-3xl font-semibold font-[DM_sans] text-[#D97706]">{exameFinal}</span>
          </div>

          <div className="bg-[#FEE2E2] rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-[#DC2626] uppercase tracking-wider mb-1">REPROVADOS</p>
            <span className="text-3xl font-semibold font-[DM_sans] text-[#DC2626]">{reprovados}</span>
          </div>

          <div className="bg-slate-100/70 rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">PENDENTES</p>
            <span className="text-3xl font-semibold font-[DM_sans] text-slate-400">{pendentes}</span>
          </div>
        </div>

        {/* Tabela de Notas e Situação */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900">
              Consolidação Final - {nomeTurma} ({codigoTurma})
            </h2>
          </div>

          <div className="grid grid-cols-12 px-6 py-3.5 bg-slate-50/80 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            <div className="col-span-5">ALUNO</div>
            <div className="col-span-1 text-center">AV1</div>
            <div className="col-span-1 text-center">AV2</div>
            <div className="col-span-2 text-center">MÉDIA FINAL</div>
            <div className="col-span-1 text-center">FALTAS</div>
            <div className="col-span-2 text-right pr-2">SITUAÇÃO</div>
          </div>

          <div className="divide-y divide-slate-100">
            {alunos.map((aluno) => (
              <div key={aluno.id} className="grid grid-cols-12 items-center px-6 py-4 hover:bg-slate-50/60 transition-colors">
                <div className="col-span-5">
                  <h3 className="text-sm font-semibold text-slate-800">{aluno.nome}</h3>
                  <p className="text-xs text-slate-400 font-medium mt-0.5">RA: {aluno.ra}</p>
                </div>

                <div className={`col-span-1 text-center text-sm ${getNotaColor(aluno.av1)}`}>
                  {aluno.av1}
                </div>

                <div className={`col-span-1 text-center text-sm ${getNotaColor(aluno.av2)}`}>
                  {aluno.av2}
                </div>

                <div className="col-span-2 flex justify-center">
                  <span className="border border-slate-200 rounded-lg px-4 py-1 text-xs font-semibold text-slate-800 bg-white">
                    {aluno.mediaFinal}
                  </span>
                </div>

                <div className="col-span-1 text-center text-xs font-medium text-slate-500">
                  {aluno.faltas}
                </div>

                <div className="col-span-2 flex justify-end">
                  <span className={`text-[11px] font-semibold px-3 py-1 rounded-full ${getSituacaoBadge(aluno.situacao)}`}>
                    {aluno.situacao}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Modal de Confirmação Dupla (T014.4) */}
        <ModalFecharDisciplina
          isOpen={isModalOpen}
          nomeDisciplina={`${nomeTurma} (${codigoTurma})`}
          totalAlunos={alunos.length}
          onClose={() => setIsModalOpen(false)}
          onConfirmarFechamento={handleConfirmarEncerramento}
          isLoading={isEncerrando}
        />
      </main>
    </div>
  )
}