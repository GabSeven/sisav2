from typing import Literal

from pydantic import BaseModel, Field, field_validator

from sisav.usuarios.models import Perfil


class LoginRequest(BaseModel):
    nome_de_usuario: str = Field(min_length=1, max_length=64)
    senha: str = Field(min_length=1)

    @field_validator("nome_de_usuario", mode="before")
    @classmethod
    def normalizar_usuario(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor

    @field_validator("nome_de_usuario")
    @classmethod
    def validar_usuario(cls, valor: str) -> str:
        if any(caractere.isspace() for caractere in valor):
            raise ValueError("O nome de usuário não pode conter espaços.")
        return valor

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes.")
        return valor

class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    perfil: Perfil

class RecuperarSenhaRequest(BaseModel):
    identificador: str = Field(min_length=5, max_length=150)

    @field_validator("identificador", mode="before")
    @classmethod
    def normalizar_identificador(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor

    @field_validator("identificador")
    @classmethod
    def validar_identificador(cls, valor: str) -> str:
        if any(caractere.isspace() for caractere in valor):
            raise ValueError("O identificador não pode conter espaços.")
        return valor


class RedefinirSenhaRequest(BaseModel):
    token: str = Field(min_length=1)
    nova_senha: str = Field(min_length=8)

    @field_validator("token")
    @classmethod
    def validar_token(cls, valor: str) -> str:
        if any(caractere.isspace() for caractere in valor):
            raise ValueError("O token não pode conter espaços.")
        return valor

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes.")
        return valor


class MensagemResponse(BaseModel):
    mensagem: str