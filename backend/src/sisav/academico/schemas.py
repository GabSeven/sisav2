from datetime import time

from pydantic import BaseModel, ConfigDict, field_serializer


class AulaHorarioResponse(BaseModel):
    id_turma: int
    codigo_turma: str
    nome_disciplina: str
    sala: str
    dia_semana: str
    horario_inicio: time
    horario_fim: time

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("horario_inicio", "horario_fim")
    def serializar_horario(self, valor: time) -> str:
        return valor.strftime("%H:%M")


class GradeHorariaResponse(BaseModel):
    semestre: str
    aulas: list[AulaHorarioResponse]