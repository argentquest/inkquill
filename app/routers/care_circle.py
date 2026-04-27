from datetime import date as date_type
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db_session
from app.crud import care_circle as care_circle_crud
from app.crud.care_circle_delete import hard_delete_patient
from app.crud import job_status as crud_job_status
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.models.job_status import JobStateEnum, JobTypeEnum
from app.models.user import User
from app.schemas.base import ApiError, ApiResponse
from app.schemas.care_circle import (
    AdminFamilyDisableRequest,
    CareCirclePatientCreateRequest,
    CareCirclePatientLoginRequest,
    CareCirclePatientProviderFeedbackUpdate,
    CareCirclePatientUpdateRequest,
    CareCircleProviderPatientConfigUpdate,
    CareCircleProviderReorderRequest,
    FamilyInviteEmailRequest,
    JoinFamilyRequest,
)
from app.services.email_service import EmailService, get_email_service
from app.utils.iso_codes import LANGUAGES, COUNTRIES

router = APIRouter(prefix="/care-circle", tags=["care-circle"])


class ProviderUpdate(BaseModel):
    enabled: bool
    patient_visible: bool


async def _run_patient_newsletter_regeneration_job(
    job_id: str,
    patient_id: int,
    patient_name: str,
) -> None:
    """Run newsletter regeneration asynchronously and update the job status row."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    async with async_session_local() as db:
        await crud_job_status.update_job_status(
            db,
            job_id,
            JobStateEnum.RUNNING,
            status_message=f"Regenerating newsletter for {patient_name}.",
        )
        try:
            result = await assemble_daily_patient_session(
                db,
                patient_id,
                force_regenerate=True,
            )
            if not result or not result.get("success"):
                await crud_job_status.update_job_status(
                    db,
                    job_id,
                    JobStateEnum.FAILED,
                    status_message=f"Newsletter regeneration failed for {patient_name}.",
                    result_message="assemble_daily_patient_session returned no successful result.",
                )
                return

            await crud_job_status.update_job_status(
                db,
                job_id,
                JobStateEnum.COMPLETED,
                status_message=f"Newsletter regeneration completed for {patient_name}.",
                result_message=f"Generated {result.get('card_count', 0)} cards.",
            )
        except Exception as exc:
            await crud_job_status.update_job_status(
                db,
                job_id,
                JobStateEnum.FAILED,
                status_message=f"Newsletter regeneration failed for {patient_name}.",
                result_message=str(exc)[:500],
            )


@router.get("/cached-image/{patient_id}/{date_str}/{filename}")
async def serve_cached_image(
    patient_id: int,
    date_str: str,
    filename: str,
    current_user: User = Depends(get_current_active_user),
):
    """Serve a provider-cached image file by its API path."""
    from app.services.care_circle.provider_cache import CACHE_ROOT

    candidate = CACHE_ROOT / str(patient_id) / date_str / filename
    try:
        candidate.resolve().relative_to(CACHE_ROOT.resolve())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")

    if not candidate.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    return FileResponse(str(candidate))


@router.get("/providers", response_model=ApiResponse)
async def read_care_circle_providers(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    providers = await care_circle_crud.list_provider_catalog(db)
    return ApiResponse.success_response(data=providers)


@router.get("/iso-codes", response_model=ApiResponse)
async def read_iso_codes(
    current_user: User = Depends(get_current_active_user),
):
    """Return ISO language and country codes for dropdowns."""
    return ApiResponse.success_response(data={
        "languages": LANGUAGES,
        "countries": COUNTRIES,
    })


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


@router.post("/family/patients", response_model=ApiResponse, status_code=201)
async def create_family_patient(
    payload: CareCirclePatientCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    patient = await care_circle_crud.create_family_patient(db, current_user, payload.model_dump())
    return ApiResponse.success_response(data=patient)


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


@router.put("/patient/session/{patient_id}/provider-feedback/{provider_key}", response_model=ApiResponse)
async def update_patient_provider_feedback(
    patient_id: int,
    provider_key: str,
    payload: CareCirclePatientProviderFeedbackUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    patient = await db.get(CareCirclePatientProfile, patient_id)
    if not patient or patient.access_state == "archived":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient session not found")

    try:
        saved_feedback = await care_circle_crud.set_patient_provider_feedback(
            db,
            patient_id,
            provider_key,
            payload.feedback,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ApiResponse.success_response(data={
        "patient_id": patient_id,
        "provider_key": provider_key,
        "feedback": saved_feedback,
    })


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


@router.delete("/family/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Permanently delete a patient and all related data.
    This action is irreversible."""
    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    success = await hard_delete_patient(db, patient_id)
    
    if success:
        return ApiResponse.success_response(
            data={"message": f"Patient {patient_id} has been permanently deleted"}
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete patient. Check server logs."
        )


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

    try:
        config = await care_circle_crud.upsert_patient_provider_config(
            db, patient_id, provider_key, payload.is_enabled, payload.custom_parameters,
            display_order=payload.display_order,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiResponse.success_response(data={
        "id": config.id,
        "patient_id": config.patient_id,
        "provider_key": config.provider_key,
        "is_enabled": config.is_enabled,
        "display_order": config.display_order,
        "custom_parameters": config.custom_parameters or {},
    })


@router.post("/family/patients/{patient_id}/send-newsletter", response_model=ApiResponse)
async def send_patient_newsletter(
    patient_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Immediately assemble and send the newsletter to a single patient."""
    from datetime import date as _date
    from app.services.care_circle.newsletter_delivery_service import deliver_newsletter_to_patient

    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    result = await deliver_newsletter_to_patient(db, patient, _date.today())
    return ApiResponse.success_response(data=result)


@router.post("/family/patients/{patient_id}/regenerate-newsletter", response_model=ApiResponse)
async def regenerate_patient_newsletter(
    patient_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Queue a forced newsletter regeneration job for a patient."""

    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    job_id = str(uuid.uuid4())
    await crud_job_status.create_job(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
        job_type=JobTypeEnum.CARE_CIRCLE_DAILY_SESSION,
        status_message=f"Queued newsletter regeneration for {patient.display_name}.",
    )
    background_tasks.add_task(
        _run_patient_newsletter_regeneration_job,
        job_id,
        patient.id,
        patient.display_name,
    )

    return ApiResponse.success_response(data={
        "job_id": job_id,
        "state": JobStateEnum.PENDING.value,
        "message": "Newsletter regeneration started",
    })


@router.get("/family/patients/{patient_id}/regenerate-newsletter/{job_id}", response_model=ApiResponse)
async def get_regenerate_patient_newsletter_status(
    patient_id: int,
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Return status for a queued newsletter regeneration job."""
    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    job = await crud_job_status.get_job_by_job_id(db, job_id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return ApiResponse.success_response(data={
        "job_id": job.job_id,
        "state": job.state.value,
        "status_message": job.status_message,
        "result_message": job.result_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    })


@router.get("/family/patients/{patient_id}/newsletter-preview", response_model=ApiResponse)
async def get_patient_newsletter_preview(
    patient_id: int,
    for_date: date_type | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Return the assembled newsletter HTML for a patient on a given date.

    Defaults to today. For today, the assembler runs if the cache is cold.
    For past dates, only the on-disk cache is read — no providers are invoked.
    """
    from datetime import date as _date
    from app.services.care_circle.session_assembler import (
        assemble_daily_patient_session,
        get_newsletter_html_for_date,
    )

    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    target_date = for_date or _date.today()
    today = _date.today()

    if target_date > today:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot preview future dates")

    if target_date == today:
        await assemble_daily_patient_session(db, patient_id)

    html = await get_newsletter_html_for_date(db, patient_id, target_date)
    return ApiResponse.success_response(data={
        "date": target_date.isoformat(),
        "html": html,
        "has_content": bool(html),
    })


@router.post("/family/patients/{patient_id}/provider-configs/reorder", response_model=ApiResponse)
async def reorder_patient_provider_configs(
    patient_id: int,
    payload: CareCircleProviderReorderRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk-update display_order for a patient's provider configs."""
    family = await care_circle_crud.get_or_create_family_for_user(db, current_user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    await care_circle_crud.reorder_patient_provider_configs(
        db, patient_id, [item.model_dump() for item in payload.ordering]
    )
    return ApiResponse.success_response(data={"message": "Order saved"})


# ---------------------------------------------------------------------------
# Family membership / join-request endpoints
# ---------------------------------------------------------------------------

@router.post("/family/join", response_model=ApiResponse, status_code=201)
async def join_family(
    payload: JoinFamilyRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a request to join a family by join code."""
    try:
        result = await care_circle_crud.request_to_join_family(db, current_user, payload.join_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse.success_response(data=result)


@router.get("/family/owner-summary", response_model=ApiResponse)
async def get_owner_family_summary(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Return family summary data for the current owner account page."""
    try:
        result = await care_circle_crud.get_owner_family_summary(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return ApiResponse.success_response(data=result)


@router.post("/family/invite-email", response_model=ApiResponse, status_code=201)
async def send_family_invite_email(
    payload: FamilyInviteEmailRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    email_service: EmailService = Depends(get_email_service),
):
    """Send a Care Circle invite email containing the owner's family join code."""
    try:
        summary = await care_circle_crud.get_owner_family_summary(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    success = await email_service.send_care_circle_invite_email(
        recipient_email=payload.email,
        family_name=summary["name"],
        join_code=summary["join_code"],
        inviter_name=current_user.display_name or current_user.username,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invite email could not be sent.")

    return ApiResponse.success_response(
        data={
            "sent": True,
            "email": payload.email,
            "join_code": summary["join_code"],
        }
    )


@router.get("/family/join-requests", response_model=ApiResponse)
async def list_join_requests(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """List pending join requests for the current owner's family."""
    requests = await care_circle_crud.list_join_requests(db, current_user)
    return ApiResponse.success_response(data=requests)


@router.put("/family/join-requests/{membership_id}/approve", response_model=ApiResponse)
async def approve_join_request(
    membership_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = await care_circle_crud.resolve_join_request(db, current_user, membership_id, approve=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse.success_response(data=result)


@router.put("/family/join-requests/{membership_id}/reject", response_model=ApiResponse)
async def reject_join_request(
    membership_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = await care_circle_crud.resolve_join_request(db, current_user, membership_id, approve=False)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse.success_response(data=result)


@router.get("/family/members", response_model=ApiResponse)
async def list_family_members(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """List active members of the current owner's family."""
    members = await care_circle_crud.list_family_members(db, current_user)
    return ApiResponse.success_response(data=members)


@router.delete("/family/members/{membership_id}", response_model=ApiResponse)
async def remove_family_member(
    membership_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        await care_circle_crud.remove_family_member(db, current_user, membership_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse.success_response(data={"message": "Member removed"})


# ---------------------------------------------------------------------------
# Admin family management endpoints
# ---------------------------------------------------------------------------

@router.get("/admin/families", response_model=ApiResponse)
async def admin_list_families(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    families = await care_circle_crud.admin_list_families(db)
    return ApiResponse.success_response(data=families)


@router.put("/admin/families/{family_id}/disable", response_model=ApiResponse)
async def admin_disable_family(
    family_id: int,
    payload: AdminFamilyDisableRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    try:
        result = await care_circle_crud.admin_set_family_disabled(db, family_id, payload.disabled)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiResponse.success_response(data=result)


@router.delete("/admin/families/{family_id}", response_model=ApiResponse)
async def admin_delete_family(
    family_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    try:
        await care_circle_crud.admin_delete_family(db, family_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiResponse.success_response(data={"message": "Family deleted"})
