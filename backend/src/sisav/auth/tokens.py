from datetime import UTC, datetime, timedelta

import jwt

from sisav.core.config import get_settings
from sisav.usuarios.models import Perfil

TOKEN_TIPO_ACESSO = "access"
TOKEN_TIPO_REFRESH = "refresh"


class TokenInvalido(Exception):
    pass


def _gerar_token(usuario_id: int, perfil: Perfil, tipo: str, validade: timedelta) -> str:
    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "perfil": perfil.value,
        "tipo": tipo,
        "iat": agora,
        "exp": agora + validade,
    }
    config = get_settings()
    return jwt.encode(
        payload,
        config.jwt_secret,
        algorithm="HS256",
        headers={"typ": "JWT"},
    )


def gerar_token_acesso(usuario_id: int, perfil: Perfil) -> str:
    return _gerar_token(
        usuario_id,
        perfil,
        TOKEN_TIPO_ACESSO,
        timedelta(minutes=get_settings().jwt_access_minutes),
    )


def gerar_token_refresh(usuario_id: int, perfil: Perfil) -> str:
    return _gerar_token(
        usuario_id,
        perfil,
        TOKEN_TIPO_REFRESH,
        timedelta(days=get_settings().jwt_refresh_days),
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