"""merge care circle heads

Revision ID: h4i5j6k7l8m9
Revises: a9b8c7d6e5f4, g3h4i5j6k7l8
Create Date: 2026-04-25 09:05:00.000000

"""

from typing import Sequence, Union


revision: str = "h4i5j6k7l8m9"
down_revision: Union[str, Sequence[str], None] = ("a9b8c7d6e5f4", "g3h4i5j6k7l8")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge divergent care circle heads into a single linear head."""


def downgrade() -> None:
    """Split the merge point back into the prior divergent heads."""
