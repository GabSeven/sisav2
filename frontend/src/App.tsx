import { useState } from 'react'
import { TabelaChamada } from './components/TabelaChamada'
import { FecharDisciplina } from './components/FecharDisciplina'
import type { Aluno } from './components/TabelaChamada'

const alunosTeste: Aluno[] = [
  { id: 1, nome: 'Daniella Midori Hamada Yamasaki', ra: '139567', faltasAcumuladas: 3 },
  { id: 2, nome: 'João Vitor Bidoia Angelo', ra: '139617', faltasAcumuladas: 6 },
  { id: 3, nome: 'Gabriel Rodrigues Gomes', ra: '139159', faltasAcumuladas: 4 },
  { id: 4, nome: 'Gabrielly Bianka Ferreira da Mata', ra: '140600', faltasAcumuladas: 0 },
  { id: 5, nome: 'Fulaninho', ra: '140123', faltasAcumuladas: 9 },
  { id: 6, nome: 'Ciclaninho', ra: '140234', faltasAcumuladas: 2 },
  { id: 7, nome: 'Beltraninho', ra: '140345', faltasAcumuladas: 1 },
]

export default function App() {
  const [telaAtiva, setTelaAtiva] = useState<'chamada' | 'fechar'>('fechar')

  return (
    <div>
      {/* Barra superior para alternar entre os componentes durante os testes */}
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
        </div>
      </div>

      {/* Renderização do componente selecionado */}
      {telaAtiva === 'chamada' ? (
        <TabelaChamada alunos={alunosTeste} />
      ) : (
        <FecharDisciplina />
      )}
    </div>
  )
}