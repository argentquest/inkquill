from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional

from app.db.database import Base


class CareCircleFamily(Base):
    __tablename__ = "care_circle_families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    join_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CareCircleFamilyMembership(Base):
    __tablename__ = "care_circle_family_memberships"
    __table_args__ = (UniqueConstraint("family_id", "user_id", name="uq_care_circle_family_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("care_circle_families.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), default="owner", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CareCirclePatientProfile(Base):
    __tablename__ = "care_circle_patient_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("care_circle_families.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    family_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    stage: Mapped[str] = mapped_column(String(50), default="moderate", nullable=False)
    access_state: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), default="America/Chicago", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    country: Mapped[str] = mapped_column(String(10), default="US", nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delivery_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    delivery_days: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    auth_image_keys: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CareCircleProviderCatalog(Base):
    __tablename__ = "care_circle_provider_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    patient_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    family_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_app: Mapped[str] = mapped_column(String(100), default="daily_newsletter", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CareCirclePatientContentCard(Base):
    __tablename__ = "care_circle_patient_content_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("care_circle_patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    rendered_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    card_kind: Mapped[str] = mapped_column(String(50), default="family", nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CareCircleProviderRunLog(Base):
    __tablename__ = "care_circle_provider_run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    patient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("care_circle_patient_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    family_id: Mapped[Optional[int]] = mapped_column(ForeignKey("care_circle_families.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="succeeded", nullable=False) # e.g. "succeeded", "failed"
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CareCircleProviderPatientConfig(Base):
    __tablename__ = "care_circle_provider_patient_configs"
    __table_args__ = (UniqueConstraint("patient_id", "provider_key", name="uq_care_circle_patient_provider"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("care_circle_patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    schedule_expression: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    custom_parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CareCircleProviderSessionOutput(Base):
    __tablename__ = "care_circle_provider_session_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("care_circle_patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    run_log_id: Mapped[Optional[int]] = mapped_column(ForeignKey("care_circle_provider_run_logs.id", ondelete="SET NULL"), nullable=True)
    output_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    session_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

