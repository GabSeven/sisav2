from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sisav.academico.calculo import para_centesimos
from sisav.academico.models import CriterioAvaliacao, Disciplina, SubcriterioAvaliacao
from sisav.academico.template_schemas import (
    CriterioResponse,
    SalvarTemplateRequest,
    SubcriterioResponse,
    TemplateResponse,
)
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Perfil, Usuario

router = APIRouter(prefix="/disciplinas", tags=["Acadêmico"])


async def exigir_gestor(
    usuario_id: int, db: AsyncSession
) -> None:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    if usuario.perfil != Perfil.GESTOR:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Acesso restrito a gestores."
        )


async def montar_resposta(disciplina: Disciplina, db: AsyncSession) -> TemplateResponse:
    criterios = (
        await db.scalars(
            select(CriterioAvaliacao)
            .where(CriterioAvaliacao.disciplina_id == disciplina.id)
            .options(selectinload(CriterioAvaliacao.subcriterios))
            .order_by(CriterioAvaliacao.ordem)
        )
    ).all()
    return TemplateResponse(
        disciplina_id=disciplina.id,
        disciplina=disciplina.nome,
        criterios=[
            CriterioResponse(
                id=criterio.id,
                ordem=criterio.ordem,
                nome=criterio.nome,
                peso=criterio.peso,
                subcriterios=[
                    SubcriterioResponse.model_validate(sub)
                    for sub in sorted(criterio.subcriterios, key=lambda item: item.ordem)
                ],
            )
            for criterio in criterios
        ],
    )


@router.get("/{disciplina_id}/criterios", response_model=TemplateResponse)
async def obter_criterios(
    disciplina_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> TemplateResponse:
    await exigir_gestor(usuario_id, db)
    disciplina = await db.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Disciplina não encontrada.")
    return await montar_resposta(disciplina, db)


@router.put("/{disciplina_id}/criterios", response_model=TemplateResponse)
async def salvar_criterios(
    disciplina_id: int,
    dados: SalvarTemplateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> TemplateResponse:
    await exigir_gestor(usuario_id, db)
    disciplina = await db.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Disciplina não encontrada.")

    validados = []
    for criterio in dados.criterios:
        peso = para_centesimos(criterio.peso)
        if peso <= 0:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Peso deve ser maior que zero."
            )
        subcriterios = []
        for sub in criterio.subcriterios:
            peso_sub = para_centesimos(sub.peso)
            if peso_sub <= 0:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "Peso deve ser maior que zero.",
                )
            subcriterios.append((sub, peso_sub))
        validados.append((criterio, peso, subcriterios))

    existentes = (
        await db.scalars(
            select(CriterioAvaliacao.id).where(
                CriterioAvaliacao.disciplina_id == disciplina_id
            )
        )
    ).all()
    if existentes:
        await db.execute(
            delete(SubcriterioAvaliacao).where(
                SubcriterioAvaliacao.criterio_id.in_(existentes)
            )
        )
        await db.execute(
            delete(CriterioAvaliacao).where(CriterioAvaliacao.id.in_(existentes))
        )

    for criterio, peso, subcriterios in validados:
        novo = CriterioAvaliacao(
            disciplina_id=disciplina_id,
            ordem=criterio.ordem,
            nome=criterio.nome,
            peso=peso,
        )
        db.add(novo)
        await db.flush()
        for sub, peso_sub in subcriterios:
            db.add(
                SubcriterioAvaliacao(
                    criterio_id=novo.id,
                    ordem=sub.ordem,
                    nome=sub.nome,
                    peso=peso_sub,
                )
            )

    await db.commit()
    return await montar_resposta(disciplina, db)
