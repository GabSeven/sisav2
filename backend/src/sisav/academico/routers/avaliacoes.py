from collections import defaultdict
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sisav.academico.models import (
    Avaliacao,
    ConsolidacaoAluno,
    CriterioAvaliacao,
    Disciplina,
    Matricula,
    Nota,
    RegistroFrequencia,
    TipoAvaliacao,
    Turma,
)
from sisav.academico.schemas.avaliacoes import (
    AvaliacaoResponse,
    BoletimResponse,
    BoletimTurmaResponse,
    CriarAvaliacaoRequest,
    EditarAvaliacaoRequest,
    LancarNotasRequest,
    NotaAvaliacaoResponse,
    NotaResponse,
    NotasLancadasResponse,
)
from sisav.academico.services.agregacao import (
    criterios_da_matricula,
    exame_da_turma,
    valor_da_nota,
)
from sisav.academico.services.calculo import (
    calcular_situacao,
    media_pre_exame,
    para_centesimos,
)
from sisav.academico.services.frequencia import excedeu_limite, limite_de_faltas
from sisav.academico.services.permissoes import turma_do_professor
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Perfil, Usuario

router = APIRouter(prefix="/avaliacao-frequencia", tags=["Avaliação e Frequência"])


@router.post(
    "/turmas/{turma_id}/avaliacoes",
    response_model=list[AvaliacaoResponse],
    status_code=status.HTTP_201_CREATED,
)
async def criar_avaliacoes(
    turma_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor_id: Annotated[int, Depends(get_current_user_id)],
    dados: Annotated[CriarAvaliacaoRequest | None, Body()] = None,
) -> list[AvaliacaoResponse]:
    turma = await turma_do_professor(turma_id, professor_id, db)
    modo = dados.tipo if dados is not None else "template"

    if modo == "exame":
        existente = await db.scalar(
            select(Avaliacao.id).where(
                Avaliacao.turma_id == turma_id,
                Avaliacao.tipo == TipoAvaliacao.EXAME.value,
            )
        )
        if existente is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Exame já criado para esta turma.")
        exame = Avaliacao(
            turma_id=turma_id,
            nome="Exame Final",
            codigo="EX",
            tipo=TipoAvaliacao.EXAME.value,
            peso=100,
        )
        db.add(exame)
        await db.commit()
        await db.refresh(exame)
        return [AvaliacaoResponse.model_validate(exame)]

    existente = await db.scalar(
        select(Avaliacao.id).where(Avaliacao.turma_id == turma_id).limit(1)
    )
    if existente is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Turma já possui avaliações instanciadas."
        )

    criterios = (
        await db.scalars(
            select(CriterioAvaliacao)
            .where(CriterioAvaliacao.disciplina_id == turma.disciplina_id)
            .options(selectinload(CriterioAvaliacao.subcriterios))
            .order_by(CriterioAvaliacao.ordem)
        )
    ).all()
    if not criterios:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Disciplina sem template de critérios."
        )

    criadas: list[Avaliacao] = []
    for criterio in criterios:
        pai = Avaliacao(
            turma_id=turma_id,
            nome=criterio.nome,
            codigo=str(criterio.ordem),
            tipo=TipoAvaliacao.CRITERIO.value,
            peso=criterio.peso,
        )
        db.add(pai)
        await db.flush()
        criadas.append(pai)

        subcriterios = sorted(criterio.subcriterios, key=lambda sub: sub.ordem)
        if subcriterios:
            for sub in subcriterios:
                folha = Avaliacao(
                    turma_id=turma_id,
                    pai_id=pai.id,
                    nome=sub.nome,
                    codigo=f"{criterio.ordem}-{sub.ordem}",
                    tipo=TipoAvaliacao.AVALIACAO.value,
                    peso=sub.peso,
                )
                db.add(folha)
                criadas.append(folha)
        else:
            folha = Avaliacao(
                turma_id=turma_id,
                pai_id=pai.id,
                nome=criterio.nome,
                codigo=f"{criterio.ordem}-1",
                tipo=TipoAvaliacao.AVALIACAO.value,
                peso=100,
            )
            db.add(folha)
            criadas.append(folha)

    await db.commit()
    return [AvaliacaoResponse.model_validate(item) for item in criadas]


@router.patch(
    "/turmas/{turma_id}/avaliacoes/{avaliacao_id}",
    response_model=AvaliacaoResponse,
)
async def editar_avaliacao(
    turma_id: int,
    avaliacao_id: int,
    dados: EditarAvaliacaoRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor_id: Annotated[int, Depends(get_current_user_id)],
) -> AvaliacaoResponse:
    await turma_do_professor(turma_id, professor_id, db)
    avaliacao = await db.get(Avaliacao, avaliacao_id)
    if avaliacao is None or avaliacao.turma_id != turma_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Avaliação não encontrada.")

    if avaliacao.tipo == TipoAvaliacao.EXAME.value and dados.peso is not None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "O peso do exame é fixo em 1,0."
        )

    if dados.nome is not None:
        avaliacao.nome = dados.nome
    if dados.peso is not None:
        peso = para_centesimos(dados.peso)
        if peso <= 0:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Peso deve ser maior que zero."
            )
        avaliacao.peso = peso

    await db.commit()
    await db.refresh(avaliacao)
    return AvaliacaoResponse.model_validate(avaliacao)


@router.put(
    "/turmas/{turma_id}/notas",
    response_model=NotasLancadasResponse,
)
async def lancar_notas(
    turma_id: int,
    dados: LancarNotasRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    professor_id: Annotated[int, Depends(get_current_user_id)],
) -> NotasLancadasResponse:
    await turma_do_professor(turma_id, professor_id, db)
    avaliacao = await db.get(Avaliacao, dados.avaliacao_id)
    if avaliacao is None or avaliacao.turma_id != turma_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Avaliação não encontrada.")
    if avaliacao.tipo == TipoAvaliacao.CRITERIO.value:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Critérios não recebem nota."
        )

    ids = [item.matricula_id for item in dados.registros]
    validas = set(
        (
            await db.scalars(
                select(Matricula.id).where(
                    Matricula.turma_id == turma_id,
                    Matricula.id.in_(ids),
                )
            )
        ).all()
    )
    invalidas = sorted(set(ids) - validas)
    if invalidas:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Matrículas que não pertencem à turma: {invalidas}.",
        )

    existentes = {
        nota.matricula_id: nota
        for nota in (
            await db.scalars(
                select(Nota).where(
                    Nota.avaliacao_id == avaliacao.id,
                    Nota.matricula_id.in_(ids),
                )
            )
        ).all()
    }

    salvos: list[Nota] = []
    for item in dados.registros:
        nota = existentes.get(item.matricula_id)
        if nota is None:
            nota = Nota(
                avaliacao_id=avaliacao.id,
                matricula_id=item.matricula_id,
                valor=para_centesimos(item.valor),
            )
            db.add(nota)
        else:
            nota.valor = para_centesimos(item.valor)
        salvos.append(nota)

    await db.commit()
    return NotasLancadasResponse(
        avaliacao_id=avaliacao.id,
        registros=[
            NotaResponse(matricula_id=nota.matricula_id, valor=nota.valor)
            for nota in salvos
        ],
    )


@router.get("/alunos/me/boletim", response_model=BoletimResponse)
async def obter_boletim(
    db: Annotated[AsyncSession, Depends(get_db)],
    aluno_id: Annotated[int, Depends(get_current_user_id)],
    ano: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    semestre: Annotated[int | None, Query(ge=1, le=2)] = None,
) -> BoletimResponse:
    usuario = await db.get(Usuario, aluno_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    if usuario.perfil != Perfil.ALUNO:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Acesso permitido apenas para alunos."
        )

    hoje = date.today()
    ano = ano or hoje.year
    semestre = semestre or (1 if hoje.month <= 6 else 2)
    chave_semestre = f"{ano}.{semestre}"

    linhas = (
        await db.execute(
            select(Matricula, Turma, Disciplina)
            .join(Turma, Matricula.turma_id == Turma.id)
            .join(Disciplina, Turma.disciplina_id == Disciplina.id)
            .where(
                Matricula.aluno_id == aluno_id,
                Matricula.ano_letivo == ano,
                Turma.semestre == chave_semestre,
            )
            .order_by(Turma.id, Matricula.id)
        )
    ).all()
    if not linhas:
        return BoletimResponse(ano=ano, semestre=semestre, turmas=[])

    turma_ids = sorted({turma.id for _, turma, _ in linhas})
    matricula_ids = sorted({matricula.id for matricula, _, _ in linhas})
    avaliacoes = (
        await db.scalars(
            select(Avaliacao)
            .where(Avaliacao.turma_id.in_(turma_ids))
            .order_by(Avaliacao.id)
        )
    ).all()
    por_turma: dict[int, list[Avaliacao]] = defaultdict(list)
    for avaliacao in avaliacoes:
        por_turma[avaliacao.turma_id].append(avaliacao)

    notas_por_chave: dict[tuple[int, int], Nota] = {}
    if avaliacoes:
        ids_avaliacoes = [avaliacao.id for avaliacao in avaliacoes]
        notas = (
            await db.scalars(
                select(Nota).where(
                    Nota.matricula_id.in_(matricula_ids),
                    Nota.avaliacao_id.in_(ids_avaliacoes),
                )
            )
        ).all()
        notas_por_chave = {(nota.matricula_id, nota.avaliacao_id): nota for nota in notas}

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
    snapshots = {
        (item.turma_id, item.matricula_id): item
        for item in (
            await db.scalars(
                select(ConsolidacaoAluno).where(
                    ConsolidacaoAluno.turma_id.in_(turma_ids),
                    ConsolidacaoAluno.matricula_id.in_(matricula_ids),
                )
            )
        ).all()
    }

    turmas: list[BoletimTurmaResponse] = []
    for matricula, turma, disciplina in linhas:
        avaliacoes_da_turma = por_turma[turma.id]
        itens: list[NotaAvaliacaoResponse] = []
        for avaliacao in avaliacoes_da_turma:
            nota = notas_por_chave.get((matricula.id, avaliacao.id))
            itens.append(
                NotaAvaliacaoResponse(
                    codigo=avaliacao.codigo,
                    nome=avaliacao.nome,
                    tipo=TipoAvaliacao(avaliacao.tipo),
                    peso=avaliacao.peso,
                    valor=nota.valor if nota is not None else None,
                )
            )

        snapshot = snapshots.get((turma.id, matricula.id))
        if turma.fechada_em is not None and snapshot is None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Consolidação da turma não encontrada."
            )

        if snapshot is not None:
            media_pre = snapshot.media_pre_exame
            nota_exame = snapshot.nota_exame
            media_final = snapshot.media_final
            total_faltas = snapshot.total_faltas
            limite = snapshot.limite_faltas
            situacao = snapshot.situacao
        else:
            criterios = criterios_da_matricula(
                avaliacoes_da_turma, notas_por_chave, matricula.id
            )
            media_pre = media_pre_exame(criterios) if criterios else None
            exame = exame_da_turma(avaliacoes_da_turma)
            nota_exame = (
                valor_da_nota(notas_por_chave, matricula.id, exame.id)
                if exame is not None
                else None
            )
            total_faltas = faltas_por_matricula.get(matricula.id, 0)
            limite = limite_de_faltas(disciplina.carga_horaria)
            if media_pre is None:
                media_final = None
                situacao = None
            else:
                resultado = calcular_situacao(
                    media_pre,
                    excedeu_limite=excedeu_limite(
                        total_faltas, disciplina.carga_horaria
                    ),
                    nota_exame=nota_exame,
                )
                media_final = resultado.media_final
                situacao = resultado.situacao

        turmas.append(
            BoletimTurmaResponse(
                turma_id=turma.id,
                codigo_turma=turma.codigo,
                disciplina=disciplina.nome,
                ano_letivo=matricula.ano_letivo,
                semestre=turma.semestre,
                avaliacoes=itens,
                media_pre_exame=media_pre,
                nota_exame=nota_exame,
                media_final=media_final,
                total_faltas=total_faltas,
                limite_faltas=limite,
                situacao=situacao,
            )
        )

    return BoletimResponse(ano=ano, semestre=semestre, turmas=turmas)
