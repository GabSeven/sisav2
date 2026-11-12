import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { salvarChamada } from '@/services/frequenciaService'
import { Header } from './Header'

export interface Aluno {
  id: number
  nome: string
  ra: string
  faltasAcumuladas: number
}

export interface TurmaChamada {
  id: number
  nome: string
  ano: string
  alunos: Aluno[]
}

interface TabelaChamadaProps {
  turmas: TurmaChamada[]
}

export function TabelaChamada({ turmas }: TabelaChamadaProps) {
  const queryClient = useQueryClient()

  const [turmaSelecionada, setTurmaSelecionada] = useState(String(turmas[0]?.id ?? ''))
  const [dataAula, setDataAula] = useState(new Date().toISOString().split('T')[0])
  const [busca, setBusca] = useState('')

  // Armazena as faltas por chave "${turmaId}-${dataAula}" para não misturar datas/turmas
  const [faltasPorAula, setFaltasPorAula] = useState<Record<string, Record<number, boolean>>>({})

  // Turma ativa e alunos derivados diretamente da prop
  const turmaAtual = turmas.find((t) => String(t.id) === turmaSelecionada) ?? turmas[0]
  const alunosDaTurma = turmaAtual?.alunos ?? []

  // Filtro de busca por nome ou RA
  const alunosFiltrados = alunosDaTurma.filter(
    (aluno) =>
      aluno.nome.toLowerCase().includes(busca.toLowerCase()) ||
      aluno.ra.includes(busca.trim())
  )

  const chaveAulaAtual = `${turmaAtual?.id}-${dataAula}`
  const faltasAtuais = faltasPorAula[chaveAulaAtual] ?? {}

  // Mutação do TanStack Query
  const mutation = useMutation({
    mutationFn: salvarChamada,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['turmas', String(turmaAtual?.id)] })
      alert('Faltas salvas com sucesso!')
    },
    onError: () => {
      alert('Erro ao salvar as faltas. Tente novamente.')
    },
  })

  // Alterna a falta de um aluno individual na data/turma ativa
  const toggleFalta = (alunoId: number) => {
    setFaltasPorAula((prev) => ({
      ...prev,
      [chaveAulaAtual]: {
        ...(prev[chaveAulaAtual] ?? {}),
        [alunoId]: !prev[chaveAulaAtual]?.[alunoId],
      },
    }))
  }

  // Alterna a marcação dos alunos visíveis na lista
  const todosMarcados =
    alunosFiltrados.length > 0 && alunosFiltrados.every((aluno) => Boolean(faltasAtuais[aluno.id]))

  const toggleMarcarTodos = () => {
    const novoEstado = !todosMarcados
    const atualizado = { ...faltasAtuais }

    alunosFiltrados.forEach((aluno) => {
      atualizado[aluno.id] = novoEstado
    })

    setFaltasPorAula((prev) => ({
      ...prev,
      [chaveAulaAtual]: atualizado,
    }))
  }

  // Envio dos dados formatados para a API (considerando todos os alunos da turma)
  const handleSalvar = () => {
    if (!turmaAtual) return

    const registros = alunosDaTurma.map((aluno) => ({
      alunoId: aluno.id,
      presente: !faltasAtuais[aluno.id], // Se a caixa de falta está marcada, presente é false
    }))

    mutation.mutate({
      turmaId: turmaAtual.id,
      data: dataAula,
      registros,
    })
  }

  // Define a cor do contador e da barra lateral de faltas acumuladas
  const getFaltaEstilo = (count: number) => {
    if (count >= 8) return { text: 'text-red-600', bar: 'bg-amber-700', percent: '80%' }
    if (count >= 5) return { text: 'text-amber-600', bar: 'bg-amber-600', percent: '60%' }
    return {
      text: 'text-emerald-600',
      bar: 'bg-emerald-500',
      percent: `${Math.min(count * 15 + 10, 50)}%`,
    }
  }

  if (!turmaAtual) {
    return (
      <div className="min-h-screen bg-[#F1F5F9] text-slate-800">
        <Header
          titulo="Lançar Faltas"
          subtitulo="Registro de frequência por data de aula"
        />
        <main className="p-6 text-sm text-slate-500">Nenhuma turma disponível.</main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-800">
      <Header
        titulo="Lançar Faltas"
        subtitulo="Registro de frequência por data de aula"
        busca={busca}
        onBuscaChange={setBusca}
      />

      <main className="px-6 pb-6 pt-4">
        {/* Card de Filtros e Ação */}
        <div className="bg-white rounded-xl p-6 border border-slate-100 shadow-sm mb-4">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div className="flex flex-wrap items-center gap-6">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  TURMA
                </label>
                <select
                  value={String(turmaAtual.id)}
                  onChange={(e) => setTurmaSelecionada(e.target.value)}
                  className="w-64 border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm font-medium text-slate-700 bg-white focus:outline-none focus:border-blue-500"
                >
                  {turmas.map((turma) => (
                    <option key={turma.id} value={String(turma.id)}>
                      {turma.nome}
                    </option>
                  ))}
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
          <span className="font-semibold text-slate-900">{turmaAtual.nome}</span> · {turmaAtual.ano} · {alunosDaTurma.length} alunos
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
            {alunosFiltrados.length === 0 ? (
              <div className="px-5 py-8 text-center text-sm text-slate-400">
                Nenhum aluno encontrado para os filtros selecionados.
              </div>
            ) : (
              alunosFiltrados.map((aluno) => {
                const estaComFalta = Boolean(faltasAtuais[aluno.id])
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
              })
            )}
          </div>
        </div>
      </main>
    </div>
  )
}