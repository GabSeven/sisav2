import pytest

pytestmark = pytest.mark.asyncio


async def test_retorna_aulas_do_semestre_ordenadas(client, cenario):
    r = await client.get("/api/v1/academico/alunos/me/horario?semestre=2026.1")
    assert r.status_code == 200
    aulas = r.json()["aulas"]
    assert [a["dia_semana"] for a in aulas] == ["segunda", "quarta"]
    assert aulas[0]["codigo_turma"] == "B"
    assert aulas[0]["sala"] == "I-12"


async def test_filtra_por_semestre(client, cenario):
    r = await client.get("/api/v1/academico/alunos/me/horario?semestre=2026.2")
    assert [a["dia_semana"] for a in r.json()["aulas"]] == ["sexta"]


async def test_semestre_sem_matricula_retorna_lista_vazia(client, cenario):
    r = await client.get("/api/v1/academico/alunos/me/horario?semestre=2025.1")
    assert r.status_code == 200
    assert r.json()["aulas"] == []


async def test_semestre_invalido_retorna_422(client, cenario):
    r = await client.get("/api/v1/academico/alunos/me/horario?semestre=2026-1")
    assert r.status_code == 422