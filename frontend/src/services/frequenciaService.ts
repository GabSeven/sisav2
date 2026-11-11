import { api } from '@/lib/api'

export interface RegistroPresenca {
  alunoId: number
  presente: boolean
}

export interface PayloadChamada {
  turmaId: number
  data: string
  registros: RegistroPresenca[]
}

export async function salvarChamada({ turmaId, data, registros }: PayloadChamada) {
  const response = await api.put(`/avaliacao-frequencia/turmas/${turmaId}/faltas`, {
    data,
    registros,
  })
  return response.data
}