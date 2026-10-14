import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from sisav.academico.models import Disciplina, Matricula, Turma
from sisav.auth.dependencies import get_current_user_id  # <-- Nova importação
from sisav.core.db import Base, get_db
from sisav.main import app
from sisav.usuarios.models import Perfil, Usuario


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    async def _get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user_id] = lambda: 1  # <-- Atualizado aqui
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def cenario(session_factory):
    async with session_factory() as db:
        aluno = Usuario(id=1, nome="A", nome_de_usuario="a", senha_hash="x", perfil=Perfil.ALUNO)
        outro = Usuario(id=2, nome="B", nome_de_usuario="b", senha_hash="x", perfil=Perfil.ALUNO)
        calc = Disciplina(id=1, nome="Cálculo I", carga_horaria=90)
        cs = Disciplina(id=2, nome="Construção de Software", carga_horaria=60)
        db.add_all([aluno, outro, calc, cs])
        await db.flush()
        t1 = Turma(id=1, codigo="A", semestre="2026.1", sala="B-101", dia_semana="quarta",
                   horario_inicio="10:00", horario_fim="11:40", disciplina_id=1)
        t2 = Turma(id=2, codigo="B", semestre="2026.1", sala="I-12", dia_semana="segunda",
                   horario_inicio="08:00", horario_fim="09:40", disciplina_id=2)
        t3 = Turma(id=3, codigo="A", semestre="2026.2", sala="B-103", dia_semana="sexta",
                   horario_inicio="08:00", horario_fim="09:40", disciplina_id=2)
        db.add_all([t1, t2, t3])
        await db.flush()
        db.add_all([
            Matricula(aluno_id=1, turma_id=1, ano_letivo=2026),
            Matricula(aluno_id=1, turma_id=2, ano_letivo=2026),
            Matricula(aluno_id=1, turma_id=3, ano_letivo=2026),
            Matricula(aluno_id=2, turma_id=1, ano_letivo=2026),  # outro aluno
        ])
        await db.commit()