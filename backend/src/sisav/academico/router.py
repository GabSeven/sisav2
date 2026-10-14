from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import Disciplina, Matricula, Turma
from sisav.academico.schemas import AulaHorarioResponse, GradeHorariaResponse
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db

router = APIRouter(prefix="/academico", tags=["Acadêmico"])

ORDEM_DIAS = {
    "segunda": 1, "terca": 2, "quarta": 3,
    "quinta": 4, "sexta": 5, "sabado": 6, "domingo": 7,
}


def semestre_atual() -> str:
    hoje = date.today()
    return f"{hoje.year}.{1 if hoje.month <= 6 else 2}"


@router.get("/alunos/me/horario", response_model=GradeHorariaResponse)
async def obter_horario_aluno(
    db: Annotated[AsyncSession, Depends(get_db)],
    aluno_id: Annotated[int, Depends(get_current_user_id)],
    semestre: Annotated[str | None, Query(pattern=r"^\d{4}\.[12]$")] = None,
) -> GradeHorariaResponse:
    semestre = semestre or semestre_atual()
    ordem_dia = case(ORDEM_DIAS, value=Turma.dia_semana, else_=99)

    query = (
        select(Turma, Disciplina.nome.label("nome_disciplina"))
        .join(Matricula, Matricula.turma_id == Turma.id)
        .join(Disciplina, Turma.disciplina_id == Disciplina.id)
        .where(Matricula.aluno_id == aluno_id)
        .where(Turma.semestre == semestre)
        .order_by(ordem_dia, Turma.horario_inicio)
    )

    rows = (await db.execute(query)).all()

    aulas = [
        AulaHorarioResponse(
            id_turma=turma.id,
            codigo_turma=turma.codigo,
            nome_disciplina=nome_disciplina,
            sala=turma.sala,
            dia_semana=turma.dia_semana,
            horario_inicio=turma.horario_inicio,
            horario_fim=turma.horario_fim,
        )
        for turma, nome_disciplina in rows
    ]
    return GradeHorariaResponse(semestre=semestre, aulas=aulas)


@router.get("/professores/me/turmas", response_model=GradeHorariaResponse)
async def obter_turmas_professor(
    db: Annotated[AsyncSession, Depends(get_db)],
    professor_id: Annotated[int, Depends(get_current_user_id)],
    semestre: Annotated[str, Query(pattern=r"^\d{4}\.[12]$")] = "2026.1",
) -> GradeHorariaResponse:
    ordem_dia = case(ORDEM_DIAS, value=Turma.dia_semana, else_=99)
    
    query = (
        select(Turma, Disciplina.nome.label("nome_disciplina"))
        .join(Disciplina, Turma.disciplina_id == Disciplina.id)
        .where(Turma.professor_id == professor_id)
        .where(Turma.semestre == semestre)
        .order_by(ordem_dia, Turma.horario_inicio)
    )

    rows = (await db.execute(query)).all()

    turmas_lista = [
        AulaHorarioResponse(
            id_turma=turma.id,
            codigo_turma=turma.codigo,
            nome_disciplina=nome_disciplina,
            sala=turma.sala,
            dia_semana=turma.dia_semana,
            horario_inicio=turma.horario_inicio,
            horario_fim=turma.horario_fim,
        )
        for turma, nome_disciplina in rows
    ]
    
    return GradeHorariaResponse(semestre=semestre, aulas=turmas_lista)