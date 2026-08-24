"""Criar tabela armarios

Revision ID: b81d7a42c5e1
Revises: a6a15de4ef5a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b81d7a42c5e1"
down_revision: Union[str, Sequence[str], None] = "a6a15de4ef5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "armarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero", sa.String(length=30), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="disponivel"),
        sa.Column("cliente_id", sa.Integer(), nullable=True),
        sa.Column("alugado_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero"),
    )
    op.create_index(op.f("ix_armarios_cliente_id"), "armarios", ["cliente_id"])
    op.create_index(op.f("ix_armarios_numero"), "armarios", ["numero"], unique=True)
    op.create_index(op.f("ix_armarios_status"), "armarios", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_armarios_status"), table_name="armarios")
    op.drop_index(op.f("ix_armarios_numero"), table_name="armarios")
    op.drop_index(op.f("ix_armarios_cliente_id"), table_name="armarios")
    op.drop_table("armarios")
