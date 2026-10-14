"""criar tabelas academicas

Revision ID: 0d10cd83dd10
Revises: adc5e3b6728b
Create Date: 2026-10-13 04:45:04.382808

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0d10cd83dd10"
down_revision: str | None = "adc5e3b6728b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "disciplinas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("carga_horaria", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_disciplinas")),
    )
    op.create_table(
        "turmas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=20), nullable=False),
        sa.Column("semestre", sa.String(length=10), nullable=False),
        sa.Column("sala", sa.String(length=50), nullable=False),
        sa.Column("dia_semana", sa.String(length=20), nullable=False),
        sa.Column("horario_inicio", sa.String(length=5), nullable=False),
        sa.Column("horario_fim", sa.String(length=5), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.Column("professor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["disciplina_id"],
            ["disciplinas.id"],
            name=op.f("fk_turmas_disciplina_id_disciplinas"),
        ),
        sa.ForeignKeyConstraint(
            ["professor_id"],
            ["usuarios.id"],
            name=op.f("fk_turmas_professor_id_usuarios"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_turmas")),
    )
    op.create_table(
        "matriculas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("turma_id", sa.Integer(), nullable=False),
        sa.Column("ano_letivo", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["aluno_id"],
            ["usuarios.id"],
            name=op.f("fk_matriculas_aluno_id_usuarios"),
        ),
        sa.ForeignKeyConstraint(
            ["turma_id"],
            ["turmas.id"],
            name=op.f("fk_matriculas_turma_id_turmas"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_matriculas")),
    )


def downgrade() -> None:
    op.drop_table("matriculas")
    op.drop_table("turmas")
    op.drop_table("disciplinas")