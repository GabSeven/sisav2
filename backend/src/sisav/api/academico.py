from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from sisav.core.database import get_db
from sisav.models.academico import Turma, Disciplina, Matricula
from sisav.schemas.academico import GradeHorariaResponse, AulaHorarioResponse

router = APIRouter(prefix="/academico", tags=["Acadêmico"])

@router.get("/alunos/me/horario", response_model=GradeHorariaResponse)
async def obter_horario_aluno(
    semestre: str = "2026.1", 
    db: AsyncSession = Depends(get_db)
):
    # TODO: No futuro, pegar este ID do token JWT do usuário logado
    # Por agora, usamos um UUID genérico para não dar erro na compilação
    aluno_mock_id = UUID("00000000-0000-0000-0000-000000000000")

    # A nossa consulta SQL (SELECT ... JOIN ... WHERE)
    query = (
        select(Turma, Disciplina.nome.label("nome_disciplina"))
        .join(Matricula, Matricula.turma_id == Turma.id)
        .join(Disciplina, Turma.disciplina_id == Disciplina.id)
        .where(Matricula.aluno_id == aluno_mock_id)
        .where(Turma.semestre == semestre)
    )
    
    # Executa a query no banco de dados
    result = await db.execute(query)
    rows = result.all()

    # Formata os dados para enviar para o frontend
    aulas = []
    for turma, nome_disciplina in rows:
        aulas.append(AulaHorarioResponse(
            id_turma=turma.id,
            nome_disciplina=nome_disciplina,
            dia_semana=turma.dia_semana,
            horario_inicio=turma.horario_inicio,
            horario_fim=turma.horario_fim
        ))
    
    return GradeHorariaResponse(semestre=semestre, aulas=aulas)