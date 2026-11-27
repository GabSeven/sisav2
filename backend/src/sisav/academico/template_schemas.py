from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from sisav.academico.calculo import de_centesimos


class SubcriterioPayload(BaseModel):
    ordem: int = Field(ge=1)
    nome: str = Field(min_length=1, max_length=100)
    peso: float = Field(gt=0)


class CriterioPayload(SubcriterioPayload):
    subcriterios: list[SubcriterioPayload] = Field(default_factory=list)


class SalvarTemplateRequest(BaseModel):
    criterios: list[CriterioPayload]

    @model_validator(mode="after")
    def validar_ordens(self) -> "SalvarTemplateRequest":
        ordens = [criterio.ordem for criterio in self.criterios]
        if len(ordens) != len(set(ordens)):
            raise ValueError("ordem repetida entre critérios.")
        for criterio in self.criterios:
            sub_ordens = [sub.ordem for sub in criterio.subcriterios]
            if len(sub_ordens) != len(set(sub_ordens)):
                raise ValueError(
                    f"ordem repetida entre subcritérios do critério {criterio.ordem}."
                )
        return self


class SubcriterioResponse(BaseModel):
    id: int
    ordem: int
    nome: str
    peso: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("peso")
    def serializar_peso(self, valor: int) -> float:
        return de_centesimos(valor)


class CriterioResponse(BaseModel):
    id: int
    ordem: int
    nome: str
    peso: int
    subcriterios: list[SubcriterioResponse]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("peso")
    def serializar_peso(self, valor: int) -> float:
        return de_centesimos(valor)


class TemplateResponse(BaseModel):
    disciplina_id: int
    disciplina: str
    criterios: list[CriterioResponse]
