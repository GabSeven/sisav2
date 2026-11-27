from datetime import UTC, datetime, time

import pytest_asyncio

from sisav.academico.models import (
    CriterioAvaliacao,
    Curso,
    Disciplina,
    Matricula,
    SubcriterioAvaliacao,
    Turma,
)
from sisav.auth.dependencies import get_current_user_id
from sisav.main import app
from sisav.usuarios.models import Aluno, Perfil, Usuario

BASE = "/api/v1/avaliacao-frequencia"


def como(usuario_id: int) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: usuario_id


@pytest_asyncio.fixture
async def cenario_leitura(session_factory):
    async with session_factory() as db:
        db.add_all(
            [
                Curso(id=1, nome="Engenharia de Software"),
                Usuario(
                    id=10, nome="Prof Um", nome_de_usuario="p1", senha_hash="x",
                    perfil=Perfil.PROFESSOR,
                ),
                Usuario(
                    id=11, nome="Prof Dois", nome_de_usuario="p2", senha_hash="x",
                    perfil=Perfil.PROFESSOR,
                ),
                Usuario(
                    id=12, nome="Gestor", nome_de_usuario="g1", senha_hash="x",
                    perfil=Perfil.GESTOR,
                ),
                Usuario(
                    id=1, nome="Aluno Um", nome_de_usuario="a1", senha_hash="x",
                    perfil=Perfil.ALUNO,
                ),
                Usuario(
                    id=2, nome="Aluno Dois", nome_de_usuario="a2", senha_hash="x",
                    perfil=Perfil.ALUNO,
                ),
                Disciplina(id=1, nome="Cálculo I", carga_horaria=90),
            ]
        )
        await db.flush()
        db.add_all([Aluno(id=1, curso_id=1), Aluno(id=2, curso_id=1)])
        db.add(
            Turma(
                id=1, codigo="A", semestre="2026.1", sala="B-101", dia_semana="segunda",
                horario_inicio=time(8, 0), horario_fim=time(9, 40),
                disciplina_id=1, professor_id=10,
            )
        )
        await db.flush()
        db.add_all(
            [
                Matricula(id=1, aluno_id=1, turma_id=1, ano_letivo=2026),
                Matricula(id=2, aluno_id=2, turma_id=1, ano_letivo=2026),
            ]
        )
        db.add(
            CriterioAvaliacao(id=1, disciplina_id=1, ordem=1, nome="Provas", peso=100)
        )
        await db.flush()
        db.add(
            SubcriterioAvaliacao(
                id=1, criterio_id=1, ordem=1, nome="P1", peso=100
            )
        )
        await db.commit()


async def instanciar(client) -> dict[str, int]:
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    assert resposta.status_code == 201, resposta.text
    return {item["codigo"]: item["id"] for item in resposta.json()}


async def test_listar_alunos_da_turma(client, cenario_leitura):
    como(10)
    resposta = await client.get(f"{BASE}/turmas/1/alunos")
    assert resposta.status_code == 200
    por_id = {item["matricula_id"]: item for item in resposta.json()["alunos"]}
    assert set(por_id) == {1, 2}
    assert por_id[1]["nome"] == "Aluno Um"
    assert por_id[2]["nome_de_usuario"] == "a2"

    como(12)
    assert (await client.get(f"{BASE}/turmas/1/alunos")).status_code == 200

    como(11)
    assert (await client.get(f"{BASE}/turmas/1/alunos")).status_code == 403


async def test_listar_avaliacoes_e_notas(client, cenario_leitura):
    por_codigo = await instanciar(client)
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": por_codigo["1-1"],
            "registros": [{"matricula_id": 1, "valor": 7.5}],
        },
    )
    assert resposta.status_code == 200

    como(10)
    avaliacoes = await client.get(f"{BASE}/turmas/1/avaliacoes")
    assert avaliacoes.status_code == 200
    assert [item["codigo"] for item in avaliacoes.json()] == ["1", "1-1"]

    notas = await client.get(f"{BASE}/turmas/1/notas")
    assert notas.status_code == 200
    assert notas.json()["notas"] == [
        {"avaliacao_id": por_codigo["1-1"], "matricula_id": 1, "valor": 7.5}
    ]


async def test_consultar_faltas_do_bloco(client, cenario_leitura):
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/faltas",
        json={
            "data": "2026-10-13",
            "horario_inicio": "08:00",
            "horario_fim": "09:40",
            "aulas_no_dia": 2,
            "registros": [
                {"matricula_id": 1, "faltas": 2},
                {"matricula_id": 2, "faltas": 0},
            ],
        },
    )
    assert resposta.status_code == 200
    por_id = {item["matricula_id"]: item for item in resposta.json()["alunos"]}
    assert por_id[1]["faltas_no_bloco"] == 2
    assert por_id[2]["faltas_no_bloco"] == 0

    como(10)
    consulta = await client.get(
        f"{BASE}/turmas/1/faltas?data=2026-10-13"
        "&horario_inicio=08:00&horario_fim=09:40"
    )
    assert consulta.status_code == 200
    dados = consulta.json()
    por_id = {item["matricula_id"]: item for item in dados["alunos"]}
    assert por_id[1]["faltas_no_bloco"] == 2
    assert por_id[1]["total_faltas"] == 2
    assert por_id[1]["limite_faltas"] == 22
    assert por_id[1]["percentual_faltas"] == 2.22

    como(10)
    invalido = await client.get(
        f"{BASE}/turmas/1/faltas?data=2026-10-13"
        "&horario_inicio=10:00&horario_fim=11:40"
    )
    assert invalido.status_code == 422


async def test_leitura_continua_disponivel_apos_fechamento(
    client, cenario_leitura, session_factory
):
    por_codigo = await instanciar(client)
    como(10)
    await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": por_codigo["1-1"],
            "registros": [
                {"matricula_id": 1, "valor": 8.0},
                {"matricula_id": 2, "valor": 6.0},
            ],
        },
    )
    async with session_factory() as db:
        turma = await db.get(Turma, 1)
        turma.fechada_em = datetime.now(UTC)
        await db.commit()

    como(10)
    assert (await client.get(f"{BASE}/turmas/1/alunos")).status_code == 200
    assert (await client.get(f"{BASE}/turmas/1/avaliacoes")).status_code == 200
    assert (await client.get(f"{BASE}/turmas/1/notas")).status_code == 200
    consulta = await client.get(
        f"{BASE}/turmas/1/faltas?data=2026-10-13"
        "&horario_inicio=08:00&horario_fim=09:40"
    )
    assert consulta.status_code == 200
