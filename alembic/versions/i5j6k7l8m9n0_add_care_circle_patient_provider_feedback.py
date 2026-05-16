"""add care circle patient provider feedback

Revision ID: i5j6k7l8m9n0
Revises: h4i5j6k7l8m9
Create Date: 2026-04-26 10:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "i5j6k7l8m9n0"
down_revision = "h4i5j6k7l8m9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "care_circle_patient_provider_feedback"

    if not inspector.has_table(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("patient_id", sa.Integer(), nullable=False),
            sa.Column("provider_key", sa.String(length=120), nullable=False),
            sa.Column("feedback", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["patient_id"], ["care_circle_patient_profiles.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("patient_id", "provider_key", name="uq_care_circle_patient_provider_feedback"),
        )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_care_circle_patient_provider_feedback_id "
        "ON care_circle_patient_provider_feedback (id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_care_circle_patient_provider_feedback_patient_id "
        "ON care_circle_patient_provider_feedback (patient_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_care_circle_patient_provider_feedback_provider_key "
        "ON care_circle_patient_provider_feedback (provider_key)"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_care_circle_patient_provider_feedback_provider_key"), table_name="care_circle_patient_provider_feedback")
    op.drop_index(op.f("ix_care_circle_patient_provider_feedback_patient_id"), table_name="care_circle_patient_provider_feedback")
    op.drop_index(op.f("ix_care_circle_patient_provider_feedback_id"), table_name="care_circle_patient_provider_feedback")
    op.drop_table("care_circle_patient_provider_feedback")
