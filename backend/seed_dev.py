import asyncio

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sisav.academico.models import Disciplina, Matricula, Turma
from sisav.core.config import get_settings
from sisav.usuarios.models import Perfil, Usuario


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


async def main() -> None:
    engine = create_async_engine(get_settings().database_url)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        existe = await db.scalar(
            select(Usuario).where(Usuario.nome_de_usuario == "aluno.teste")
        )
        if existe:
            print("Seed já aplicado, aluno id =", existe.id)
            return

        aluno = Usuario(
            nome="Aluno Teste",
            nome_de_usuario="aluno.teste",
            senha_hash=hash_senha("senha123"),
            perfil=Perfil.ALUNO,
        )
        professor = Usuario(
            nome="Professor Teste",
            nome_de_usuario="prof.teste",
            senha_hash=hash_senha("senha123"),
            perfil=Perfil.PROFESSOR,
        )
        calculo = Disciplina(nome="Cálculo I", carga_horaria=90)
        construcao = Disciplina(nome="Construção de Software", carga_horaria=60)
        db.add_all([aluno, professor, calculo, construcao])
        await db.flush()  # gera os ids

        turmas = [
            Turma(codigo="A", semestre="2026.1", sala="B-101", dia_semana="segunda",
                  horario_inicio="08:00", horario_fim="09:40",
                  disciplina_id=calculo.id, professor_id=professor.id),
            Turma(codigo="B", semestre="2026.1", sala="I-12", dia_semana="quarta",
                  horario_inicio="10:00", horario_fim="11:40",
                  disciplina_id=construcao.id, professor_id=professor.id),
            Turma(codigo="A", semestre="2026.2", sala="B-103", dia_semana="sexta",
                  horario_inicio="08:00", horario_fim="09:40",
                  disciplina_id=construcao.id, professor_id=professor.id),
        ]
        db.add_all(turmas)
        await db.flush()

        db.add_all(
            Matricula(aluno_id=aluno.id, turma_id=t.id, ano_letivo=2026) for t in turmas
        )
        await db.commit()
        print("Seed aplicado. aluno id =", aluno.id)

    await engine.dispose()


asyncio.run(main())