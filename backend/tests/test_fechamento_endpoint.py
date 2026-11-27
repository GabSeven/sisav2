from datetime import date, time

import pytest_asyncio
from sqlalchemy import select

from sisav.academico.models import (
    CriterioAvaliacao,
    Curso,
    Disciplina,
    Matricula,
    Nota,
    RegistroFrequencia,
    SubcriterioAvaliacao,
    Turma,
)
from sisav.auth.dependencies import get_current_user_id
from sisav.main import app
from sisav.usuarios.models import Aluno, Perfil, Usuario

BASE = "/api/v1/avaliacao-frequencia"


def como(usuario_id: int) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: usuario_id


async def lancar(client, avaliacao_id: int, matricula_id: int, valor: float) -> None:
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": avaliacao_id,
            "registros": [{"matricula_id": matricula_id, "valor": valor}],
        },
    )
    assert resposta.status_code == 200, resposta.text


async def preparar(client, com_exame: bool = False) -> dict[str, int]:
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    assert resposta.status_code == 201, resposta.text
    por_codigo = {item["codigo"]: item["id"] for item in resposta.json()}

    for codigo, valor in (("1-1", 8.0), ("1-2", 6.0), ("2-1", 4.0)):
        for matricula_id in (1, 2):
            await lancar(client, por_codigo[codigo], matricula_id, valor)

    if com_exame:
        como(10)
        resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "exame"})
        assert resposta.status_code == 201, resposta.text
        exame_id = resposta.json()[0]["id"]
        por_codigo["EX"] = exame_id
        for matricula_id in (1, 2):
            await lancar(client, exame_id, matricula_id, 5.0)
    return por_codigo


@pytest_asyncio.fixture
async def cenario_fechamento(session_factory):
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
                Disciplina(id=1, nome="Construção de Software", carga_horaria=60),
            ]
        )
        await db.flush()
        db.add_all([Aluno(id=1, curso_id=1), Aluno(id=2, curso_id=1)])
        db.add(
            Turma(
                id=1, codigo="A", semestre="2026.1", sala="I-12", dia_semana="segunda",
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
        db.add_all(
            [
                CriterioAvaliacao(id=1, disciplina_id=1, ordem=1, nome="Provas", peso=100),
                CriterioAvaliacao(id=2, disciplina_id=1, ordem=2, nome="Trabalhos", peso=100),
            ]
        )
        await db.flush()
        db.add_all(
            [
                SubcriterioAvaliacao(id=1, criterio_id=1, ordem=1, nome="P1", peso=60),
                SubcriterioAvaliacao(id=2, criterio_id=1, ordem=2, nome="P2", peso=40),
            ]
        )
        await db.commit()


async def test_fechar_gera_snapshot_e_trava_escrita(client, cenario_fechamento):
    por_codigo = await preparar(client, com_exame=True)
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/fechar")
    assert resposta.status_code == 201, resposta.text
    dados = resposta.json()
    assert dados["fechada_em"] is not None
    assert len(dados["consolidacoes"]) == 2
    consolidacao = dados["consolidacoes"][0]
    assert consolidacao["media_pre_exame"] == 5.6
    assert consolidacao["nota_exame"] == 5.0
    assert consolidacao["media_final"] == 5.3
    assert consolidacao["situacao"] == "Aprovado"
    assert consolidacao["limite_faltas"] == 15

    como(10)
    consulta = await client.get(f"{BASE}/turmas/1/consolidacao")
    assert consulta.status_code == 200
    assert consulta.json()["consolidacoes"] == dados["consolidacoes"]

    como(10)
    assert (await client.post(f"{BASE}/turmas/1/fechar")).status_code == 409

    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": por_codigo["1-1"],
            "registros": [{"matricula_id": 1, "valor": 9.0}],
        },
    )
    assert resposta.status_code == 409

    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/faltas",
        json={
            "data": "2026-10-13",
            "horario_inicio": "08:00",
            "horario_fim": "09:40",
            "aulas_no_dia": 2,
            "registros": [{"matricula_id": 1, "faltas": 1}],
        },
    )
    assert resposta.status_code == 409


async def test_fechamento_exige_todas_as_folhas(client, cenario_fechamento):
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    por_codigo = {item["codigo"]: item["id"] for item in resposta.json()}
    await lancar(client, por_codigo["1-1"], 1, 8.0)
    await lancar(client, por_codigo["1-2"], 1, 6.0)
    await lancar(client, por_codigo["2-1"], 1, 4.0)

    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/fechar")
    assert resposta.status_code == 422
    assert "sem nota em" in resposta.json()["detail"]

    como(10)
    consulta = await client.get(f"{BASE}/turmas/1/consolidacao")
    assert consulta.json()["fechada_em"] is None


async def test_fechar_sem_avaliacoes_retorna_409(client, cenario_fechamento):
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/fechar")
    assert resposta.status_code == 409


async def test_boletim_le_snapshot_apos_fechamento(
    client, cenario_fechamento, session_factory
):
    await preparar(client)
    como(10)
    assert (await client.post(f"{BASE}/turmas/1/fechar")).status_code == 201

    async with session_factory() as db:
        nota = (
            await db.scalars(
                select(Nota).where(Nota.matricula_id == 1, Nota.valor == 800)
            )
        ).first()
        nota.valor = 1000
        db.add(
            RegistroFrequencia(
                matricula_id=1,
                data=date(2026, 10, 13),
                horario_inicio=time(8, 0),
                horario_fim=time(9, 40),
                faltas=5,
            )
        )
        await db.commit()

    como(1)
    resposta = await client.get(f"{BASE}/alunos/me/boletim?ano=2026&semestre=1")
    assert resposta.status_code == 200
    turma = resposta.json()["turmas"][0]
    assert turma["media_pre_exame"] == 5.6
    assert turma["total_faltas"] == 0
    assert turma["situacao"] == "Exame Final"


async def test_consolidacao_respeita_professor_e_gestor(client, cenario_fechamento):
    await preparar(client)
    como(10)
    assert (await client.post(f"{BASE}/turmas/1/fechar")).status_code == 201

    como(11)
    assert (await client.get(f"{BASE}/turmas/1/consolidacao")).status_code == 403

    como(12)
    resposta = await client.get(f"{BASE}/turmas/1/consolidacao")
    assert resposta.status_code == 200
    assert len(resposta.json()["consolidacoes"]) == 2
