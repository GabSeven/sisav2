// import { useEffect, useState } from 'react'
import { TabelaChamada } from './components/TabelaChamada'

// type ApiStatus = 'indo' | 'ok' | 'erro'

// Dados tabela
const alunos: Aluno[] = [
  { id: 1, nome: 'Daniella Midori Hamada Yamasaki', ra: '139567', faltasAcumuladas: 3 },
  { id: 2, nome: 'João Vitor Bidoia Angelo', ra: '139617', faltasAcumuladas: 6 },
  { id: 3, nome: 'Gabriel Rodrigues Gomes', ra: '139159', faltasAcumuladas: 4 },
  { id: 4, nome: 'Gabrielly Bianka Ferreira da Mata', ra: '140600', faltasAcumuladas: 0 },
  { id: 5, nome: 'Fulaninho', ra: '140123', faltasAcumuladas: 9 },
  { id: 6, nome: 'Ciclaninho', ra: '140234', faltasAcumuladas: 2 },
  { id: 7, nome: 'Beltraninho', ra: '140345', faltasAcumuladas: 1 },
]

export default function App() {
  /* const [status, setStatus] = useState<ApiStatus>('indo')

  useEffect(() => {
    fetch('/health')
      .then((r) => setStatus(r.ok ? 'ok' : 'erro'))
      .catch(() => setStatus('erro'))
  }, [])
*/ 
  return (
/*     <div className="flex min-h-screen items-center justify-center bg-neutral-50 text-neutral-900">
      <main className="text-center">
        <h1 className="text-2xl font-semibold">SISAV 2</h1>
        <p className="mt-2 text-sm text-neutral-500">
          API: <span className={status === 'ok' ? 'text-green-600' : 'text-red-600'}>{status}</span>
        </p>
      </main>
    </div> */

    // Visualização da Tabela
    <div className="p-8 bg-gray-100 min-h-screen">
      <TabelaChamada turmaId={1} alunos={alunos} />
    </div>
  )
}