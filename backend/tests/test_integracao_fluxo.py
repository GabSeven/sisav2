import pytest

from sisav.auth.dependencies import get_current_user_id
from sisav.auth.security import gerar_hash
from sisav.core.config import get_settings
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario

PREFIXO = get_settings().api_v1_prefix


@pytest.mark.asyncio
async def test_cors_preflight_permite_frontend_vite(client):
    resp = await client.options(
        f"{PREFIXO}/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.asyncio
async def test_fluxo_login_e_acesso_rota_protegida_com_jwt_real(client, session_factory):
    async with session_factory() as db:
        db.add(
            Usuario(
                id=10,
                nome="Aluno Integracao",
                nome_de_usuario="aluno_int",
                senha_hash=gerar_hash("senha123"),
                perfil=Perfil.ALUNO,
            )
        )
        await db.commit()

    override_anterior = app.dependency_overrides.pop(get_current_user_id, None)
    try:
        # 1. Sem token deve retornar 401
        sem_token = await client.get(f"{PREFIXO}/notificacoes/aluno")
        assert sem_token.status_code == 401

        # 2. Login exatamente no formato de frontend/src/modules/auth/api.ts
        login_resp = await client.post(
            f"{PREFIXO}/auth/login",
            json={"nome_de_usuario": "aluno_int", "senha": "senha123"},
        )
        assert login_resp.status_code == 200
        dados = login_resp.json()
        assert dados["token_type"] == "bearer"
        assert dados["perfil"] == "aluno"
        assert dados["access_token"]

        # 3. Usa o JWT real retornado para acessar uma rota protegida
        protegida = await client.get(
            f"{PREFIXO}/notificacoes/aluno",
            headers={"Authorization": f"Bearer {dados['access_token']}"},
        )
        assert protegida.status_code == 200
        assert protegida.json() == {"nao_lidas": 0, "notificacoes": []}
    finally:
        if override_anterior is not None:
            app.dependency_overrides[get_current_user_id] = override_anterior