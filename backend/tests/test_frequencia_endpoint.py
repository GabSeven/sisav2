import pytest_asyncio

from sisav.academico.models import Disciplina, Matricula, Turma
from sisav.auth.dependencies import get_current_user_id
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario

URL = "/api/v1/avaliacao-frequencia/turmas/{}/faltas"


def corpo(data: str, aulas: int, faltas: dict[int, int]) -> dict:
    return {
        "data": data,
        "aulas_no_dia": aulas,
        "registros": [{"matricula_id": m, "faltas": f} for m, f in faltas.items()],
    }


def como(usuario_id: int) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: usuario_id


def por_matricula(resposta) -> dict:
    return {a["matricula_id"]: a for a in resposta.json()["alunos"]}


@pytest_asyncio.fixture
async def cenario_frequencia(session_factory):
    async with session_factory() as db:
        db.add_all(
            [
                Usuario(
                    id=10,
                    nome="Prof Um",
                    nome_de_usuario="p1",
                    senha_hash="x",
                    perfil=Perfil.PROFESSOR,
                ),
                Usuario(
                    id=11,
                    nome="Prof Dois",
                    nome_de_usuario="p2",
                    senha_hash="x",
                    perfil=Perfil.PROFESSOR,
                ),
                Usuario(
                    id=1, nome="Aluno Um", nome_de_usuario="a1", senha_hash="x", perfil=Perfil.ALUNO
                ),
                Usuario(
                    id=2,
                    nome="Aluno Dois",
                    nome_de_usuario="a2",
                    senha_hash="x",
                    perfil=Perfil.ALUNO,
                ),
                Disciplina(id=1, nome="Construção de Software", carga_horaria=60),
            ]
        )
        await db.flush()
        db.add_all(
            [
                Turma(
                    id=1,
                    codigo="A",
                    semestre="2026.2",
                    sala="I-12",
                    dia_semana="segunda",
                    horario_inicio="08:00",
                    horario_fim="09:40",
                    disciplina_id=1,
                    professor_id=10,
                ),
                Turma(
                    id=2,
                    codigo="B",
                    semestre="2026.2",
                    sala="I-13",
                    dia_semana="terca",
                    horario_inicio="08:00",
                    horario_fim="09:40",
                    disciplina_id=1,
                    professor_id=11,
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
        await db.commit()


async def test_professor_da_turma_lanca_faltas(client, cenario_frequencia):
    como(10)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {1: 0, 2: 3}))
    assert r.status_code == 200
    alunos = por_matricula(r)
    assert alunos[1]["total_faltas"] == 0
    assert alunos[2]["total_faltas"] == 3
    assert alunos[2]["limite_faltas"] == 15
    assert alunos[2]["percentual_faltas"] == 5.0
    assert alunos[2]["excedeu_limite"] is False


async def test_editar_o_mesmo_dia_atualiza_sem_duplicar(client, cenario_frequencia):
    como(10)
    await client.put(URL.format(1), json=corpo("2026-10-13", 3, {2: 3}))
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {2: 1}))
    assert r.status_code == 200
    assert por_matricula(r)[2]["total_faltas"] == 1


async def test_soma_faltas_de_dias_diferentes(client, cenario_frequencia):
    como(10)
    await client.put(URL.format(1), json=corpo("2026-10-13", 3, {2: 3}))
    r = await client.put(URL.format(1), json=corpo("2026-10-14", 2, {2: 2}))
    aluno = por_matricula(r)[2]
    assert aluno["total_faltas"] == 5
    assert aluno["percentual_faltas"] == 8.33


async def test_marca_quando_excede_o_limite(client, cenario_frequencia):
    como(10)
    for dia in range(1, 5):
        r = await client.put(URL.format(1), json=corpo(f"2026-10-0{dia}", 4, {2: 4}))
    aluno = por_matricula(r)[2]
    assert aluno["total_faltas"] == 16
    assert aluno["excedeu_limite"] is True


async def test_aluno_nao_pode_lancar_faltas(client, cenario_frequencia):
    como(1)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {1: 0}))
    assert r.status_code == 403


async def test_professor_de_outra_turma_recebe_403(client, cenario_frequencia):
    como(11)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {1: 0}))
    assert r.status_code == 403


async def test_sem_token_retorna_401(client, cenario_frequencia):
    app.dependency_overrides.pop(get_current_user_id)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {1: 0}))
    assert r.status_code == 401


async def test_faltas_maiores_que_as_aulas_do_dia_retorna_422(client, cenario_frequencia):
    como(10)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 2, {2: 3}))
    assert r.status_code == 422


async def test_matricula_de_outra_turma_retorna_422(client, cenario_frequencia):
    como(10)
    r = await client.put(URL.format(1), json=corpo("2026-10-13", 3, {3: 1}))
    assert r.status_code == 422


async def test_turma_inexistente_retorna_404(client, cenario_frequencia):
    como(10)
    r = await client.put(URL.format(99), json=corpo("2026-10-13", 3, {1: 0}))
    assert r.status_code == 404
