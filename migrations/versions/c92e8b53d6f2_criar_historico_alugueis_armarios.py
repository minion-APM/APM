"""Criar histórico de aluguéis de armários

Revision ID: c92e8b53d6f2
Revises: b81d7a42c5e1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c92e8b53d6f2"
down_revision: Union[str, Sequence[str], None] = "b81d7a42c5e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alugueis_armarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("armario_id", sa.Integer(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("inicio_em", sa.DateTime(), nullable=False),
        sa.Column("devolvido_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["armario_id"], ["armarios.id"]),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alugueis_armarios_armario_id"), "alugueis_armarios", ["armario_id"])
    op.create_index(op.f("ix_alugueis_armarios_cliente_id"), "alugueis_armarios", ["cliente_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_alugueis_armarios_cliente_id"), table_name="alugueis_armarios")
    op.drop_index(op.f("ix_alugueis_armarios_armario_id"), table_name="alugueis_armarios")
    op.drop_table("alugueis_armarios")
