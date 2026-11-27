from collections.abc import Sequence
from datetime import date, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import Disciplina, Matricula, RegistroFrequencia, Turma
from sisav.academico.schemas.frequencia import (
    AlunoFrequenciaResponse,
    FaltasTurmaResponse,
    RegistrarFaltasRequest,
)
from sisav.academico.services.frequencia import (
    excedeu_limite,
    limite_de_faltas,
    percentual_de_faltas,
)
from sisav.academico.services.permissoes import get_professor_atual, turma_para_leitura
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Usuario

router = APIRouter(prefix="/avaliacao-frequencia", tags=["Avaliação e Frequência"])


def _montar_alunos(
    matriculas: Sequence[tuple[int, str]],
    totais: dict[int, int],
    no_bloco: dict[int, int],
    carga_horaria: int,
) -> list[AlunoFrequenciaResponse]:
    alunos: list[AlunoFrequenciaResponse] = []
    for matricula_id, nome in matriculas:
        total = totais.get(matricula_id, 0)
        alunos.append(
            AlunoFrequenciaResponse(
                matricula_id=matricula_id,
                nome_aluno=nome,
                total_faltas=total,
                faltas_no_bloco=no_bloco.get(matricula_id, 0),
                limite_faltas=limite_de_faltas(carga_horaria),
                percentual_faltas=percentual_de_faltas(total, carga_horaria),
                excedeu_limite=excedeu_limite(total, carga_horaria),
            )
        )
    return alunos


@router.put("/turmas/{turma_id}/faltas", response_model=FaltasTurmaResponse)
async def registrar_faltas(
    turma_id: int,
    dados: RegistrarFaltasRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor: Annotated[Usuario, Depends(get_professor_atual)],
) -> FaltasTurmaResponse:
    linha = (
        await db.execute(
            select(
                Turma.professor_id,
                Turma.horario_inicio,
                Turma.horario_fim,
                Turma.fechada_em,
                Disciplina.carga_horaria,
            )
            .join(Disciplina, Turma.disciplina_id == Disciplina.id)
            .where(Turma.id == turma_id)
        )
    ).first()
    if linha is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    professor_da_turma, inicio_turma, fim_turma, fechada_em, carga_horaria = linha
    if professor_da_turma != professor.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    if fechada_em is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Turma já fechada.")
    if dados.horario_inicio != inicio_turma or dados.horario_fim != fim_turma:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "O bloco informado não corresponde ao horário da turma.",
        )

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
                    RegistroFrequencia.horario_inicio == dados.horario_inicio,
                    RegistroFrequencia.horario_fim == dados.horario_fim,
                )
            )
        ).all()
    }
    for item in dados.registros:
        registro = existentes.get(item.matricula_id)
        if registro is None:
            db.add(
                RegistroFrequencia(
                    matricula_id=item.matricula_id,
                    data=dados.data,
                    horario_inicio=dados.horario_inicio,
                    horario_fim=dados.horario_fim,
                    faltas=item.faltas,
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

    no_bloco = {item.matricula_id: item.faltas for item in dados.registros}
    return FaltasTurmaResponse(
        turma_id=turma_id,
        data=dados.data,
        horario_inicio=dados.horario_inicio,
        horario_fim=dados.horario_fim,
        alunos=_montar_alunos(matriculas, totais, no_bloco, carga_horaria),
    )


@router.get("/turmas/{turma_id}/faltas", response_model=FaltasTurmaResponse)
async def consultar_faltas(
    turma_id: int,
    data: Annotated[date, Query()],
    horario_inicio: Annotated[time, Query()],
    horario_fim: Annotated[time, Query()],
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> FaltasTurmaResponse:
    turma = await turma_para_leitura(turma_id, usuario_id, db)
    if turma.horario_inicio != horario_inicio or turma.horario_fim != horario_fim:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "O bloco informado não corresponde ao horário da turma.",
        )

    matriculas = (
        await db.execute(
            select(Matricula.id, Usuario.nome)
            .join(Usuario, Matricula.aluno_id == Usuario.id)
            .where(Matricula.turma_id == turma.id)
            .order_by(Usuario.nome)
        )
    ).all()
    ids_da_turma = [matricula_id for matricula_id, _ in matriculas]
    if not ids_da_turma:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma sem matrículas.")

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
    no_bloco = {
        matricula_id: faltas
        for matricula_id, faltas in (
            await db.execute(
                select(RegistroFrequencia.matricula_id, RegistroFrequencia.faltas).where(
                    RegistroFrequencia.matricula_id.in_(ids_da_turma),
                    RegistroFrequencia.data == data,
                    RegistroFrequencia.horario_inicio == horario_inicio,
                    RegistroFrequencia.horario_fim == horario_fim,
                )
            )
        ).all()
    }
    carga_horaria = await db.scalar(
        select(Disciplina.carga_horaria).where(Disciplina.id == turma.disciplina_id)
    )
    return FaltasTurmaResponse(
        turma_id=turma.id,
        data=data,
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        alunos=_montar_alunos(matriculas, totais, no_bloco, carga_horaria),
    )
