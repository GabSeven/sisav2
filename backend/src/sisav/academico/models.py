from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sisav.core.db import Base


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
    professor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )

    disciplina: Mapped["Disciplina"] = relationship(back_populates="turmas")


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(Integer, nullable=False)