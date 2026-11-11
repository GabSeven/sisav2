import axios from 'axios'

const API_BASE = '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, mensagem: string) {
    super(mensagem)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiFetch<T>(caminho: string, init?: RequestInit): Promise<T> {
  let resposta: Response

  try {
    resposta = await fetch(`${API_BASE}${caminho}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError(0, 'Não foi possível conectar ao servidor.')
  }

  if (!resposta.ok) {
    throw new ApiError(resposta.status, await lerDetalhe(resposta))
  }

  if (resposta.status === 204) {
    return undefined as T
  }

  return (await resposta.json()) as T
}

async function lerDetalhe(resposta: Response): Promise<string> {
  try {
    const corpo = (await resposta.json()) as { detail?: unknown }
    if (typeof corpo.detail === 'string') {
      return corpo.detail
    }
  } catch {
    // corpo de erro não é JSON
  }
  return 'Ocorreu um erro inesperado. Tente novamente.'
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para injetar o token JWT automaticamente em todas as requisições
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('@SISAV:token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})