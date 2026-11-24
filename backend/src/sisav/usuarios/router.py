from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.service import nome_do_curso
from sisav.auth.dependencies import get_current_user_id
from sisav.core.db import get_db
from sisav.usuarios.models import Aluno, Usuario
from sisav.usuarios.schemas import ContatoUpdateRequest, PerfilResponse

router = APIRouter(prefix="/usuarios", tags=["Usuário"])

async def montar_perfil(usuario: Usuario, db: AsyncSession) -> PerfilResponse:
    aluno = await db.get(Aluno, usuario.id)
    curso = await nome_do_curso(aluno.curso_id, db) if aluno is not None else None
    return PerfilResponse(
        nome=usuario.nome,
        matricula=usuario.nome_de_usuario,
        curso=curso,
        email_institucional=f"{usuario.nome_de_usuario}@uem.br",
        foto_url=f"/uploads/{usuario.foto_perfil}" if usuario.foto_perfil else None,
        telefone=usuario.telefone,
        email_alternativo=usuario.email_alternativo,
    )

@router.get("/me/perfil", response_model=PerfilResponse)
async def obter_perfil(
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)]
) -> PerfilResponse:

    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")
    return await montar_perfil(usuario, db)

@router.patch("/me/contato", response_model=PerfilResponse)
async def atualiza_contato(
    dados: ContatoUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    usuario_id: Annotated[int, Depends(get_current_user_id)],
) -> PerfilResponse:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado.")

    campos = dados.model_fields_set
    if "telefone" in campos:
        usuario.telefone = dados.telefone
    if "email_alternativo" in campos:
        usuario.email_alternativo = dados.email_alternativo

    await db.commit()
    await db.refresh(usuario)
    return await montar_perfil(usuario, db)
