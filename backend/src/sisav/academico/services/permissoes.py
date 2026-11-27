"""Verificações de acesso compartilhadas pelos routers acadêmicos."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import Turma
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Perfil, Usuario


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


async def exigir_gestor(usuario_id: int, db: AsyncSession) -> None:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    if usuario.perfil != Perfil.GESTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a gestores.")


async def turma_do_professor(
    turma_id: int, professor_id: int, db: AsyncSession
) -> Turma:
    turma = await db.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if turma.professor_id != professor_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    if turma.fechada_em is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Turma já fechada.")
    return turma


async def turma_para_leitura(
    turma_id: int, usuario_id: int, db: AsyncSession
) -> Turma:
    turma = await db.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    if usuario.perfil != Perfil.GESTOR and turma.professor_id != usuario_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Acesso restrito ao professor da turma."
        )
    return turma
