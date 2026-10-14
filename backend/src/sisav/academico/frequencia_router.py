from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.frequencia import excedeu_limite, limite_de_faltas, percentual_de_faltas
from sisav.academico.frequencia_schemas import (
    AlunoFrequenciaResponse,
    FaltasTurmaResponse,
    RegistrarFaltasRequest,
)
from sisav.academico.models import Disciplina, Matricula, RegistroFrequencia, Turma
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Perfil, Usuario

router = APIRouter(prefix="/avaliacao-frequencia", tags=["Avaliação e Frequência"])


async def get_professor_atual(
    usuario_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    if usuario.perfil != Perfil.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a professores.")
    return usuario


@router.put("/turmas/{turma_id}/faltas", response_model=FaltasTurmaResponse)
async def registrar_faltas(
    turma_id: int,
    dados: RegistrarFaltasRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor: Annotated[Usuario, Depends(get_professor_atual)],
) -> FaltasTurmaResponse:
    linha = (
        await db.execute(
            select(Turma.professor_id, Disciplina.carga_horaria)
            .join(Disciplina, Turma.disciplina_id == Disciplina.id)
            .where(Turma.id == turma_id)
        )
    ).first()
    if linha is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    professor_da_turma, carga_horaria = linha
    if professor_da_turma != professor.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")

    matriculas = (
        await db.execute(
            select(Matricula.id, Usuario.nome)
            .join(Usuario, Matricula.aluno_id == Usuario.id)
            .where(Matricula.turma_id == turma_id)
            .order_by(Usuario.nome)
        )
    ).all()
    ids_da_turma = [matricula_id for matricula_id, _ in matriculas]

    invalidas = sorted({r.matricula_id for r in dados.registros} - set(ids_da_turma))
    if invalidas:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Matrículas que não pertencem à turma: {invalidas}.",
        )

    existentes = {
        registro.matricula_id: registro
        for registro in (
            await db.scalars(
                select(RegistroFrequencia).where(
                    RegistroFrequencia.matricula_id.in_(ids_da_turma),
                    RegistroFrequencia.data == dados.data,
                )
            )
        ).all()
    }
    for item in dados.registros:
        registro = existentes.get(item.matricula_id)
        if registro is None:
            db.add(
                RegistroFrequencia(
                    matricula_id=item.matricula_id, data=dados.data, faltas=item.faltas
                )
            )
        else:
            registro.faltas = item.faltas
    await db.commit()

    totais = {
        matricula_id: int(total)
        for matricula_id, total in (
            await db.execute(
                select(RegistroFrequencia.matricula_id, func.sum(RegistroFrequencia.faltas))
                .where(RegistroFrequencia.matricula_id.in_(ids_da_turma))
                .group_by(RegistroFrequencia.matricula_id)
            )
        ).all()
    }

    limite = limite_de_faltas(carga_horaria)
    alunos = [
        AlunoFrequenciaResponse(
            matricula_id=matricula_id,
            nome_aluno=nome,
            total_faltas=totais.get(matricula_id, 0),
            limite_faltas=limite,
            percentual_faltas=percentual_de_faltas(totais.get(matricula_id, 0), carga_horaria),
            excedeu_limite=excedeu_limite(totais.get(matricula_id, 0), carga_horaria),
        )
        for matricula_id, nome in matriculas
    ]
    return FaltasTurmaResponse(turma_id=turma_id, data=dados.data, alunos=alunos)
