import asyncio
from sisav.core.db import get_db
from sisav.usuarios.models import Usuario, Perfil
from sisav.academico.models import Disciplina, Turma, Matricula

async def testar_banco():
    # Como get_db() é um gerador, usamos async for para pegar a sessão
    async for db in get_db():
        
        # 1. Criar Usuários
        aluno = Usuario(nome="Teste Aluno", nome_de_usuario="aluno1", senha_hash="hash", perfil=Perfil.ALUNO)
        professor = Usuario(nome="Teste Professor", nome_de_usuario="prof1", senha_hash="hash", perfil=Perfil.PROFESSOR)
        db.add_all([aluno, professor])
        await db.commit()

        # 2. Criar Disciplina
        disciplina = Disciplina(nome="Banco de Dados", carga_horaria=80)
        db.add(disciplina)
        await db.commit()

        # 3. Criar Turma
        turma = Turma(
            codigo="BD-01", semestre="2026.1", sala="Lab 1", dia_semana="segunda",
            horario_inicio="19:00", horario_fim="21:00",
            disciplina_id=disciplina.id, professor_id=professor.id
        )
        db.add(turma)
        await db.commit()

        # 4. Criar Matrícula
        matricula = Matricula(aluno_id=aluno.id, turma_id=turma.id, ano_letivo=2026)
        db.add(matricula)
        await db.commit()

        print(f"Sucesso! Aluno ID: {aluno.id}, Professor ID: {professor.id}, Turma ID: {turma.id}")
        
        break # Interrompe o loop após a primeira sessão

if __name__ == "__main__":
    asyncio.run(testar_banco())