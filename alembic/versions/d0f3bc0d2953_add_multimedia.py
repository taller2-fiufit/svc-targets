"""add multimedia

Revision ID: d0f3bc0d2953
Revises: 43f9a5ee2d4c
Create Date: 2023-06-20 18:16:35.335060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d0f3bc0d2953"
down_revision = "43f9a5ee2d4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "target_multimedias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["target_id"],
            ["targets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("target_multimedias", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_target_multimedias_id"), ["id"], unique=False
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("target_multimedias", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_target_multimedias_id"))

    op.drop_table("target_multimedias")
    # ### end Alembic commands ###
