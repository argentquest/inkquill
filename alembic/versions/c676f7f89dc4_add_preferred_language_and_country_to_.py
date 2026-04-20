# /story_app/alembic/script.py.mako
"""add_preferred_language_and_country_to_patient_profiles

Revision ID: c676f7f89dc4
Revises: b9c0d1e2f3a4
Create Date: 2026-04-19 09:14:09.377396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c676f7f89dc4'
down_revision: Union[str, None] = 'b9c0d1e2f3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('care_circle_patient_profiles', sa.Column('preferred_language', sa.String(10), nullable=False, server_default='en'))
    op.add_column('care_circle_patient_profiles', sa.Column('country', sa.String(10), nullable=False, server_default='US'))


def downgrade() -> None:
    op.drop_column('care_circle_patient_profiles', 'country')
    op.drop_column('care_circle_patient_profiles', 'preferred_language')
