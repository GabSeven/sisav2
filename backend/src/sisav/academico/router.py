from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import Disciplina, Matricula, Turma
from sisav.academico.schemas import AulaHorarioResponse, GradeHorariaResponse
from sisav.core.db import get_db

router = APIRouter(prefix="/academico", tags=["Acadêmico"])


@router.get("/alunos/me/horario", response_model=GradeHorariaResponse)
async def obter_horario_aluno(
    db: Annotated[AsyncSession, Depends(get_db)],
    semestre: str = "2026.1",
) -> GradeHorariaResponse:
    # TODO: Obter o id a partir do token JWT de quem estiver logado.
    aluno_mock_id = 0

    query = (
        select(Turma, Disciplina.nome.label("nome_disciplina"))
        .join(Matricula, Matricula.turma_id == Turma.id)
        .join(Disciplina, Turma.disciplina_id == Disciplina.id)
        .where(Matricula.aluno_id == aluno_mock_id)
        .where(Turma.semestre == semestre)
    )

    result = await db.execute(query)
    rows = result.all()

    aulas = [
        AulaHorarioResponse(
            id_turma=turma.id,
            nome_disciplina=nome_disciplina,
            dia_semana=turma.dia_semana,
            horario_inicio=turma.horario_inicio,
            horario_fim=turma.horario_fim,
        )
        for turma, nome_disciplina in rows
    ]

    return GradeHorariaResponse(semestre=semestre, aulas=aulas)