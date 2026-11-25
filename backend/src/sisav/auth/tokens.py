from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from sisav.core.config import get_settings
from sisav.usuarios.models import Perfil

TOKEN_TIPO_ACESSO = "access"
TOKEN_TIPO_REFRESH = "refresh"
TOKEN_TIPO_RECUPERACAO = "recuperacao"

RESERVADAS = {"sub", "tipo", "iat", "exp", "perfil"}

class TokenInvalido(Exception):
    pass

def _assinar(payload: dict[str, object]):
    config = get_settings()
    return jwt.encode(
        payload,
        config.jwt_secret,
        algorithm="HS256",
        headers={"typ": "JWT"},
    )


def _gerar_token(
    usuario_id: int,
    tipo: str,
    validade: timedelta,
    *,
    perfil: Perfil | None = None,
    claims_extras: dict[str, object] | None = None) -> str:
    
    if tipo in (TOKEN_TIPO_ACESSO, TOKEN_TIPO_REFRESH) and perfil is None:
        raise ValueError(f"{tipo} exige perfil")
    
    conflitos = RESERVADAS.intersection(claims_extras or {})
    if conflitos:
        raise ValueError(f"claim reservadas: {sorted(conflitos)}")

    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "tipo": tipo,
        "iat": agora,
        "exp": agora + validade,
        **(claims_extras or {})
    }

    if perfil is not None:
        payload["perfil"] = perfil.value
    return _assinar(payload)


def gerar_token_acesso(usuario_id: int, perfil: Perfil) -> str:
    return _gerar_token(
        usuario_id,
        TOKEN_TIPO_ACESSO,
        timedelta(minutes=get_settings().jwt_access_minutes),
        perfil=perfil
    )


def gerar_token_refresh(usuario_id: int, perfil: Perfil) -> str:
    return _gerar_token(
        usuario_id,
        TOKEN_TIPO_REFRESH,
        timedelta(days=get_settings().jwt_refresh_days),
        perfil=perfil
    )

def gerar_token_recuperacao(usuario_id: int) -> str:
    return _gerar_token(
        usuario_id,
        TOKEN_TIPO_RECUPERACAO,
        timedelta(minutes=get_settings().jwt_reset_minutes),
        claims_extras={"jti": uuid4().hex}
    )
    

def decodificar_token(token: str, tipo: str) -> dict:
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as erro:
        raise TokenInvalido("Token inválido ou expirado.") from erro

    if payload.get("tipo") != tipo:
        raise TokenInvalido("Tipo de token incompatível com o recurso.")

    return payload


def usuario_id_do_token(token: str, tipo: str = TOKEN_TIPO_ACESSO) -> int:
    payload = decodificar_token(token, tipo)
    return int(payload["sub"])