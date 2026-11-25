from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.auth.envio import EnviadorLink, get_enviador_link
from sisav.auth.models import TokenRecuperacao
from sisav.auth.schemas import (
    LoginRequest,
    LoginResponse,
    MensagemResponse,
    RecuperarSenhaRequest,
    RedefinirSenhaRequest,
)
from sisav.auth.security import gerar_hash, verificar_senha
from sisav.auth.tokens import (
    TOKEN_TIPO_RECUPERACAO,
    TokenInvalido,
    decodificar_token,
    gerar_token_acesso,
    gerar_token_recuperacao,
)
from sisav.core.config import get_settings
from sisav.core.db import get_db
from sisav.usuarios.models import Usuario
from sisav.usuarios.service import email_institucional

MENSAGEM_RECUPERACAO = (
    "Se o e-mail estiver cadastrado, enviaremos um link para redefinir a senha."
)
MENSAGEM_REDEFINICAO = "Senha redefinida com sucesso."

router = APIRouter(prefix="/auth", tags=["Autenticação"])
settings = get_settings()


def _erro_link_invalido() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Link inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


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


@router.post(
    "/recuperar-senha",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=MensagemResponse,
)
async def recuperar_senha(
    dados: RecuperarSenhaRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    enviar_link: Annotated[EnviadorLink, Depends(get_enviador_link)],
) -> MensagemResponse:
    ident = dados.identificador
    condicoes = [Usuario.email_alternativo == ident]

    sufixo = f"@{settings.dominio_institucional}"
    if ident.endswith(sufixo):
        condicoes.append(Usuario.nome_de_usuario == ident.removesuffix(sufixo))
    elif "@" not in ident:
        condicoes.append(Usuario.nome_de_usuario == ident)

    usuarios = (await db.scalars(select(Usuario).where(or_(*condicoes)))).all()

    if len(usuarios) == 1:
        usuario = usuarios[0]
        token = gerar_token_recuperacao(usuario.id)
        payload = decodificar_token(token, TOKEN_TIPO_RECUPERACAO)

        agora = datetime.now(UTC)
        anteriores = (
            await db.scalars(
                select(TokenRecuperacao).where(
                    TokenRecuperacao.usuario_id == usuario.id,
                    TokenRecuperacao.usado_em.is_(None),
                )
            )
        ).all()
        for anterior in anteriores:
            anterior.usado_em = agora

        db.add(
            TokenRecuperacao(
                jti=payload["jti"],
                usuario_id=usuario.id,
                exp=datetime.fromtimestamp(payload["exp"], UTC),
            )
        )
        await db.commit()

        destinos = {
            email_institucional(usuario.nome_de_usuario),
            usuario.email_alternativo,
        } - {None}
        await enviar_link(usuario.id, token, sorted(destinos))

    return MensagemResponse(mensagem=MENSAGEM_RECUPERACAO)


@router.post("/redefinir-senha", response_model=MensagemResponse)
async def redefinir_senha(
    dados: RedefinirSenhaRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MensagemResponse:
    try:
        payload = decodificar_token(dados.token, TOKEN_TIPO_RECUPERACAO)
    except TokenInvalido as erro:
        raise _erro_link_invalido() from erro

    jti = payload.get("jti")
    if not jti:
        raise _erro_link_invalido()

    registro = await db.scalar(
        select(TokenRecuperacao)
        .where(TokenRecuperacao.jti == jti)
        .with_for_update()
    )
    if (
        registro is None
        or registro.usuario_id != int(payload["sub"])
        or registro.usado_em is not None
    ):
        raise _erro_link_invalido()

    usuario = await db.get(Usuario, registro.usuario_id)
    if usuario is None:
        raise _erro_link_invalido()

    agora = datetime.now(UTC)
    usuario.senha_hash = gerar_hash(dados.nova_senha)
    registro.usado_em = agora
    await db.commit()

    return MensagemResponse(mensagem=MENSAGEM_REDEFINICAO)
