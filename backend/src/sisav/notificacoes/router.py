from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.notificacoes.models import Notificacao
from sisav.notificacoes.schemas import (
    ListaNotificacoesResponse,
    MarcarLidasRequest,
    MarcarLidasResponse,
    NotificacaoResponse,
)
from sisav.usuarios.models import Perfil, Usuario

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("/aluno", response_model=ListaNotificacoesResponse)
async def listar_notificacoes_aluno(
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> ListaNotificacoesResponse:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None or usuario.perfil != Perfil.ALUNO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para alunos.",
        )

    query = (
        select(Notificacao)
        .where(Notificacao.usuario_id == usuario_id)
        .order_by(Notificacao.criada_em.desc(), Notificacao.id.desc())
    )
    itens = (await db.execute(query)).scalars().all()
    nao_lidas = sum(1 for item in itens if not item.lida)

    return ListaNotificacoesResponse(
        nao_lidas=nao_lidas,
        notificacoes=[NotificacaoResponse.model_validate(item) for item in itens],
    )


@router.patch("/marcar-lidas", response_model=MarcarLidasResponse)
async def marcar_notificacoes_lidas(
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
    payload: Annotated[MarcarLidasRequest | None, Body()] = None,
) -> MarcarLidasResponse:
    stmt = (
        update(Notificacao)
        .where(Notificacao.usuario_id == usuario_id)
        .where(Notificacao.lida.is_(False))
    )

    if payload and payload.notificacao_ids:
        stmt = stmt.where(Notificacao.id.in_(payload.notificacao_ids))

    result = await db.execute(stmt.values(lida=True))
    await db.commit()

    return MarcarLidasResponse(atualizadas=result.rowcount or 0)
