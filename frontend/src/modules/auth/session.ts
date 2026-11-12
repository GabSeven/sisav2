import type { Perfil, Sessao } from './api'

const CHAVE_SESSAO = 'sisav.sessao'

export const rotaInicialPorPerfil: Record<Perfil, string> = {
  aluno: '/aluno',
  professor: '/professor',
  gestor: '/gestor',
}

export function salvarSessao(sessao: Sessao): void {
  localStorage.setItem(CHAVE_SESSAO, JSON.stringify(sessao))
}

export function lerSessao(): Sessao | null {
  const bruto = localStorage.getItem(CHAVE_SESSAO)
  if (bruto === null) {
    return null
  }

  try {
    return JSON.parse(bruto) as Sessao
  } catch {
    localStorage.removeItem(CHAVE_SESSAO)
    return null
  }
}

export function limparSessao(): void {
  localStorage.removeItem(CHAVE_SESSAO)
}
