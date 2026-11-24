from sqlalchemy.ext.asyncio import AsyncSession

from sisav.academico.models import Curso


async def nome_do_curso(
    db: AsyncSession,
    curso_id: int | None
) -> str | None:
    if curso_id is None:
        return None

    curso = await db.get(Curso, curso_id)
    return curso.nome if curso is not None else None