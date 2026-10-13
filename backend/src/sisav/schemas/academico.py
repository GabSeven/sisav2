from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID

class AulaHorarioResponse(BaseModel):
    id_turma: UUID
    nome_disciplina: str
    dia_semana: str
    horario_inicio: str
    horario_fim: str

    model_config = ConfigDict(from_attributes=True)

class GradeHorariaResponse(BaseModel):
    semestre: str
    aulas: List[AulaHorarioResponse]