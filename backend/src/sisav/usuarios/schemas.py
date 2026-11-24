import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PerfilResponse(BaseModel):
    nome: str
    matricula: str
    curso: str | None
    email_institucional: str
    foto_url: str | None
    telefone: str | None
    email_alternativo: str | None

class ContatoUpdateRequest(BaseModel):
    telefone: str | None = Field(default=None, max_length=20)
    email_alternativo: str | None = Field(default=None, max_length=150)
    confirmado: Literal[True]

    @field_validator("telefone", mode="before")
    @classmethod
    def normalizar_telefone(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip() or None
        return valor

    @field_validator("email_alternativo", mode="before")
    @classmethod
    def normalizar_email(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip().lower() or None
        return valor

    @field_validator("email_alternativo")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        if valor is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ValueError("E-mail alternativo inválido.")
        return valor
