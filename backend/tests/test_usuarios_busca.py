import pytest

from sisav.auth.dependencies import get_current_user_id
from sisav.auth.security import gerar_hash
from sisav.core.config import get_settings
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario

PREFIXO = get_settings().api_v1_prefix


async def _criar_usuarios(session_factory):
    senha = gerar_hash("senha123")
    async with session_factory() as db:
        db.add_all(
            [
                Usuario(
                    id=1,
                    nome="Ana Silva",
                    nome_de_usuario="ra10001",
                    senha_hash=senha,
                    perfil=Perfil.ALUNO,
                ),
                Usuario(
                    id=2,
                    nome="Ana Paula Souza",
                    nome_de_usuario="prof_ana",
                    senha_hash=senha,
                    perfil=Perfil.PROFESSOR,
                    foto_perfil="ana.jpg",
                ),
                Usuario(
                    id=3,
                    nome="Bruno Costa",
                    nome_de_usuario="ra10002",
                    senha_hash=senha,
                    perfil=Perfil.ALUNO,
                ),
            ]
        )
        await db.commit()


@pytest.mark.asyncio
async def test_busca_por_nome_exclui_proprio_usuario(client, session_factory):
    await _criar_usuarios(session_factory)
    override_anterior = app.dependency_overrides.get(get_current_user_id)
    app.dependency_overrides[get_current_user_id] = lambda: 1
    try:
        resp = await client.get(f"{PREFIXO}/usuarios/busca", params={"q": "ana"})
        assert resp.status_code == 200
        dados = resp.json()
        assert len(dados) == 1
        assert dados[0]["id"] == 2
        assert dados[0]["nome"] == "Ana Paula Souza"
        assert dados[0]["perfil"] == "professor"
        assert dados[0]["email_institucional"] == "prof_ana@uem.br"
        assert dados[0]["foto_url"] == "/uploads/ana.jpg"
    finally:
        if override_anterior is None:
            app.dependency_overrides.pop(get_current_user_id, None)
        else:
            app.dependency_overrides[get_current_user_id] = override_anterior


@pytest.mark.asyncio
async def test_busca_por_matricula_e_filtro_perfil(client, session_factory):
    await _criar_usuarios(session_factory)
    override_anterior = app.dependency_overrides.get(get_current_user_id)
    app.dependency_overrides[get_current_user_id] = lambda: 1
    try:
        resp = await client.get(
            f"{PREFIXO}/usuarios/busca",
            params={"q": "ra100", "perfil": "aluno"},
        )
        assert resp.status_code == 200
        dados = resp.json()
        assert len(dados) == 1
        assert dados[0]["nome_de_usuario"] == "ra10002"

        resp_vazio = await client.get(
            f"{PREFIXO}/usuarios/busca",
            params={"q": "ra100", "perfil": "professor"},
        )
        assert resp_vazio.status_code == 200
        assert resp_vazio.json() == []
    finally:
        if override_anterior is None:
            app.dependency_overrides.pop(get_current_user_id, None)
        else:
            app.dependency_overrides[get_current_user_id] = override_anterior


@pytest.mark.asyncio
async def test_busca_com_termo_em_branco_retorna_vazio(client, session_factory):
    await _criar_usuarios(session_factory)
    override_anterior = app.dependency_overrides.get(get_current_user_id)
    app.dependency_overrides[get_current_user_id] = lambda: 1
    try:
        resp = await client.get(f"{PREFIXO}/usuarios/busca", params={"q": "   "})
        assert resp.status_code == 200
        assert resp.json() == []
    finally:
        if override_anterior is None:
            app.dependency_overrides.pop(get_current_user_id, None)
        else:
            app.dependency_overrides[get_current_user_id] = override_anterior