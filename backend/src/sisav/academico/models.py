from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sisav.core.db import Base
from sisav.usuarios.models import Usuario  # Importando o modelo para a relação


class DiaSemana(StrEnum):
    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class TipoAvaliacao(StrEnum):
    CRITERIO = "criterio"
    AVALIACAO = "avaliacao"
    EXAME = "exame"


class SituacaoAluno(StrEnum):
    APROVADO = "Aprovado"
    REPROVADO = "Reprovado"
    REP_POR_FALTA = "Rep. por Falta"
    EXAME_FINAL = "Exame Final"


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    carga_horaria: Mapped[int] = mapped_column(Integer, nullable=False)

    turmas: Mapped[list["Turma"]] = relationship(back_populates="disciplina")
    criterios: Mapped[list["CriterioAvaliacao"]] = relationship(
        back_populates="disciplina"
    )


class Turma(Base):
    __tablename__ = "turmas"
    __table_args__ = (
        CheckConstraint(
            "dia_semana IN "
            "('segunda','terca','quarta','quinta','sexta','sabado','domingo')",
            name="dia_semana_valido",
        ),
        CheckConstraint("horario_fim > horario_inicio", name="horario_ordem"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    semestre: Mapped[str] = mapped_column(String(10), nullable=False)
    sala: Mapped[str] = mapped_column(String(50), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(10), nullable=False)
    horario_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    horario_fim: Mapped[time] = mapped_column(Time, nullable=False)

    disciplina_id: Mapped[int] = mapped_column(ForeignKey("disciplinas.id"), nullable=False)
    professor_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fechada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fechada_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    disciplina: Mapped["Disciplina"] = relationship(back_populates="turmas")
    professor: Mapped["Usuario"] = relationship(foreign_keys=[professor_id])
    fechado_por: Mapped["Usuario | None"] = relationship(foreign_keys=[fechada_por])
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="turma")
    avaliacoes: Mapped[list["Avaliacao"]] = relationship(back_populates="turma")
    consolidacoes: Mapped[list["ConsolidacaoAluno"]] = relationship(back_populates="turma")


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"), nullable=False)
    ano_letivo: Mapped[int] = mapped_column(Integer, nullable=False)

    aluno: Mapped["Usuario"] = relationship(foreign_keys=[aluno_id])
    turma: Mapped["Turma"] = relationship(back_populates="matriculas")
    notas: Mapped[list["Nota"]] = relationship(back_populates="matricula")
    consolidacao: Mapped["ConsolidacaoAluno | None"] = relationship(
        back_populates="matricula", uselist=False
    )


class CriterioAvaliacao(Base):
    """Componente cumulativo da nota de uma disciplina.

    Uma disciplina pode ter vários; não são modos alternativos de avaliar.
    O template não propaga para turmas já criadas.
    """

    __tablename__ = "criterios_avaliacoes"
    __table_args__ = (
        UniqueConstraint(
            "disciplina_id",
            "ordem",
            name="uq_criterios_avaliacoes_disciplina_ordem",
        ),
        CheckConstraint("peso > 0", name="peso_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    disciplina_id: Mapped[int] = mapped_column(
        ForeignKey("disciplinas.id"), nullable=False, index=True
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    peso: Mapped[int] = mapped_column(Integer, nullable=False, default=100)  # centésimos

    disciplina: Mapped["Disciplina"] = relationship(back_populates="criterios")
    subcriterios: Mapped[list["SubcriterioAvaliacao"]] = relationship(
        back_populates="criterio"
    )


class SubcriterioAvaliacao(Base):
    """Segmento de 2º nível do critério; também é template por disciplina."""

    __tablename__ = "subcriterios_avaliacoes"
    __table_args__ = (
        UniqueConstraint(
            "criterio_id",
            "ordem",
            name="uq_subcriterios_avaliacoes_criterio_ordem",
        ),
        CheckConstraint("peso > 0", name="peso_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    criterio_id: Mapped[int] = mapped_column(
        ForeignKey("criterios_avaliacoes.id"), nullable=False, index=True
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    peso: Mapped[int] = mapped_column(Integer, nullable=False, default=100)  # centésimos

    criterio: Mapped["CriterioAvaliacao"] = relationship(back_populates="subcriterios")


class Avaliacao(Base):
    """Instância na turma, copiada do template da disciplina.

    tipo=criterio   -> pai, sem Nota, peso multiplica a média dos filhos.
    tipo=avaliacao  -> folha, recebe Nota.
    tipo=exame      -> único por turma, sem pai, peso fixo 1,00.
    Profundidade máxima: 2 (pai não pode ter pai).
    """

    __tablename__ = "avaliacoes"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('criterio','avaliacao','exame')", name="tipo_valido"
        ),
        CheckConstraint("peso > 0", name="peso_positivo"),
        UniqueConstraint("turma_id", "codigo", name="uq_avaliacoes_turma_codigo"),
        Index(
            "uq_avaliacoes_exame_por_turma",
            "turma_id",
            unique=True,
            postgresql_where=text("tipo = 'exame'"),
            sqlite_where=text("tipo = 'exame'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    peso: Mapped[int] = mapped_column(Integer, nullable=False, default=100)  # centésimos
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TipoAvaliacao.AVALIACAO.value
    )
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)

    turma_id: Mapped[int] = mapped_column(
        ForeignKey("turmas.id"), nullable=False, index=True
    )
    pai_id: Mapped[int | None] = mapped_column(
        ForeignKey("avaliacoes.id"), nullable=True, index=True
    )

    turma: Mapped["Turma"] = relationship(back_populates="avaliacoes")
    pai: Mapped["Avaliacao | None"] = relationship(
        back_populates="filhos",
        remote_side=[id],
        foreign_keys=[pai_id],
    )
    filhos: Mapped[list["Avaliacao"]] = relationship(
        back_populates="pai",
        foreign_keys=[pai_id],
    )
    notas: Mapped[list["Nota"]] = relationship(back_populates="avaliacao")


class Nota(Base):
    __tablename__ = "notas"
    __table_args__ = (
        CheckConstraint("valor BETWEEN 0 AND 1000", name="valor_entre_0_e_10"),
        UniqueConstraint(
            "avaliacao_id", "matricula_id", name="uq_notas_avaliacao_matricula"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)  # centésimos

    avaliacao_id: Mapped[int] = mapped_column(
        ForeignKey("avaliacoes.id"), nullable=False, index=True
    )
    matricula_id: Mapped[int] = mapped_column(
        ForeignKey("matriculas.id"), nullable=False, index=True
    )

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="notas")
    matricula: Mapped["Matricula"] = relationship(back_populates="notas")


class RegistroFrequencia(Base):
    __tablename__ = "registros_frequencia"
    __table_args__ = (
        UniqueConstraint(
            "matricula_id",
            "data",
            "horario_inicio",
            "horario_fim",
            name="uq_registros_frequencia_matricula_data_bloco",
        ),
        CheckConstraint("faltas >= 0", name="faltas_nao_negativas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    matricula_id: Mapped[int] = mapped_column(
        ForeignKey("matriculas.id"), nullable=False, index=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    horario_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    horario_fim: Mapped[time] = mapped_column(Time, nullable=False)
    faltas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    matricula: Mapped["Matricula"] = relationship()


class ConsolidacaoAluno(Base):
    """Snapshot gravado no fechamento; não é recalculado depois."""

    __tablename__ = "consolidacao_alunos"
    __table_args__ = (
        UniqueConstraint(
            "turma_id", "matricula_id", name="uq_consolidacao_alunos_turma_matricula"
        ),
        CheckConstraint(
            "situacao IN "
            "('Aprovado','Reprovado','Rep. por Falta','Exame Final')",
            name="situacao_valido",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    turma_id: Mapped[int] = mapped_column(
        ForeignKey("turmas.id"), nullable=False, index=True
    )
    matricula_id: Mapped[int] = mapped_column(
        ForeignKey("matriculas.id"), nullable=False, index=True
    )
    media_pre_exame: Mapped[int] = mapped_column(Integer, nullable=False)  # centésimos
    nota_exame: Mapped[int | None] = mapped_column(Integer, nullable=True)  # centésimos
    media_final: Mapped[int] = mapped_column(Integer, nullable=False)  # centésimos
    total_faltas: Mapped[int] = mapped_column(Integer, nullable=False)
    limite_faltas: Mapped[int] = mapped_column(Integer, nullable=False)
    situacao: Mapped[str] = mapped_column(String(30), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    turma: Mapped["Turma"] = relationship(back_populates="consolidacoes")
    matricula: Mapped["Matricula"] = relationship(back_populates="consolidacao")


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
