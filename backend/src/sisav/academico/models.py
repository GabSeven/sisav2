from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sisav.core.db import Base
from sisav.usuarios.models import Usuario  # Importando o modelo para a relação


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    carga_horaria: Mapped[int] = mapped_column(Integer, nullable=False)

    turmas: Mapped[list["Turma"]] = relationship(back_populates="disciplina")


class Turma(Base):
    __tablename__ = "turmas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    semestre: Mapped[str] = mapped_column(String(10), nullable=False)
    sala: Mapped[str] = mapped_column(String(50), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(20), nullable=False)
    horario_inicio: Mapped[str] = mapped_column(String(5), nullable=False)
    horario_fim: Mapped[str] = mapped_column(String(5), nullable=False)

    disciplina_id: Mapped[int] = mapped_column(ForeignKey("disciplinas.id"), nullable=False)
    professor_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    disciplina: Mapped["Disciplina"] = relationship(back_populates="turmas")
    professor: Mapped["Usuario"] = relationship(foreign_keys=[professor_id])


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(Integer, nullable=False)

    aluno: Mapped["Usuario"] = relationship(foreign_keys=[aluno_id])
    turma: Mapped["Turma"] = relationship()

class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False) # Ex: "Prova 1", "Trabalho Final"
    peso: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)

    turma: Mapped["Turma"] = relationship()
    notas: Mapped[list["Nota"]] = relationship(back_populates="avaliacao")


class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    
    avaliacao_id: Mapped[int] = mapped_column(ForeignKey("avaliacoes.id"), nullable=False)
    matricula_id: Mapped[int] = mapped_column(ForeignKey("matriculas.id"), nullable=False)

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="notas")
    matricula: Mapped["Matricula"] = relationship()