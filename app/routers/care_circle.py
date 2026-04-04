from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db_session
from app.crud import care_circle as care_circle_crud
from app.models.user import User
from app.schemas.base import ApiError, ApiResponse
from app.schemas.care_circle import CareCirclePatientLoginRequest

router = APIRouter(prefix="/care-circle", tags=["care-circle"])


@router.get("/providers", response_model=ApiResponse)
async def read_care_circle_providers(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    providers = await care_circle_crud.list_provider_catalog(db)
    return ApiResponse.success_response(data=providers)


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
    patient = await care_circle_crud.get_patient_session(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient session not found")
    return ApiResponse.success_response(data=patient)
