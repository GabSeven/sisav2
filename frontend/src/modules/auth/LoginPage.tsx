import { Eye, EyeOff, GraduationCap } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export type Credenciais = {
  nomeDeUsuario: string
  senha: string
}

type LoginPageProps = {
  onSubmit?: (credenciais: Credenciais) => Promise<void> | void
}

export function LoginPage({ onSubmit }: LoginPageProps) {
  const [nomeDeUsuario, setNomeDeUsuario] = useState('')
  const [senha, setSenha] = useState('')
  const [senhaVisivel, setSenhaVisivel] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErro(null)

    if (nomeDeUsuario.trim() === '' || senha === '') {
      setErro('Informe o usuário e a senha.')
      return
    }

    if (!onSubmit) return

    try {
      setEnviando(true)
      await onSubmit({ nomeDeUsuario: nomeDeUsuario.trim(), senha })
    } catch {
      setErro('Não foi possível entrar. Verifique o usuário e a senha.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-100">
      <aside className="hidden w-1/2 flex-col justify-between bg-slate-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-700">
            <GraduationCap className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <p className="font-display text-lg font-bold">SISAV 2</p>
            <p className="text-[11px] text-slate-500">Universidade Estadual de Maringá</p>
          </div>
        </div>

        <div>
          <h1 className="font-display text-4xl font-bold leading-tight">
            SECRETARIA ACADÊMICA
            <br />
            VIRTUAL - UEM
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400">
            O sistema Secretaria Acadêmica Virtual (SAV), da Diretoria de Assuntos Acadêmicos
            (DAA), é o portal onde o acadêmico pode consultar as disciplinas cursadas e os
            conceitos finais obtidos, obter declarações de matrícula e outros documentos.
          </p>
        </div>

        <p className="text-[11px] text-slate-700">
          © 2026 UEM · Departamento de Informática · SISAV 2
        </p>
      </aside>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="font-display text-2xl font-bold text-slate-900">Entrar</h2>
            <p className="mt-1 text-sm text-slate-500">
              Acesse o portal com suas credenciais UEM.
            </p>

            <form className="mt-6 space-y-4" onSubmit={handleSubmit} noValidate>
              <div className="space-y-1.5">
                <Label htmlFor="nome-de-usuario">Usuário</Label>
                <Input
                  id="nome-de-usuario"
                  name="nomeDeUsuario"
                  autoComplete="username"
                  autoCapitalize="none"
                  autoCorrect="off"
                  placeholder="seu.usuario"
                  value={nomeDeUsuario}
                  onChange={(event) => setNomeDeUsuario(event.target.value)}
                  aria-invalid={erro !== null}
                  disabled={enviando}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="senha">Senha</Label>
                <div className="relative">
                  <Input
                    id="senha"
                    name="senha"
                    type={senhaVisivel ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    className="pr-10"
                    value={senha}
                    onChange={(event) => setSenha(event.target.value)}
                    aria-invalid={erro !== null}
                    disabled={enviando}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-slate-400 hover:text-slate-600"
                    onClick={() => setSenhaVisivel((visivel) => !visivel)}
                    aria-label={senhaVisivel ? 'Ocultar senha' : 'Mostrar senha'}
                    tabIndex={-1}
                  >
                    {senhaVisivel ? (
                      <EyeOff className="h-4 w-4" aria-hidden="true" />
                    ) : (
                      <Eye className="h-4 w-4" aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>

              {erro !== null && (
                <p role="alert" className="text-sm text-red-600">
                  {erro}
                </p>
              )}

              <div className="flex justify-end">
                <button
                  type="button"
                  className="text-xs font-semibold text-blue-700 hover:underline"
                >
                  Esqueceu a senha?
                </button>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={enviando}
              >
                {enviando ? 'Entrando…' : 'Entrar no Portal'}
              </Button>
            </form>
          </div>

          <p className="mt-4 text-center text-xs text-slate-400">
            Problemas com o acesso? Contate a secretaria acadêmica.
          </p>
        </div>
      </div>
    </div>
  )
}
