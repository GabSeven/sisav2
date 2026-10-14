from datetime import UTC, datetime, timedelta

import jwt
import pytest

from sisav.auth import tokens
from sisav.core.config import get_settings
from sisav.usuarios.models import Perfil


def test_token_acesso_tem_claims_esperadas():
    token = tokens.gerar_token_acesso(7, Perfil.ALUNO)
    payload = tokens.decodificar_token(token, tokens.TOKEN_TIPO_ACESSO)

    assert payload["sub"] == "7"
    assert payload["perfil"] == "aluno"
    assert payload["tipo"] == "access"


def test_token_refresh_valida_no_tipo_correto():
    token = tokens.gerar_token_refresh(9, Perfil.PROFESSOR)
    payload = tokens.decodificar_token(token, tokens.TOKEN_TIPO_REFRESH)

    assert payload["sub"] == "9"
    assert payload["perfil"] == "professor"
    assert payload["tipo"] == "refresh"


def test_tipo_de_token_e_verificado():
    token = tokens.gerar_token_acesso(1, Perfil.ALUNO)

    with pytest.raises(tokens.TokenInvalido):
        tokens.decodificar_token(token, tokens.TOKEN_TIPO_REFRESH)


def test_token_com_assinatura_adulterada_rejeitado():
    token = tokens.gerar_token_acesso(1, Perfil.GESTOR)
    adulterado = token.rsplit(".", 1)[0] + ".AAAAAAAAAA"

    with pytest.raises(tokens.TokenInvalido):
        tokens.decodificar_token(adulterado, tokens.TOKEN_TIPO_ACESSO)


def test_token_expirado_rejeitado():
    agora = datetime.now(UTC)
    payload = {
        "sub": "1",
        "perfil": "aluno",
        "tipo": tokens.TOKEN_TIPO_ACESSO,
        "iat": agora - timedelta(hours=1),
        "exp": agora - timedelta(minutes=1),
    }
    token = jwt.encode(payload, get_settings().jwt_secret, algorithm="HS256")

    with pytest.raises(tokens.TokenInvalido):
        tokens.decodificar_token(token, tokens.TOKEN_TIPO_ACESSO)


def test_usuario_id_extraido_do_token():
    token = tokens.gerar_token_acesso(42, Perfil.PROFESSOR)

    assert tokens.usuario_id_do_token(token) == 42