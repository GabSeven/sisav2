import { GraduationCap, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router'

import { Button } from '@/components/ui/button'
import { limparSessao } from '@/modules/auth/session'

type PainelProps = {
  titulo: string
  descricao: string
}

export function Painel({ titulo, descricao }: PainelProps) {
  const navegar = useNavigate()

  function sair() {
    limparSessao()
    navegar('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-blue-700 text-white">
            <GraduationCap className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="font-display font-bold text-slate-900">SISAV 2</span>
        </div>
        <Button variant="outline" onClick={sair}>
          <LogOut className="h-4 w-4" aria-hidden="true" />
          Sair
        </Button>
      </header>

      <main className="mx-auto max-w-3xl p-8">
        <h1 className="font-display text-2xl font-bold text-slate-900">{titulo}</h1>
        <p className="mt-2 text-sm text-slate-500">{descricao}</p>
      </main>
    </div>
  )
}
