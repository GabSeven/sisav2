import pytest

from sisav.auth import tokens
from sisav.auth.dependencies import get_current_user_id
from sisav.main import app

pytestmark = pytest.mark.asyncio

LOGIN_URL = "/api/v1/auth/login"
TOKEN_URL = "/api/v1/auth/token"


async def test_login_valido_retorna_token_e_perfil(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL,
        json={"nome_de_usuario": usuario_teste["nome_de_usuario"], "senha": usuario_teste["senha"]},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["perfil"] == "professor"
    assert corpo["access_token"]


async def test_token_do_login_carrega_usuario_e_perfil(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL,
        json={"nome_de_usuario": usuario_teste["nome_de_usuario"], "senha": usuario_teste["senha"]},
    )

    token = resposta.json()["access_token"]
    payload = tokens.decodificar_token(token, tokens.TOKEN_TIPO_ACESSO)

    assert payload["sub"] == str(usuario_teste["id"])
    assert payload["perfil"] == "professor"
    assert get_current_user_id(token) == usuario_teste["id"]


async def test_login_com_senha_incorreta_retorna_401(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL,
        json={"nome_de_usuario": usuario_teste["nome_de_usuario"], "senha": "senha-errada"},
    )

    assert resposta.status_code == 401


async def test_login_com_usuario_inexistente_retorna_401(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL,
        json={"nome_de_usuario": "nao_existe", "senha": usuario_teste["senha"]},
    )

    assert resposta.status_code == 401


async def test_login_normaliza_usuario(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL,
        json={"nome_de_usuario": "  PROFESSOR_Teste ", "senha": usuario_teste["senha"]},
    )

    assert resposta.status_code == 200


async def test_login_sem_usuario_retorna_422(client, usuario_teste):
    resposta = await client.post(LOGIN_URL, json={"senha": usuario_teste["senha"]})

    assert resposta.status_code == 422


async def test_login_sem_senha_retorna_422(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL, json={"nome_de_usuario": usuario_teste["nome_de_usuario"]}
    )

    assert resposta.status_code == 422


async def test_login_usuario_com_espaco_retorna_422(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL, json={"nome_de_usuario": "professor teste", "senha": usuario_teste["senha"]}
    )

    assert resposta.status_code == 422


async def test_login_senha_acima_de_72_bytes_retorna_422(client, usuario_teste):
    resposta = await client.post(
        LOGIN_URL, json={"nome_de_usuario": usuario_teste["nome_de_usuario"], "senha": "s" * 73}
    )

    assert resposta.status_code == 422


async def test_token_oauth2_valido_retorna_token(client, usuario_teste):
    resposta = await client.post(
        TOKEN_URL,
        data={
            "username": usuario_teste["nome_de_usuario"],
            "password": usuario_teste["senha"],
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    payload = tokens.decodificar_token(corpo["access_token"], tokens.TOKEN_TIPO_ACESSO)
    assert payload["sub"] == str(usuario_teste["id"])


async def test_token_oauth2_com_senha_incorreta_retorna_401(client, usuario_teste):
    resposta = await client.post(
        TOKEN_URL,
        data={
            "username": usuario_teste["nome_de_usuario"],
            "password": "senha-errada",
        },
    )

    assert resposta.status_code == 401


async def test_swagger_token_url_aponta_para_endpoint_oauth2():
    esquema = app.openapi()["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    token_url = esquema["flows"]["password"]["tokenUrl"]

    assert token_url == TOKEN_URL
