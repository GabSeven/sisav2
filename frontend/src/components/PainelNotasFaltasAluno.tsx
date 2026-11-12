import { useState } from 'react'
import { Header } from './Header'

export interface DisciplinaBoletim {
  id: number
  ano: string
  semestre: string
  turma: string
  cargaHoraria: string
  nome: string
  avs?: string
  media: number | null
  faltasAtuais: number
  limiteFaltas: number
  situacao: 'Aprovado' | 'Exame Final' | 'Reprovado' | 'Em Curso'
}

interface PainelNotasFaltasAlunoProps {
  disciplinas?: DisciplinaBoletim[]
}

const disciplinasPadrao: DisciplinaBoletim[] = [
  {
    id: 1,
    ano: '2026',
    semestre: '1',
    turma: 'C56',
    cargaHoraria: '68h',
    nome: 'Compiladores',
    media: 7.8,
    faltasAtuais: 4,
    limiteFaltas: 17,
    situacao: 'Aprovado',
  },
  {
    id: 2,
    ano: '2026',
    semestre: '1',
    turma: 'C56',
    cargaHoraria: '68h',
    nome: 'Algoritmos em Grafos',
    media: 8.8,
    faltasAtuais: 6,
    limiteFaltas: 17,
    situacao: 'Aprovado',
  },
  {
    id: 3,
    ano: '2026',
    semestre: '2',
    turma: 'D67',
    cargaHoraria: '68h',
    nome: 'Computação Gráfica',
    media: 7.5,
    faltasAtuais: 2,
    limiteFaltas: 17,
    situacao: 'Aprovado',
  },
  {
    id: 4,
    ano: '2026',
    semestre: '2',
    turma: 'D67',
    cargaHoraria: '34h',
    nome: 'Noções de Direito',
    media: 10.0,
    faltasAtuais: 0,
    limiteFaltas: 8,
    situacao: 'Aprovado',
  },
  {
    id: 5,
    ano: '2026',
    semestre: '2',
    turma: 'C56',
    cargaHoraria: '68h',
    nome: 'Construção de Software',
    media: 8.5,
    faltasAtuais: 3,
    limiteFaltas: 17,
    situacao: 'Aprovado',
  },
]

export function PainelNotasFaltasAluno({
  disciplinas = disciplinasPadrao,
}: PainelNotasFaltasAlunoProps) {
  const [ano, setAno] = useState('2026')
  const [semestre, setSemestre] = useState('2')
  const [busca, setBusca] = useState('')

  const disciplinasDoPeriodo = disciplinas.filter(
    (d) => d.ano === ano && d.semestre === semestre
  )

  const disciplinasFiltradas = disciplinasDoPeriodo.filter(
    (d) =>
      d.nome.toLowerCase().includes(busca.toLowerCase()) ||
      d.turma.toLowerCase().includes(busca.toLowerCase())
  )

  // Métricas consolidadas para os 4 cards superiores
  const disciplinasComNota = disciplinasDoPeriodo.filter((d) => d.media !== null)
  const mediaGeral =
    disciplinasComNota.length > 0
      ? disciplinasComNota.reduce((acc, d) => acc + (d.media ?? 0), 0) /
        disciplinasComNota.length
      : 0

  const totalAprovacoes = disciplinasDoPeriodo.filter((d) => d.situacao === 'Aprovado').length
  const totalFaltas = disciplinasDoPeriodo.reduce((acc, d) => acc + d.faltasAtuais, 0)
  const riscoReprovacao = disciplinasDoPeriodo.filter(
    (d) =>
      (d.media !== null && d.media < 7.0) ||
      (d.limiteFaltas > 0 && d.faltasAtuais / d.limiteFaltas >= 0.75)
  ).length

  const getMediaColor = (media: number | null) => {
    if (media === null) return 'text-slate-400'
    if (media >= 7.0) return 'text-emerald-600'
    if (media >= 5.0) return 'text-amber-600'
    return 'text-red-600'
  }
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
  const getFaltaNumeroColor = (faltas: number, limite: number) => {
    const ratio = limite > 0 ? faltas / limite : 0
    if (ratio >= 0.75) return 'text-red-600'
    if (ratio >= 0.5) return 'text-amber-600'
    return 'text-emerald-600'
  }

  const getSituacaoBadge = (situacao: DisciplinaBoletim['situacao']) => {
    switch (situacao) {
      case 'Aprovado':
        return 'bg-emerald-100 text-emerald-700'
      case 'Exame Final':
        return 'bg-amber-100 text-amber-700'
      case 'Reprovado':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-slate-100 text-slate-600'
    }
  }

  return (
    <div className="min-h-screen bg-[#f1f5f9] text-slate-800">
      <Header
        titulo="Notas e Faltas"
        subtitulo="Boletim do semestre atual"
        busca={busca}
        onBuscaChange={setBusca}
      />

      {/* Conteúdo Principal */}
      <main className="px-6 pb-6 pt-1">
        {/* Filtros de Ano e Semestre */}
        <div className="px-0 py-3 flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2">
              ANO
            </label>
            <select
              value={ano}
              onChange={(e) => setAno(e.target.value)}
              className="border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-700 bg-white focus:outline-none focus:border-blue-500"
            >
              <option value="2026">2026</option>
              <option value="2025">2025</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2">
              SEMESTRE
            </label>
            <select
              value={semestre}
              onChange={(e) => setSemestre(e.target.value)}
              className="border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-700 bg-white focus:outline-none focus:border-blue-500"
            >
              <option value="2">2º Semestre</option>
              <option value="1">1º Semestre</option>
            </select>
          </div>
        </div>

        {/* Cards de Métricas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              MÉDIA GERAL
            </p>
            <span className="text-3xl font-semibold font-[DM_sans] text-[#16A34A]">
              {mediaGeral.toFixed(1)}
            </span>
          </div>

          <div className="bg-white rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              APROVAÇÕES
            </p>
            <span className="text-3xl font-semibold font-[DM_sans] text-blue-600">
              {totalAprovacoes}/{disciplinas.length}
            </span>
          </div>

          <div className="bg-white rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              FALTAS TOTAIS
            </p>
            <span className="text-3xl font-semibold font-[DM_sans] text-[#D97706]">
              {totalFaltas}
            </span>
          </div>

          <div className="bg-white rounded-xl p-5 border border-[#E2E8F0]">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              RISCO DE REPROVAÇÃO
            </p>
            <span className="text-3xl font-semibold font-[DM_sans] text-slate-600">
              {riscoReprovacao}
            </span>
          </div>
        </div>

        {/* Tabela do Boletim */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900">
              Boletim - {ano}/{semestre}
            </h2>
          </div>

          {/* Cabeçalho das Colunas */}
          <div className="grid grid-cols-12 px-6 py-3.5 bg-slate-50/80 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            <div className="col-span-6">DISCIPLINA</div>
            <div className="col-span-2 text-center">AVS</div>
            <div className="col-span-1 text-center">MÉDIA</div>
            <div className="col-span-1 text-center">FALTAS</div>
            <div className="col-span-2 text-right pr-2">SITUAÇÃO</div>
          </div>

          {/* Linhas de Disciplinas */}
          <div className="divide-y divide-slate-100">
            {disciplinasFiltradas.map((disciplina) => (
              <div
                key={disciplina.id}
                className="grid grid-cols-12 items-center px-6 py-4 hover:bg-slate-50/60 transition-colors"
              >
                <div className="col-span-6">
                  <h3 className="text-sm font-semibold text-slate-800">
                    {disciplina.nome}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {disciplina.turma} · {disciplina.cargaHoraria}
                  </p>
                </div>

                <div className="col-span-2 text-center text-xs text-slate-400">
                  {disciplina.avs ?? ''}
                </div>

                <div
                  className={`col-span-1 text-center text-sm font-semibold ${getMediaColor(
                    disciplina.media
                  )}`}
                >
                  {disciplina.media !== null ? disciplina.media.toFixed(1) : '—'}
                </div>

                <div className="col-span-1 text-center text-xs font-semibold">
                  <span
                    className={getFaltaNumeroColor(
                      disciplina.faltasAtuais,
                      disciplina.limiteFaltas
                    )}
                  >
                    {disciplina.faltasAtuais}
                  </span>
                  <span className="text-slate-400 font-normal">
                    /{disciplina.limiteFaltas}
                  </span>
                </div>

                <div className="col-span-2 flex justify-end">
                  <span
                    className={`text-[11px] font-semibold px-3 py-1 rounded-full ${getSituacaoBadge(
                      disciplina.situacao
                    )}`}
                  >
                    {disciplina.situacao}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Legenda Inferior */}
        <footer className="flex flex-wrap items-center gap-6 text-xs text-slate-500 px-1 mt-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Aprovado (≥ 7,0)</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
            <span>Exame Final (5,0–6,9)</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500"></span>
            <span>Reprovado (&lt; 5,0)</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">—</span>
            <span>Nota não lançada</span>
          </div>
        </footer>
      </main>
    </div>
  )
}