from datetime import UTC, date, datetime, time

import pytest_asyncio

from sisav.academico.models import (
    CriterioAvaliacao,
    Curso,
    Disciplina,
    Matricula,
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


async def instanciar_template(client) -> list[dict]:
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


async def criar_exame(client) -> dict:
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "exame"})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()[0]


async def lancar_nota(client, avaliacao_id: int, valor: float, matricula_id: int = 1) -> None:
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": avaliacao_id,
            "registros": [{"matricula_id": matricula_id, "valor": valor}],
        },
    )
    assert resposta.status_code == 200, resposta.text


async def boletim(client) -> dict:
    como(1)
    resposta = await client.get(f"{BASE}/alunos/me/boletim?ano=2026&semestre=1")
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["turmas"][0]


@pytest_asyncio.fixture
async def cenario_avaliacao(session_factory):
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
        db.add_all(
            [
                Turma(
                    id=1, codigo="A", semestre="2026.1", sala="I-12", dia_semana="segunda",
                    horario_inicio=time(8, 0), horario_fim=time(9, 40),
                    disciplina_id=1, professor_id=10,
                ),
                Turma(
                    id=2, codigo="B", semestre="2026.1", sala="I-13", dia_semana="terca",
                    horario_inicio=time(8, 0), horario_fim=time(9, 40),
                    disciplina_id=1, professor_id=11,
                ),
            ]
        )
        await db.flush()
        db.add_all(
            [
                Matricula(id=1, aluno_id=1, turma_id=1, ano_letivo=2026),
                Matricula(id=2, aluno_id=2, turma_id=1, ano_letivo=2026),
                Matricula(id=3, aluno_id=1, turma_id=2, ano_letivo=2026),
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


async def test_instancia_template_com_pai_folhas_e_sem_subdivisao(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    assert [item["codigo"] for item in avaliacoes] == ["1", "1-1", "1-2", "2", "2-1"]
    assert [item["tipo"] for item in avaliacoes] == [
        "criterio", "avaliacao", "avaliacao", "criterio", "avaliacao",
    ]
    assert [item["peso"] for item in avaliacoes] == [1.0, 0.6, 0.4, 1.0, 1.0]


async def test_instanciar_template_duplicado_retorna_409(client, cenario_avaliacao):
    await instanciar_template(client)
    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    assert resposta.status_code == 409


async def test_cria_exame_unico_com_peso_fixo(client, cenario_avaliacao):
    exame = await criar_exame(client)
    assert exame["codigo"] == "EX"
    assert exame["tipo"] == "exame"
    assert exame["peso"] == 1.0

    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "exame"})
    assert resposta.status_code == 409


async def test_patch_edita_nome_e_peso_da_folha(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    folha = avaliacoes[1]
    como(10)
    resposta = await client.patch(
        f"{BASE}/turmas/1/avaliacoes/{folha['id']}",
        json={"nome": "P1 revisada", "peso": 0.7},
    )
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "P1 revisada"
    assert resposta.json()["peso"] == 0.7


async def test_patch_nao_altera_peso_do_exame(client, cenario_avaliacao):
    exame = await criar_exame(client)
    como(10)
    resposta = await client.patch(
        f"{BASE}/turmas/1/avaliacoes/{exame['id']}", json={"peso": 0.5}
    )
    assert resposta.status_code == 422


async def test_patch_de_avaliacao_de_outra_turma_retorna_404(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    como(11)
    resposta = await client.patch(
        f"{BASE}/turmas/2/avaliacoes/{avaliacoes[1]['id']}", json={"nome": "x"}
    )
    assert resposta.status_code == 404


async def test_notas_e_exame_calculam_o_boletim(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    por_codigo = {item["codigo"]: item["id"] for item in avaliacoes}
    await lancar_nota(client, por_codigo["1-1"], 8.0)
    await lancar_nota(client, por_codigo["1-2"], 6.0)
    await lancar_nota(client, por_codigo["2-1"], 4.0)

    turma = await boletim(client)
    assert turma["media_pre_exame"] == 5.6
    assert turma["media_final"] == 5.6
    assert turma["situacao"] == "Exame Final"
    assert turma["limite_faltas"] == 15

    exame = await criar_exame(client)
    await lancar_nota(client, exame["id"], 5.0)

    turma = await boletim(client)
    assert turma["nota_exame"] == 5.0
    assert turma["media_final"] == 5.3
    assert turma["situacao"] == "Aprovado"


async def test_boletim_sem_notas_nao_tem_situacao(client, cenario_avaliacao):
    await instanciar_template(client)
    turma = await boletim(client)
    assert turma["media_pre_exame"] is None
    assert turma["situacao"] is None
    assert all(item["valor"] is None for item in turma["avaliacoes"])


async def test_faltas_excedidas_precedem_a_nota_no_boletim(
    client, cenario_avaliacao, session_factory
):
    avaliacoes = await instanciar_template(client)
    por_codigo = {item["codigo"]: item["id"] for item in avaliacoes}
    await lancar_nota(client, por_codigo["1-1"], 9.0)

    async with session_factory() as db:
        db.add(
            RegistroFrequencia(
                matricula_id=1,
                data=date(2026, 10, 1),
                horario_inicio=time(8, 0),
                horario_fim=time(9, 40),
                faltas=16,
            )
        )
        await db.commit()

    turma = await boletim(client)
    assert turma["total_faltas"] == 16
    assert turma["media_pre_exame"] == 9.0
    assert turma["situacao"] == "Rep. por Falta"


async def test_lancar_nota_em_criterio_retorna_422(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": avaliacoes[0]["id"],
            "registros": [{"matricula_id": 1, "valor": 8.0}],
        },
    )
    assert resposta.status_code == 422


async def test_lancar_nota_de_outra_turma_retorna_422(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    como(10)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": avaliacoes[1]["id"],
            "registros": [{"matricula_id": 3, "valor": 8.0}],
        },
    )
    assert resposta.status_code == 422


async def test_aluno_nao_pode_lancar_notas(client, cenario_avaliacao):
    avaliacoes = await instanciar_template(client)
    como(1)
    resposta = await client.put(
        f"{BASE}/turmas/1/notas",
        json={
            "avaliacao_id": avaliacoes[1]["id"],
            "registros": [{"matricula_id": 1, "valor": 8.0}],
        },
    )
    assert resposta.status_code == 403


async def test_turma_fechada_bloqueia_escrita(client, cenario_avaliacao, session_factory):
    async with session_factory() as db:
        turma = await db.get(Turma, 1)
        turma.fechada_em = datetime.now(UTC)
        turma.fechada_por = 10
        await db.commit()

    como(10)
    resposta = await client.post(f"{BASE}/turmas/1/avaliacoes", json={"tipo": "template"})
    assert resposta.status_code == 409
