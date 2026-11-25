import pytest

from sisav.core.config import get_settings
from sisav.usuarios.models import Perfil, Usuario

pytestmark = pytest.mark.asyncio

PERFIL_URL = "/api/v1/usuarios/me/perfil"
CONTATO_URL = "/api/v1/usuarios/me/contato"
FOTO_URL = "/api/v1/usuarios/me/foto"

PNG_VALIDO = b"\x89PNG\r\n\x1a\n" + b"conteudo"


async def test_perfil_do_aluno_traz_dados_e_curso(client, cenario):
    resposta = await client.get(PERFIL_URL)

    assert resposta.status_code == 200
    assert resposta.json() == {
        "nome": "Fulano",
        "matricula": "ra1234",
        "curso": "Engenharia de Software",
        "email_institucional": "ra1234@uem.br",
        "foto_url": None,
        "telefone": None,
        "email_alternativo": None,
    }


async def test_patch_contato_atualiza_e_retorna_perfil(client, cenario):
    resposta = await client.patch(
        CONTATO_URL,
        json={
            "telefone": "  (44) 9999-0000  ",
            "email_alternativo": "  ALUNO@EXEMPLO.COM  ",
            "confirmado": True,
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["telefone"] == "(44) 9999-0000"
    assert corpo["email_alternativo"] == "aluno@exemplo.com"


async def test_patch_contato_parcial_preserva_outro_campo(client, cenario):
    await client.patch(CONTATO_URL, json={"telefone": "123", "confirmado": True})

    resposta = await client.patch(
        CONTATO_URL,
        json={"email_alternativo": "aluno@exemplo.com", "confirmado": True},
    )

    assert resposta.status_code == 200
    assert resposta.json()["telefone"] == "123"
    assert resposta.json()["email_alternativo"] == "aluno@exemplo.com"


async def test_patch_contato_sem_confirmacao_retorna_422(client, cenario):
    resposta = await client.patch(CONTATO_URL, json={"telefone": "123"})

    assert resposta.status_code == 422


async def test_patch_contato_com_email_invalido_retorna_422(client, cenario):
    resposta = await client.patch(
        CONTATO_URL,
        json={"email_alternativo": "invalido", "confirmado": True},
    )

    assert resposta.status_code == 422


async def test_patch_contato_com_email_institucional_retorna_422(client, cenario):
    resposta = await client.patch(
        CONTATO_URL,
        json={"email_alternativo": "ra1234@uem.br", "confirmado": True},
    )

    assert resposta.status_code == 422


async def test_patch_contato_com_alternativo_duplicado_retorna_409(
    client, cenario, session_factory
):
    async with session_factory() as db:
        db.add(
            Usuario(
                id=9,
                nome="Outro",
                nome_de_usuario="outro.usuario",
                senha_hash="x",
                perfil=Perfil.ALUNO,
                email_alternativo="duplicado@exemplo.com",
            )
        )
        await db.commit()

    resposta = await client.patch(
        CONTATO_URL,
        json={"email_alternativo": "duplicado@exemplo.com", "confirmado": True},
    )

    assert resposta.status_code == 409


async def test_upload_foto_valida_e_servea_o_arquivo(client, cenario):
    resposta = await client.post(
        FOTO_URL,
        files={"arquivo": ("foto.png", PNG_VALIDO, "image/png")},
    )

    assert resposta.status_code == 200
    foto_url = resposta.json()["foto_url"]
    assert foto_url.startswith("/uploads/")
    assert foto_url.endswith(".png")

    nome_arquivo = foto_url.rsplit("/", 1)[-1]
    caminho = get_settings().upload_dir / nome_arquivo
    try:
        assert caminho.exists()
        arquivo = await client.get(foto_url)
        assert arquivo.status_code == 200
        assert arquivo.content == PNG_VALIDO
    finally:
        caminho.unlink(missing_ok=True)


async def test_upload_foto_com_content_type_invalido_retorna_422(client, cenario):
    resposta = await client.post(
        FOTO_URL,
        files={"arquivo": ("foto.gif", PNG_VALIDO, "image/gif")},
    )

    assert resposta.status_code == 422


async def test_upload_foto_com_conteudo_falso_retorna_422(client, cenario):
    resposta = await client.post(
        FOTO_URL,
        files={"arquivo": ("foto.png", b"nao-e-png", "image/png")},
    )

    assert resposta.status_code == 422


async def test_upload_foto_acima_de_2mb_retorna_422(client, cenario):
    conteudo = PNG_VALIDO + b"0" * (2 * 1024 * 1024)
    resposta = await client.post(
        FOTO_URL,
        files={"arquivo": ("foto.png", conteudo, "image/png")},
    )

    assert resposta.status_code == 422
