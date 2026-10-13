from pydantic import BaseModel, ConfigDict


class AulaHorarioResponse(BaseModel):
    id_turma: int
    nome_disciplina: str
    dia_semana: str
    horario_inicio: str
    horario_fim: str

    model_config = ConfigDict(from_attributes=True)


class GradeHorariaResponse(BaseModel):
    semestre: str
    aulas: list[AulaHorarioResponse]