from datetime import UTC, datetime, timedelta

import pytest

from sisav.auth.dependencies import get_current_user_id
from sisav.core.config import get_settings
from sisav.main import app
from sisav.notificacoes.models import Notificacao, TipoNotificacao
from sisav.usuarios.models import Perfil, Usuario

PREFIXO = f"{get_settings().api_v1_prefix}/notificacoes"


async def _popular_notificacoes(session_factory):
    agora = datetime.now(UTC)
    async with session_factory() as db:
        aluno = Usuario(
            id=1,
            nome="Aluno Teste",
            nome_de_usuario="aluno1",
            senha_hash="x",
            perfil=Perfil.ALUNO,
        )
        professor = Usuario(
            id=2,
            nome="Prof Teste",
            nome_de_usuario="prof1",
            senha_hash="x",
            perfil=Perfil.PROFESSOR,
        )
        db.add_all([aluno, professor])
        await db.flush()

        db.add_all(
            [
                Notificacao(
                    id=1,
                    usuario_id=1,
                    titulo="Aviso antigo",
                    mensagem="Prazo de matrícula aberto.",
                    tipo=TipoNotificacao.PRAZO,
                    lida=True,
                    criada_em=agora - timedelta(hours=2),
                ),
                Notificacao(
                    id=2,
                    usuario_id=1,
                    titulo="Novo aviso",
                    mensagem="Aula transferida para sala B-202.",
                    tipo=TipoNotificacao.AVISO_PROFESSOR,
                    lida=False,
                    criada_em=agora - timedelta(hours=1),
                ),
                Notificacao(
                    id=3,
                    usuario_id=1,
                    titulo="Alerta de faltas",
                    mensagem="Você atingiu 75% de presença mínima.",
                    tipo=TipoNotificacao.LIMITE_FALTAS,
                    lida=False,
                    criada_em=agora,
                ),
                Notificacao(
                    id=4,
                    usuario_id=2,
                    titulo="Notificação do professor",
                    mensagem="Não deve aparecer para o aluno.",
                    tipo=TipoNotificacao.INSTITUCIONAL,
                    lida=False,
                    criada_em=agora,
                ),
            ]
        )
        await db.commit()


@pytest.mark.asyncio
async def test_listar_notificacoes_aluno_retorna_ordenadas_e_contagem(client, session_factory):
    await _popular_notificacoes(session_factory)

    resp = await client.get(f"{PREFIXO}/aluno")
    assert resp.status_code == 200

    body = resp.json()
    assert body["nao_lidas"] == 2
    assert [n["id"] for n in body["notificacoes"]] == [3, 2, 1]


@pytest.mark.asyncio
async def test_listar_notificacoes_aluno_bloqueia_professor(client, session_factory):
    await _popular_notificacoes(session_factory)
    app.dependency_overrides[get_current_user_id] = lambda: 2

    resp = await client.get(f"{PREFIXO}/aluno")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_marcar_notificacoes_especificas_como_lidas(client, session_factory):
    await _popular_notificacoes(session_factory)

    resp = await client.patch(f"{PREFIXO}/marcar-lidas", json={"notificacao_ids": [2]})
    assert resp.status_code == 200
    assert resp.json() == {"atualizadas": 1}

    lista = (await client.get(f"{PREFIXO}/aluno")).json()
    assert lista["nao_lidas"] == 1


@pytest.mark.asyncio
async def test_marcar_todas_notificacoes_como_lidas(client, session_factory):
    await _popular_notificacoes(session_factory)

    resp = await client.patch(f"{PREFIXO}/marcar-lidas")
    assert resp.status_code == 200
    assert resp.json() == {"atualizadas": 2}

    lista = (await client.get(f"{PREFIXO}/aluno")).json()
    assert lista["nao_lidas"] == 0
