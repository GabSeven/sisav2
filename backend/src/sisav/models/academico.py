from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from datetime import time
from sisav.core.database import Base 

class Disciplina(Base):
    __tablename__ = "disciplinas"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    carga_horaria: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relacionamento: 1 Disciplina tem Várias Turmas
    turmas: Mapped[list["Turma"]] = relationship(back_populates="disciplina")


class Turma(Base):
    __tablename__ = "turmas"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False) # Ex: "ES-A"
    semestre: Mapped[str] = mapped_column(String(10), nullable=False) # Ex: "2026.1"
    sala: Mapped[str] = mapped_column(String(50))
    dia_semana: Mapped[str] = mapped_column(String(20)) # Ex: "Segunda-feira"
    
    # Horários (Pode usar String para simplificar no início ou tipo Time)
    horario_inicio: Mapped[str] = mapped_column(String(5)) # Ex: "08:00"
    horario_fim: Mapped[str] = mapped_column(String(5)) # Ex: "09:40"
    
    # Chaves Estrangeiras
    disciplina_id: Mapped[UUID] = mapped_column(ForeignKey("disciplinas.id"))
    # professor_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id")) # Liga à tabela do seu colega
    professor_id: Mapped[UUID] = mapped_column(nullable=True)

    # Relacionamentos
    disciplina: Mapped["Disciplina"] = relationship(back_populates="turmas")


# Tabela de Associação (Muitos para Muitos) - Liga Alunos às Turmas
class Matricula(Base):
    __tablename__ = "matriculas"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # aluno_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    aluno_id: Mapped[UUID] = mapped_column(nullable=False)
    turma_id: Mapped[UUID] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(Integer)