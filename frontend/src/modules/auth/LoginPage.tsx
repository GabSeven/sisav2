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
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4 py-10 text-neutral-900">
      <main className="w-full max-w-sm sm:rounded-2xl sm:border sm:border-neutral-200 sm:bg-white sm:p-8 sm:shadow-sm">
        <header className="mb-8 flex flex-col items-center text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-neutral-900 text-white">
            <GraduationCap className="h-6 w-6" aria-hidden="true" />
          </span>
          <h1 className="mt-4 text-2xl font-semibold">SISAV 2</h1>
          <p className="mt-1 text-sm text-neutral-500">Serviços acadêmicos da UEM</p>
        </header>

        <form className="space-y-4" onSubmit={handleSubmit} noValidate>
          <div className="space-y-2">
            <Label htmlFor="nome-de-usuario">Usuário</Label>
            <Input
              id="nome-de-usuario"
              name="nomeDeUsuario"
              autoComplete="username"
              autoCapitalize="none"
              autoCorrect="off"
              placeholder="nome.de.usuario"
              value={nomeDeUsuario}
              onChange={(event) => setNomeDeUsuario(event.target.value)}
              aria-invalid={erro !== null}
              disabled={enviando}
            />
          </div>

          <div className="space-y-2">
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
                className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-neutral-400 hover:text-neutral-600"
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

          <Button type="submit" size="lg" className="w-full" disabled={enviando}>
            {enviando ? 'Entrando…' : 'Entrar'}
          </Button>
        </form>
      </main>
    </div>
  )
}
