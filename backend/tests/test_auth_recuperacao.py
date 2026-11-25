import pytest
import pytest_asyncio

from sisav.auth import tokens
from sisav.auth.envio import get_enviador_link
from sisav.auth.models import TokenRecuperacao
from sisav.auth.security import gerar_hash
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario

pytestmark = pytest.mark.asyncio

RECUPERAR_URL = "/api/v1/auth/recuperar-senha"
REDEFINIR_URL = "/api/v1/auth/redefinir-senha"
LOGIN_URL = "/api/v1/auth/login"


class SpyEnviador:
    def __init__(self) -> None:
        self.chamadas: list[tuple[int, str, list[str]]] = []

    async def __call__(self, usuario_id: int, token: str, destinos: list[str]) -> None:
        self.chamadas.append((usuario_id, token, destinos))


@pytest_asyncio.fixture
async def usuario_recuperacao(session_factory):
    senha = "senha-antiga"
    async with session_factory() as db:
        db.add(
            Usuario(
                id=7,
                nome="Usuario Teste",
                nome_de_usuario="usuario.teste",
                senha_hash=gerar_hash(senha),
                perfil=Perfil.ALUNO,
                email_alternativo="alternativo@exemplo.com",
            )
        )
        await db.commit()
    return {
        "id": 7,
        "nome_de_usuario": "usuario.teste",
        "senha": senha,
        "email_alternativo": "alternativo@exemplo.com",
    }


@pytest.fixture
def spy_enviador():
    spy = SpyEnviador()
    app.dependency_overrides[get_enviador_link] = lambda: spy
    yield spy
    app.dependency_overrides.pop(get_enviador_link, None)


async def test_recuperar_senha_registra_token_e_envia_link(
    client, session_factory, usuario_recuperacao, spy_enviador
):
    resposta = await client.post(
        RECUPERAR_URL, json={"identificador": "alternativo@exemplo.com"}
    )

    assert resposta.status_code == 202
    assert resposta.json() == {
        "mensagem": "Se o e-mail estiver cadastrado, enviaremos um link para redefinir a senha."
    }
    assert len(spy_enviador.chamadas) == 1

    usuario_id, token, destinos = spy_enviador.chamadas[0]
    payload = tokens.decodificar_token(token, tokens.TOKEN_TIPO_RECUPERACAO)

    assert usuario_id == usuario_recuperacao["id"]
    assert payload["jti"]
    assert "usuario.teste@uem.br" in destinos
    assert "alternativo@exemplo.com" in destinos

    async with session_factory() as db:
        registro = await db.get(TokenRecuperacao, payload["jti"])

    assert registro is not None
    assert registro.usuario_id == usuario_recuperacao["id"]
    assert registro.usado_em is None


async def test_recuperar_senha_inexistente_nao_envia(client, spy_enviador):
    resposta = await client.post(
        RECUPERAR_URL, json={"identificador": "ninguem@exemplo.com"}
    )

    assert resposta.status_code == 202
    assert spy_enviador.chamadas == []


async def test_recuperar_senha_ambiguiguo_nao_envia(
    client, session_factory, usuario_recuperacao, spy_enviador
):
    async with session_factory() as db:
        usuario = await db.get(Usuario, usuario_recuperacao["id"])
        usuario.email_alternativo = "conflito@uem.br"
        db.add(
            Usuario(
                id=8,
                nome="Conflito",
                nome_de_usuario="conflito",
                senha_hash="x",
                perfil=Perfil.ALUNO,
            )
        )
        await db.commit()

    resposta = await client.post(RECUPERAR_URL, json={"identificador": "conflito@uem.br"})

    assert resposta.status_code == 202
    assert spy_enviador.chamadas == []


async def test_redefinir_senha_valida_e_marca_token_como_usado(
    client, session_factory, usuario_recuperacao, spy_enviador
):
    await client.post(RECUPERAR_URL, json={"identificador": "alternativo@exemplo.com"})
    token = spy_enviador.chamadas[0][1]

    resposta = await client.post(
        REDEFINIR_URL, json={"token": token, "nova_senha": "senha-nova-123"}
    )

    assert resposta.status_code == 200

    login = await client.post(
        LOGIN_URL,
        json={
            "nome_de_usuario": usuario_recuperacao["nome_de_usuario"],
            "senha": "senha-nova-123",
        },
    )
    assert login.status_code == 200

    jti = tokens.decodificar_token(token, tokens.TOKEN_TIPO_RECUPERACAO)["jti"]
    async with session_factory() as db:
        registro = await db.get(TokenRecuperacao, jti)
    assert registro.usado_em is not None


async def test_redefinir_senha_rejeita_token_reutilizado(
    client, usuario_recuperacao, spy_enviador
):
    await client.post(RECUPERAR_URL, json={"identificador": "alternativo@exemplo.com"})
    token = spy_enviador.chamadas[0][1]

    primeira = await client.post(
        REDEFINIR_URL, json={"token": token, "nova_senha": "senha-nova-123"}
    )
    segunda = await client.post(
        REDEFINIR_URL, json={"token": token, "nova_senha": "outra-senha-123"}
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 401


async def test_redefinir_senha_rejeita_token_de_access(client):
    token = tokens.gerar_token_acesso(7, Perfil.ALUNO)

    resposta = await client.post(
        REDEFINIR_URL, json={"token": token, "nova_senha": "senha-nova-123"}
    )

    assert resposta.status_code == 401


async def test_redefinir_senha_acima_de_72_bytes_retorna_422(
    client, usuario_recuperacao, spy_enviador
):
    await client.post(RECUPERAR_URL, json={"identificador": "alternativo@exemplo.com"})
    token = spy_enviador.chamadas[0][1]

    resposta = await client.post(
        REDEFINIR_URL, json={"token": token, "nova_senha": "s" * 73}
    )

    assert resposta.status_code == 422
