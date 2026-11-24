from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.auth.schemas import LoginRequest, LoginResponse
from sisav.auth.security import verificar_senha
from sisav.auth.tokens import gerar_token_acesso
from sisav.core.db import get_db
from sisav.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


async def _autenticar(
    nome_de_usuario: str,
    senha: str,
    db: AsyncSession,
) -> Usuario:
    usuario = await db.scalar(
        select(Usuario).where(Usuario.nome_de_usuario == nome_de_usuario)
    )
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )
    return usuario


def _resposta_login(usuario: Usuario) -> LoginResponse:
    return LoginResponse(
        access_token=gerar_token_acesso(usuario.id, usuario.perfil),
        perfil=usuario.perfil,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    dados: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    usuario = await _autenticar(dados.nome_de_usuario, dados.senha, db)
    return _resposta_login(usuario)


@router.post("/token", response_model=LoginResponse, include_in_schema=False)
async def token(
    dados: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    usuario = await _autenticar(dados.username.strip().lower(), dados.password, db)
    return _resposta_login(usuario)