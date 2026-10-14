from datetime import date

from pydantic import BaseModel, Field, model_validator

MAX_AULAS_NO_DIA = 4


class RegistroFaltaItem(BaseModel):
    matricula_id: int
    faltas: int = Field(ge=0)


class RegistrarFaltasRequest(BaseModel):
    data: date
    aulas_no_dia: int = Field(ge=1, le=MAX_AULAS_NO_DIA)
    registros: list[RegistroFaltaItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_registros(self) -> "RegistrarFaltasRequest":
        ids = [r.matricula_id for r in self.registros]
        if len(ids) != len(set(ids)):
            raise ValueError("matricula_id repetido em registros.")
        if any(r.faltas > self.aulas_no_dia for r in self.registros):
            raise ValueError("faltas não pode ser maior que aulas_no_dia.")
        return self


class AlunoFrequenciaResponse(BaseModel):
    matricula_id: int
    nome_aluno: str
    total_faltas: int
    limite_faltas: int
    percentual_faltas: float
    excedeu_limite: bool


class FaltasTurmaResponse(BaseModel):
    turma_id: int
    data: date
    alunos: list[AlunoFrequenciaResponse]
