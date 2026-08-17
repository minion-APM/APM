"""adicionando tamanho_id em movimentacoes

Revision ID: a6a15de4ef5a
Revises: a9b33494c2e6
Create Date: 2026-08-17 14:41:58.883113
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6a15de4ef5a"
down_revision: Union[str, Sequence[str], None] = "a9b33494c2e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("movimentacoes") as batch_op:
        batch_op.add_column(
            sa.Column(
                "tamanho_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_movimentacoes_tamanho_id",
            "produto_tamanhos",
            ["tamanho_id"],
            ["id"],
            ondelete="SET NULL"
        )


def downgrade() -> None:
    with op.batch_alter_table("movimentacoes") as batch_op:
        batch_op.drop_constraint(
            "fk_movimentacoes_tamanho_id",
            type_="foreignkey"
        )

        batch_op.drop_column("tamanho_id")