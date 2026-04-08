"""add join code to care circle families

Revision ID: f2a1b3c4d5e6
Revises: b6c446e463aa
Create Date: 2026-04-05 11:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a1b3c4d5e6"
down_revision: Union[str, None] = "b6c446e463aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("care_circle_families", sa.Column("join_code", sa.String(length=20), nullable=True))

    op.execute(
        """
        UPDATE care_circle_families
        SET join_code = 'CC' || LPAD(id::text, 4, '0')
        WHERE join_code IS NULL
        """
    )

    op.alter_column("care_circle_families", "join_code", nullable=False)
    op.create_index(op.f("ix_care_circle_families_join_code"), "care_circle_families", ["join_code"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_care_circle_families_join_code"), table_name="care_circle_families")
    op.drop_column("care_circle_families", "join_code")
