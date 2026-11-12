import { useState } from 'react'
import { TabelaChamada } from './components/TabelaChamada'
import type { Aluno } from './components/TabelaChamada'
import { FecharDisciplina } from './components/FecharDisciplina'
import type { TurmaConsolidacao } from './components/FecharDisciplina'
import { PainelNotasFaltasAluno } from './components/PainelNotasFaltasAluno'
import type { DisciplinaBoletim } from './components/PainelNotasFaltasAluno'

const alunosTeste: Aluno[] = [
  { id: 1, nome: 'Daniella Midori Hamada Yamasaki', ra: '139567', faltasAcumuladas: 3 },
  { id: 2, nome: 'João Vitor Bidoia Angelo', ra: '139617', faltasAcumuladas: 6 },
  { id: 3, nome: 'Gabriel Rodrigues Gomes', ra: '139159', faltasAcumuladas: 4 },
  { id: 4, nome: 'Gabrielly Bianka Ferreira da Mata', ra: '140600', faltasAcumuladas: 0 },
  { id: 5, nome: 'Fulaninho', ra: '140123', faltasAcumuladas: 9 },
  { id: 6, nome: 'Ciclaninho', ra: '140234', faltasAcumuladas: 2 },
  { id: 7, nome: 'Beltraninho', ra: '140345', faltasAcumuladas: 1 },
]

const turmasConsolidacaoTeste: TurmaConsolidacao[] = [
  {
    id: 'csof-t01',
    codigo: 'CSOF401-T01',
    nome: 'Construção de Software',
    alunos: [
      { id: 1, nome: 'Daniella Midori Hamada Yamasaki', ra: '139567', av1: '10.0', av2: '10.0', mediaFinal: '10.0', faltas: '3/17', situacao: 'Aprovado' },
      { id: 2, nome: 'João Vitor Bidoia Angelo', ra: '139617', av1: '10.0', av2: '10.0', mediaFinal: '10.0', faltas: '6/17', situacao: 'Aprovado' },
      { id: 3, nome: 'Gabriel Rodrigues Gomes', ra: '139159', av1: '10.0', av2: '10.0', mediaFinal: '10.0', faltas: '4/17', situacao: 'Aprovado' },
      { id: 4, nome: 'Gabrielly Bianka Ferreira da Mata', ra: '140600', av1: '10.0', av2: '10.0', mediaFinal: '10.0', faltas: '0/17', situacao: 'Aprovado' },
    ],
  },
  {
    id: 'dino-t01',
    codigo: 'DINO512-T01',
    nome: 'Banco de Dados',
    alunos: [
      { id: 5, nome: 'Fulaninho', ra: '140123', av1: '5.5', av2: '!', mediaFinal: '5.5', faltas: '9/17', situacao: 'Exame Final' },
      { id: 6, nome: 'Ciclaninho', ra: '140234', av1: '6.0', av2: '7.5', mediaFinal: '6.8', faltas: '2/17', situacao: 'Exame Final' },
      { id: 7, nome: 'Zezinho', ra: '140345', av1: '6.0', av2: '7.5', mediaFinal: '6.8', faltas: '20/17', situacao: 'Rep. por Falta' },
    ],
  },
]

const disciplinasTeste: DisciplinaBoletim[] = [
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

export default function App() {
  const [telaAtiva, setTelaAtiva] = useState<'chamada' | 'fechar' | 'boletim'>('fechar')

  return (
    <div>
      {/* Barra superior para alternar entre os componentes */}
      <div className="bg-slate-900 text-white px-6 py-2.5 flex items-center justify-between text-xs font-sans">
        <span className="font-semibold text-slate-400">Preview de Componentes</span>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTelaAtiva('chamada')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              telaAtiva === 'chamada'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Lançar Faltas
          </button>

          <button
            type="button"
            onClick={() => setTelaAtiva('fechar')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              telaAtiva === 'fechar'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Fechar Disciplina
          </button>

          <button
            type="button"
            onClick={() => setTelaAtiva('boletim')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              telaAtiva === 'boletim'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Notas e Faltas
          </button>
        </div>
      </div>

      {/* Renderização condicional */}
      {telaAtiva === 'chamada' && <TabelaChamada alunos={alunosTeste} />}
      {telaAtiva === 'fechar' && <FecharDisciplina turmas={turmasConsolidacaoTeste} />}
      {telaAtiva === 'boletim' && <PainelNotasFaltasAluno disciplinas={disciplinasTeste} />}
    </div>
  )
}