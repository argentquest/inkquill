from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db_session
from app.crud import care_circle as care_circle_crud
from app.models.care_circle import CareCirclePatientProfile
from app.models.user import User
from app.schemas.base import ApiError, ApiResponse
from app.schemas.care_circle import (
    CareCirclePatientLoginRequest,
    CareCirclePatientUpdateRequest,
    CareCircleProviderPatientConfigUpdate,
)

router = APIRouter(prefix="/care-circle", tags=["care-circle"])


class ProviderUpdate(BaseModel):
    enabled: bool
    patient_visible: bool


@router.get("/providers", response_model=ApiResponse)
async def read_care_circle_providers(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    providers = await care_circle_crud.list_provider_catalog(db)
    return ApiResponse.success_response(data=providers)


@router.put("/providers/{provider_key}", response_model=ApiResponse)
async def update_care_circle_provider(
    provider_key: str,
    payload: ProviderUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    provider = await care_circle_crud.update_provider_catalog(
        db, provider_key, payload.enabled, payload.patient_visible
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return ApiResponse.success_response(data={"message": "Updated successfully"})


@router.get("/family/patients", response_model=ApiResponse)
async def read_family_patients(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    patients = await care_circle_crud.list_family_patients(db, current_user)
    return ApiResponse.success_response(data=patients)


@router.get("/family/patients/{patient_id}", response_model=ApiResponse)
async def read_family_patient_detail(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    patient = await care_circle_crud.get_family_patient_detail(db, current_user, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return ApiResponse.success_response(data=patient)


@router.put("/family/patients/{patient_id}", response_model=ApiResponse)
async def update_family_patient_detail(
    patient_id: int,
    payload: CareCirclePatientUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    normalized_join_code = care_circle_crud._normalize_join_code(payload.joinCode)
    if len(normalized_join_code) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Join code must contain at least three letters or digits",
        )

    if len(set(payload.authImageKeys)) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly three unique auth images are required",
        )

    invalid_auth_keys = [
        key for key in payload.authImageKeys if key not in care_circle_crud.PATIENT_AUTH_KEYS
    ]
    if invalid_auth_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid auth image keys: {', '.join(invalid_auth_keys)}",
        )

    try:
        patient = await care_circle_crud.update_family_patient_detail(
            db,
            current_user,
            patient_id,
            {**payload.model_dump(), "joinCode": normalized_join_code},
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return ApiResponse.success_response(data=patient)


@router.get("/patient/auth/catalog", response_model=ApiResponse)
async def read_patient_auth_catalog():
    catalog = await care_circle_crud.get_patient_auth_catalog()
    return ApiResponse.success_response(data=catalog)


@router.post("/patient/auth/login", response_model=ApiResponse)
async def login_patient_by_images(
    payload: CareCirclePatientLoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    patient = await care_circle_crud.authenticate_patient_by_images(db, payload.selected_image_keys)
    if not patient:
        return ApiResponse.error_response(
            errors=[ApiError(code="INVALID_PATIENT_AUTH", message="Those pictures did not match an active patient profile.")]
        )
    return ApiResponse.success_response(data=patient)


@router.get("/patient/session/{patient_id}", response_model=ApiResponse)
async def read_patient_session(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    # Attempt to regenerate fresh provider cards dynamically for the patient
    # In production, this shifts to Celery off-hours scheduling
    await assemble_daily_patient_session(db, patient_id)

    patient = await care_circle_crud.get_patient_session(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient session not found")
    return ApiResponse.success_response(data=patient)


@router.get("/family/patients/{patient_id}/provider-configs", response_model=ApiResponse)
async def read_patient_provider_configs(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """List per-patient provider enablement configs for a family patient."""
    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    configs = await care_circle_crud.get_patient_provider_configs(db, patient_id)
    return ApiResponse.success_response(data=configs)


@router.put("/family/patients/{patient_id}/provider-configs/{provider_key}", response_model=ApiResponse)
async def upsert_patient_provider_config(
    patient_id: int,
    provider_key: str,
    payload: CareCircleProviderPatientConfigUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update a per-patient provider enablement setting."""
    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    config = await care_circle_crud.upsert_patient_provider_config(
        db, patient_id, provider_key, payload.is_enabled, payload.custom_parameters
    )
    return ApiResponse.success_response(data={
        "id": config.id,
        "patient_id": config.patient_id,
        "provider_key": config.provider_key,
        "is_enabled": config.is_enabled,
        "custom_parameters": config.custom_parameters or {},
    })
