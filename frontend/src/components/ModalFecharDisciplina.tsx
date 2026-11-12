import { useState } from 'react'

interface ModalFecharDisciplinaProps {
  isOpen: boolean
  nomeDisciplina?: string
  totalAlunos?: number
  onClose: () => void
  onConfirmarFechamento: () => void
  isLoading?: boolean
}

export function ModalFecharDisciplina({
  isOpen,
  nomeDisciplina = 'Construção de Software 1',
  totalAlunos = 32,
  onClose,
  onConfirmarFechamento,
  isLoading = false,
}: ModalFecharDisciplinaProps) {
  // Estado para a confirmação por checkbox
  const [cienteRegras, setCienteRegras] = useState(false)

  if (!isOpen) return null

  // Libera a confirmação apenas se o checkbox estiver marcado
  const podeConfirmar = cienteRegras

  const handleConfirmar = () => {
    if (podeConfirmar) {
      onConfirmarFechamento()
    }
  }

  const handleClose = () => {
    setCienteRegras(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-100 font-sans">
        
        {/* Cabeçalho do Modal */}
        <div className="flex items-start gap-4 mb-4">
          <div className="w-10 h-10 rounded-full bg-red-100 text-red-600 flex items-center justify-center shrink-0">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Fechar Disciplina</h2>
            <p className="text-xs text-slate-500 mt-0.5">Esta ação é irreversível e bloqueará possíveis alterações.</p>
          </div>
        </div>

        {/* Resumo dos Dados */}
        <div className="bg-slate-50 rounded-xl p-4 mb-5 border border-slate-100 text-xs text-slate-600 space-y-1.5">
          <p><strong className="text-slate-800">Disciplina:</strong> {nomeDisciplina}</p>
          <p><strong className="text-slate-800">Total de Alunos:</strong> {totalAlunos} alunos</p>
          <p className="text-red-600 font-medium pt-1">
            Após o fechamento, notas e faltas não poderão mais ser lançadas ou editadas.
          </p>
        </div>

        {/* Passo de Confirmação (Apenas Checkbox) */}
        <div className="mb-6">
          <label className="flex items-start gap-3 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={cienteRegras}
              onChange={(e) => setCienteRegras(e.target.checked)}
              className="mt-0.5 w-4 h-4 text-red-600 rounded border-slate-300 focus:ring-red-500 cursor-pointer"
            />
            <span className="text-xs text-slate-700 leading-relaxed">
              Estou ciente de que revisei todas as notas e faltas da turma e confirmo o encerramento da disciplina.
            </span>
          </label>
        </div>

        {/* Botões de Ação */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={handleClose}
            disabled={isLoading}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirmar}
            disabled={!podeConfirmar || isLoading}
            className="bg-red-600 hover:bg-red-700 text-white font-medium text-xs px-5 py-2.5 rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? 'Encerrando...' : 'Confirmar Encerramento'}
          </button>
        </div>

      </div>
    </div>
  )
}