from datetime import time

import pytest_asyncio

from sisav.academico.models import (
    Avaliacao,
    CriterioAvaliacao,
    Disciplina,
    SubcriterioAvaliacao,
    Turma,
)
from sisav.auth.dependencies import get_current_user_id
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario

BASE = "/api/v1/disciplinas"


def como(usuario_id: int) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: usuario_id


@pytest_asyncio.fixture
async def cenario_template(session_factory):
    async with session_factory() as db:
        db.add_all(
            [
                Usuario(
                    id=1, nome="Gestor", nome_de_usuario="g1", senha_hash="x",
                    perfil=Perfil.GESTOR,
                ),
                Usuario(
                    id=2, nome="Professor", nome_de_usuario="p1", senha_hash="x",
                    perfil=Perfil.PROFESSOR,
                ),
                Disciplina(id=1, nome="Cálculo I", carga_horaria=90),
            ]
        )
        await db.flush()
        db.add(
            Turma(
                id=1, codigo="A", semestre="2026.1", sala="B-101", dia_semana="segunda",
                horario_inicio=time(8, 0), horario_fim=time(9, 40),
                disciplina_id=1, professor_id=2,
            )
        )
        db.add(CriterioAvaliacao(id=1, disciplina_id=1, ordem=1, nome="Provas", peso=100))
        await db.flush()
        db.add(
            SubcriterioAvaliacao(
                id=1, criterio_id=1, ordem=1, nome="P1", peso=60
            )
        )
        db.add(
            Avaliacao(
                id=1, turma_id=1, nome="Provas antiga", codigo="1",
                tipo="criterio", peso=80,
            )
        )
        await db.commit()


async def test_gestor_le_template(client, cenario_template):
    como(1)
    resposta = await client.get(f"{BASE}/1/criterios")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["disciplina"] == "Cálculo I"
    assert dados["criterios"][0]["nome"] == "Provas"
    assert dados["criterios"][0]["peso"] == 1.0
    assert dados["criterios"][0]["subcriterios"][0]["peso"] == 0.6


async def test_put_substitui_template_sem_propagar(client, cenario_template, session_factory):
    como(1)
    resposta = await client.put(
        f"{BASE}/1/criterios",
        json={
            "criterios": [
                {
                    "ordem": 1,
                    "nome": "Avaliações teóricas",
                    "peso": 0.7,
                    "subcriterios": [
                        {"ordem": 1, "nome": "Prova 1", "peso": 0.6},
                        {"ordem": 2, "nome": "Prova 2", "peso": 0.4},
                    ],
                },
                {
                    "ordem": 2,
                    "nome": "Trabalho final",
                    "peso": 0.3,
                    "subcriterios": [],
                },
            ]
        },
    )
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert [item["nome"] for item in dados["criterios"]] == [
        "Avaliações teóricas",
        "Trabalho final",
    ]
    assert [sub["ordem"] for sub in dados["criterios"][0]["subcriterios"]] == [1, 2]

    como(1)
    consulta = await client.get(f"{BASE}/1/criterios")
    assert consulta.json() == dados

    async with session_factory() as db:
        avaliacao = await db.get(Avaliacao, 1)
        assert avaliacao.nome == "Provas antiga"
        assert avaliacao.peso == 80


async def test_put_rejeita_ordem_repetida(client, cenario_template):
    como(1)
    resposta = await client.put(
        f"{BASE}/1/criterios",
        json={
            "criterios": [
                {"ordem": 1, "nome": "A", "peso": 1.0, "subcriterios": []},
                {"ordem": 1, "nome": "B", "peso": 1.0, "subcriterios": []},
            ]
        },
    )
    assert resposta.status_code == 422


async def test_put_rejeita_peso_zero(client, cenario_template):
    como(1)
    resposta = await client.put(
        f"{BASE}/1/criterios",
        json={
            "criterios": [
                {"ordem": 1, "nome": "A", "peso": 0, "subcriterios": []},
            ]
        },
    )
    assert resposta.status_code == 422


async def test_professor_nao_acessa_template(client, cenario_template):
    como(2)
    resposta = await client.get(f"{BASE}/1/criterios")
    assert resposta.status_code == 403


async def test_disciplina_inexistente_retorna_404(client, cenario_template):
    como(1)
    resposta = await client.get(f"{BASE}/99/criterios")
    assert resposta.status_code == 404
