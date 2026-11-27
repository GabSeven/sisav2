from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from sisav.academico.models import SituacaoAluno, TipoAvaliacao
from sisav.academico.services.calculo import de_centesimos


def _serializar_data_hora(valor: datetime | None) -> str | None:
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=UTC)
    return valor.isoformat().replace("+00:00", "Z")


class CriarAvaliacaoRequest(BaseModel):
    tipo: Literal["template", "exame"] = "template"


class EditarAvaliacaoRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    peso: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def exige_ao_menos_um_campo(self) -> "EditarAvaliacaoRequest":
        if not self.model_fields_set:
            raise ValueError("Informe nome ou peso.")
        return self


class AvaliacaoResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    tipo: TipoAvaliacao
    peso: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("peso")
    def serializar_peso(self, valor: int) -> float:
        return de_centesimos(valor)


class NotaItemRequest(BaseModel):
    matricula_id: int
    valor: float = Field(ge=0, le=10)


class LancarNotasRequest(BaseModel):
    avaliacao_id: int
    registros: list[NotaItemRequest] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_registros(self) -> "LancarNotasRequest":
        ids = [item.matricula_id for item in self.registros]
        if len(ids) != len(set(ids)):
            raise ValueError("matricula_id repetido em registros.")
        return self


class NotaResponse(BaseModel):
    matricula_id: int
    valor: int

    @field_serializer("valor")
    def serializar_valor(self, valor: int) -> float:
        return de_centesimos(valor)


class NotasLancadasResponse(BaseModel):
    avaliacao_id: int
    registros: list[NotaResponse]


class NotaAvaliacaoResponse(BaseModel):
    codigo: str
    nome: str
    tipo: TipoAvaliacao
    peso: int
    valor: int | None

    @field_serializer("peso", "valor")
    def serializar_centesimos(self, valor: int | None) -> float | None:
        return None if valor is None else de_centesimos(valor)


class BoletimTurmaResponse(BaseModel):
    turma_id: int
    codigo_turma: str
    disciplina: str
    ano_letivo: int
    semestre: str
    avaliacoes: list[NotaAvaliacaoResponse]
    media_pre_exame: int | None
    nota_exame: int | None
    media_final: int | None
    total_faltas: int
    limite_faltas: int
    situacao: SituacaoAluno | None

    @field_serializer("media_pre_exame", "nota_exame", "media_final")
    def serializar_medias(self, valor: int | None) -> float | None:
        return None if valor is None else de_centesimos(valor)


class BoletimResponse(BaseModel):
    ano: int
    semestre: int
    turmas: list[BoletimTurmaResponse]


class ConsolidacaoResponse(BaseModel):
    id: int
    matricula_id: int
    media_pre_exame: int
    nota_exame: int | None
    media_final: int
    total_faltas: int
    limite_faltas: int
    situacao: SituacaoAluno
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("media_pre_exame", "nota_exame", "media_final")
    def serializar_medias(self, valor: int | None) -> float | None:
        return None if valor is None else de_centesimos(valor)

    @field_serializer("criado_em")
    def serializar_criado_em(self, valor: datetime) -> str:
        return _serializar_data_hora(valor)


class ConsolidacaoTurmaResponse(BaseModel):
    turma_id: int
    fechada_em: datetime | None
    consolidacoes: list[ConsolidacaoResponse]

    @field_serializer("fechada_em")
    def serializar_fechada_em(self, valor: datetime | None) -> str | None:
        return _serializar_data_hora(valor)
