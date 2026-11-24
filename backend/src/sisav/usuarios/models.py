from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from sisav.core.db import Base


class Perfil(StrEnum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    GESTOR = "gestor"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_de_usuario: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[Perfil] = mapped_column(
        Enum(
            Perfil,
            name="perfil_usuario",
            values_callable=lambda enum: [membro.value for membro in enum],
        ),
        nullable=False,
    )

    telefone: Mapped[str] = mapped_column(String(20), nullable=True)
    email_alternativo: Mapped[str] = mapped_column(String(150), unique=True, nullable=True)
    foto_perfil: Mapped[str] = mapped_column(String(255), nullable=True)

class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=True)