from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import (
    Avaliacao,
    ConsolidacaoAluno,
    Disciplina,
    Matricula,
    Nota,
    RegistroFrequencia,
)
from sisav.academico.schemas.avaliacoes import (
    ConsolidacaoResponse,
    ConsolidacaoTurmaResponse,
)
from sisav.academico.services.agregacao import (
    criterios_da_matricula,
    exame_da_turma,
    folhas_de_nota,
    valor_da_nota,
)
from sisav.academico.services.calculo import calcular_situacao, media_pre_exame
from sisav.academico.services.frequencia import excedeu_limite, limite_de_faltas
from sisav.academico.services.permissoes import turma_do_professor, turma_para_leitura
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db

router = APIRouter(prefix="/avaliacao-frequencia", tags=["Avaliação e Frequência"])


@router.post(
    "/turmas/{turma_id}/fechar",
    response_model=ConsolidacaoTurmaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def fechar_turma(
    turma_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor_id: Annotated[int, Depends(get_current_user_id)],
) -> ConsolidacaoTurmaResponse:
    turma = await turma_do_professor(turma_id, professor_id, db)
    carga_horaria = await db.scalar(
        select(Disciplina.carga_horaria).where(Disciplina.id == turma.disciplina_id)
    )
    matriculas = (
        await db.scalars(
            select(Matricula).where(Matricula.turma_id == turma_id).order_by(Matricula.id)
        )
    ).all()
    avaliacoes = (
        await db.scalars(
            select(Avaliacao).where(Avaliacao.turma_id == turma_id).order_by(Avaliacao.id)
        )
    ).all()
    folhas = folhas_de_nota(avaliacoes)
    if not matriculas or not folhas:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Turma sem avaliações instanciadas."
        )

    matricula_ids = [matricula.id for matricula in matriculas]
    avaliacao_ids = [avaliacao.id for avaliacao in avaliacoes]
    notas_por_chave = {
        (nota.matricula_id, nota.avaliacao_id): nota
        for nota in (
            await db.scalars(
                select(Nota).where(
                    Nota.matricula_id.in_(matricula_ids),
                    Nota.avaliacao_id.in_(avaliacao_ids),
                )
            )
        ).all()
    }
    faltas_por_matricula = {
        matricula_id: int(total)
        for matricula_id, total in (
            await db.execute(
                select(
                    RegistroFrequencia.matricula_id, func.sum(RegistroFrequencia.faltas)
                )
                .where(RegistroFrequencia.matricula_id.in_(matricula_ids))
                .group_by(RegistroFrequencia.matricula_id)
            )
        ).all()
    }

    exame = exame_da_turma(avaliacoes)
    limite = limite_de_faltas(carga_horaria)
    consolidacoes: list[ConsolidacaoAluno] = []
    for matricula in matriculas:
        faltantes = [
            folha.codigo
            for folha in folhas
            if valor_da_nota(notas_por_chave, matricula.id, folha.id) is None
        ]
        if faltantes:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                f"Matrícula {matricula.id} sem nota em: {', '.join(faltantes)}.",
            )

        criterios = criterios_da_matricula(
            avaliacoes, notas_por_chave, matricula.id
        )
        if not criterios:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Não há critérios com nota para consolidar."
            )
        media_pre = media_pre_exame(criterios)
        nota_exame = (
            valor_da_nota(notas_por_chave, matricula.id, exame.id)
            if exame is not None
            else None
        )
        total_faltas = faltas_por_matricula.get(matricula.id, 0)
        resultado = calcular_situacao(
            media_pre,
            excedeu_limite=excedeu_limite(total_faltas, carga_horaria),
            nota_exame=nota_exame,
        )
        consolidacoes.append(
            ConsolidacaoAluno(
                turma_id=turma_id,
                matricula_id=matricula.id,
                media_pre_exame=media_pre,
                nota_exame=nota_exame,
                media_final=resultado.media_final,
                total_faltas=total_faltas,
                limite_faltas=limite,
                situacao=resultado.situacao.value,
            )
        )

    turma.fechada_em = datetime.now(UTC)
    turma.fechada_por = professor_id
    db.add_all(consolidacoes)
    await db.commit()

    return ConsolidacaoTurmaResponse(
        turma_id=turma_id,
        fechada_em=turma.fechada_em,
        consolidacoes=[
            ConsolidacaoResponse.model_validate(item) for item in consolidacoes
        ],
    )


@router.get(
    "/turmas/{turma_id}/consolidacao",
    response_model=ConsolidacaoTurmaResponse,
)
async def obter_consolidacao(
    turma_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> ConsolidacaoTurmaResponse:
    turma = await turma_para_leitura(turma_id, usuario_id, db)
    registros = (
        await db.scalars(
            select(ConsolidacaoAluno)
            .where(ConsolidacaoAluno.turma_id == turma_id)
            .order_by(ConsolidacaoAluno.id)
        )
    ).all()
    return ConsolidacaoTurmaResponse(
        turma_id=turma.id,
        fechada_em=turma.fechada_em,
        consolidacoes=[
            ConsolidacaoResponse.model_validate(item) for item in registros
        ],
    )
