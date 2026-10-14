import { apiFetch } from '@/lib/api'

export type Perfil = 'aluno' | 'professor' | 'gestor'

export type Credenciais = {
  nomeDeUsuario: string
  senha: string
}

export type Sessao = {
  accessToken: string
  perfil: Perfil
}

type RespostaLogin = {
  access_token: string
  token_type: 'bearer'
  perfil: Perfil
}

export async function login({ nomeDeUsuario, senha }: Credenciais): Promise<Sessao> {
  const resposta = await apiFetch<RespostaLogin>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ nome_de_usuario: nomeDeUsuario, senha }),
  })

  return { accessToken: resposta.access_token, perfil: resposta.perfil }
}
