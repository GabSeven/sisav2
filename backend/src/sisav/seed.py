import asyncio

from sqlalchemy import select

from sisav.auth.security import gerar_hash
from sisav.core.config import get_settings
from sisav.core.db import SessionLocal
from sisav.usuarios.models import Perfil, Usuario


async def seed() -> None:
    settings = get_settings()

    async with SessionLocal() as session:
        ja_existe = await session.scalar(
            select(Usuario).where(Usuario.nome_de_usuario == settings.seed_usuario)
        )

        if ja_existe is not None:
            print("Usuário de teste já existe.")
            return

        novo_usuario = Usuario(
            nome="Professor de teste",
            nome_de_usuario=settings.seed_usuario,
            senha_hash=gerar_hash(settings.seed_password),
            perfil=Perfil.PROFESSOR,
        )
        session.add(novo_usuario)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())