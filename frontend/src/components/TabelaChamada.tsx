import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { salvarChamada } from '@/services/frequenciaService'
import { Header } from  './Header'

export interface Aluno {
  id: number
  nome: string
  ra: string
  faltasAcumuladas: number
}

interface TabelaChamadaProps {
  turmaId?: number
  nomeTurma?: string
  ano?: string
  alunos: Aluno[]
}

export function TabelaChamada({
  turmaId = 1,
  nomeTurma = 'Banco de Dados',
  ano = '4º Ano',
  alunos,
}: TabelaChamadaProps) {
  const queryClient = useQueryClient()

  // Data atual no formato YYYY-MM-DD
  const [dataAula, setDataAula] = useState(new Date().toISOString().split('T')[0])
  const [turmaSelecionada, setTurmaSelecionada] = useState(String(turmaId))

  // Estado das faltas (true = aluno faltou / checkbox marcado)
  const [faltas, setFaltas] = useState<Record<number, boolean>>(() =>
    alunos.reduce((acc, aluno) => ({ ...acc, [aluno.id]: false }), {})
  )

  // Mutação do TanStack Query
  const mutation = useMutation({
    mutationFn: salvarChamada,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['turmas', turmaSelecionada] })
      alert('Faltas salvas com sucesso!')
    },
    onError: () => {
      alert('Erro ao salvar as faltas. Tente novamente.')
    },
  })

  // Alterna a falta de um aluno individual
  const toggleFalta = (alunoId: number) => {
    setFaltas((prev) => ({
      ...prev,
      [alunoId]: !prev[alunoId],
    }))
  }

  // Alterna a marcação de todos os alunos
  const todosMarcados = alunos.length > 0 && alunos.every((aluno) => faltas[aluno.id])

  const toggleMarcarTodos = () => {
    const novoEstado = !todosMarcados
    const atualizado = alunos.reduce(
      (acc, aluno) => ({ ...acc, [aluno.id]: novoEstado }),
      {}
    )
    setFaltas(atualizado)
  }

  // Envio dos dados formatados para a API
  const handleSalvar = () => {
    const registros = alunos.map((aluno) => ({
      alunoId: aluno.id,
      presente: !faltas[aluno.id], // Se a caixa de falta está marcada, presente é false
    }))

    mutation.mutate({
      turmaId: Number(turmaSelecionada),
      data: dataAula,
      registros,
    })
  }

  // Define a cor do contador e da barra lateral de faltas acumuladas
  const getFaltaEstilo = (count: number) => {
    if (count >= 8) return { text: 'text-red-600', bar: 'bg-amber-700', percent: '80%' }
    if (count >= 5) return { text: 'text-amber-600', bar: 'bg-amber-600', percent: '60%' }
    return { text: 'text-emerald-600', bar: 'bg-emerald-500', percent: `${Math.min(count * 15 + 10, 50)}%` }
  }

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-800">
      <Header
      titulo="Lançar Faltas"
      subtitulo="Registro de frequência por data de aula"
      />
      <main className="p-6">

      {/* Card de Filtros e Ação */}
      <div className="bg-white rounded-xl p-6 border border-slate-100 shadow-sm mb-4">
        <div className="flex items-end justify-between gap-4">
          <div className="flex items-center gap-6">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                TURMA
              </label>
              <select
                value={turmaSelecionada}
                onChange={(e) => setTurmaSelecionada(e.target.value)}
                className="w-64 border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-700 bg-white focus:outline-none focus:border-blue-500"
              >
                <option value="1">Construção de Software 1</option>
                <option value="2">Banco de Dados</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                DATA DA AULA
              </label>
              <input
                type="date"
                value={dataAula}
                onChange={(e) => setDataAula(e.target.value)}
                className="border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm text-slate-700 bg-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <button
            type="button"
            onClick={handleSalvar}
            disabled={mutation.isPending}
            className="bg-[#1D4ED8] hover:bg-blue-800 text-white font-medium text-sm px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Salvando...' : 'Salvar Faltas'}
          </button>
        </div>
      </div>

    {/* Subtítulo da Lista */}
    <p className="text-xs font-semibold text-slate-500 mb-3 px-1">
    <span className="font-semibold text-slate-900">{nomeTurma}</span> · {ano} · {alunos.length} alunos
    </p>

      {/* Card Principal da Lista */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">Lista de Chamada</h2>
          <button
            type="button"
            onClick={toggleMarcarTodos}
            className="text-xs font-semibold text-[#1D4ED8] hover:text-blue-800 transition-colors"
          >
            {todosMarcados ? 'Desmarcar todos' : 'Marcar todos como falta'}
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {alunos.map((aluno) => {
            const estaComFalta = faltas[aluno.id] ?? false
            const estiloFalta = getFaltaEstilo(aluno.faltasAcumuladas)

            return (
              <div
                key={aluno.id}
                onClick={() => toggleFalta(aluno.id)}
                className="flex items-center justify-between px-5 py-4 hover:bg-slate-50/70 transition-colors cursor-pointer select-none"
              >
                <div className="flex items-center gap-4">
                  <input
                    type="checkbox"
                    checked={estaComFalta}
                    onChange={() => {}} // Tratado no clique do container
                    className="w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                  <div>
                    <h3 className="text-sm font-semibold text-slate-800">{aluno.nome}</h3>
                    <p className="text-xs text-slate-400 font-medium mt-0.5">RA: {aluno.ra}</p>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1.5 w-24">
                  <span className={`text-xs font-semibold ${estiloFalta.text}`}>
                    {aluno.faltasAcumuladas} faltas
                  </span>
                  <div className="w-12 h-1 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${estiloFalta.bar} rounded-full`}
                      style={{ width: estiloFalta.percent }}
                    ></div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </main>
    </div>
  )
}