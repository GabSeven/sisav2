from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sisav.core.config import get_settings

# A nossa Base para os modelos
class Base(DeclarativeBase):
    pass

# Cria o "motor" assíncrono que liga ao PostgreSQL
engine = create_async_engine(get_settings().database_url, echo=True)

# Cria a fábrica de sessões
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Função que vai ser injetada nas rotas do FastAPI (Dependency)
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session