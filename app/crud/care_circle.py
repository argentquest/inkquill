import json
import string
from secrets import choice
from pathlib import Path
from typing import Any

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientContentCard,
    CareCirclePatientProfile,
    CareCircleProviderCatalog,
    CareCircleProviderPatientConfig,
    CareCirclePatientProviderFeedback,
    CareCircleProviderRunLog,
    CareCircleProviderSessionOutput,
)
from app.models.user import User
from app.services.care_circle.location_service import resolve_postal_location

PATIENT_AUTH_CATALOG = [
    {"key": "sun", "label": "Sun", "emoji": "☀️"},
    {"key": "dog", "label": "Dog", "emoji": "🐶"},
    {"key": "flower", "label": "Flower", "emoji": "🌷"},
    {"key": "cake", "label": "Cake", "emoji": "🎂"},
    {"key": "bird", "label": "Bird", "emoji": "🐦"},
    {"key": "car", "label": "Car", "emoji": "🚗"},
    {"key": "tree", "label": "Tree", "emoji": "🌳"},
    {"key": "house", "label": "House", "emoji": "🏡"},
    {"key": "moon", "label": "Moon", "emoji": "🌙"},
    {"key": "star", "label": "Star", "emoji": "⭐"},
    {"key": "boat", "label": "Boat", "emoji": "⛵"},
    {"key": "hat", "label": "Hat", "emoji": "🎩"},
]
PATIENT_AUTH_KEYS = {item["key"] for item in PATIENT_AUTH_CATALOG}

PROVIDER_INVENTORY_CONFIG_PATH = Path(__file__).resolve().parent.parent / "services" / "care_circle" / "providers" / "config.json"
PROVIDER_CONFIGS_ROOT = Path(__file__).resolve().parent.parent / "services" / "care_circle" / "providers"
OBSOLETE_PROVIDER_KEYS = {"comic_mimi_eunice"}

DEFAULT_DAILY_NEWSLETTER_PROVIDER_CATALOG = [
    {"provider_key": "weather", "label": "Weather", "icon": "☀️", "category": "core", "display_order": 1, "patient_visible": True, "family_visible": True},
    {"provider_key": "joke", "label": "Daily Joy", "icon": "😄", "category": "wellbeing", "display_order": 2, "patient_visible": True, "family_visible": True},
    {"provider_key": "nostalgia", "label": "Time Machine", "icon": "🕰️", "category": "memory", "display_order": 3, "patient_visible": True, "family_visible": True},
    {"provider_key": "puzzle", "label": "Puzzle", "icon": "🧩", "category": "games", "display_order": 4, "patient_visible": True, "family_visible": True},
    {"provider_key": "brain_booster", "label": "Brain Booster", "icon": "🧠", "category": "games", "display_order": 5, "patient_visible": True, "family_visible": True},
    {"provider_key": "sensory", "label": "Sensory", "icon": "🎵", "category": "wellbeing", "display_order": 6, "patient_visible": True, "family_visible": True},
    {"provider_key": "ai_trivia", "label": "AI Trivia", "icon": "💡", "category": "games", "display_order": 7, "patient_visible": True, "family_visible": True},
    {"provider_key": "daily_quote", "label": "Daily Quote", "icon": "✨", "category": "core", "display_order": 8, "patient_visible": True, "family_visible": True},
    {"provider_key": "dog_photo", "label": "Furry Friend", "icon": "🐶", "category": "memory", "display_order": 9, "patient_visible": True, "family_visible": True},
    {"provider_key": "cat_fact", "label": "Cat Fact", "icon": "🐱", "category": "memory", "display_order": 10, "patient_visible": True, "family_visible": True},
    {"provider_key": "gratitude", "label": "Gratitude", "icon": "🙏", "category": "wellbeing", "display_order": 11, "patient_visible": True, "family_visible": True},
    {"provider_key": "gentle_exercise", "label": "Gentle Exercise", "icon": "🤼", "category": "wellbeing", "display_order": 12, "patient_visible": True, "family_visible": True},
    {"provider_key": "daily_affirmation", "label": "Affirmation", "icon": "💛", "category": "core", "display_order": 13, "patient_visible": True, "family_visible": True},
    {"provider_key": "simple_recipe", "label": "Simple Recipe", "icon": "🍳", "category": "lifestyle", "display_order": 15, "patient_visible": True, "family_visible": True},
    {"provider_key": "this_day_history", "label": "On This Day", "icon": "📅", "category": "memory", "display_order": 16, "patient_visible": True, "family_visible": True},
    {"provider_key": "riddle", "label": "Daily Riddle", "icon": "🤔", "category": "games", "display_order": 17, "patient_visible": True, "family_visible": True},
    {"provider_key": "missing_vowels", "label": "Missing Vowels", "icon": "🔤", "category": "games", "display_order": 18, "patient_visible": True, "family_visible": True},
    {"provider_key": "finish_phrase", "label": "Finish the Phrase", "icon": "💬", "category": "games", "display_order": 19, "patient_visible": True, "family_visible": True},
    {"provider_key": "odd_one_out", "label": "Odd One Out", "icon": "🎯", "category": "games", "display_order": 20, "patient_visible": True, "family_visible": True},
    {"provider_key": "word_scramble", "label": "Word Scramble", "icon": "🔀", "category": "games", "display_order": 21, "patient_visible": True, "family_visible": True},
    {"provider_key": "song_of_the_day", "label": "Song of the Day", "icon": "🎵", "category": "memory", "display_order": 22, "patient_visible": True, "family_visible": True},
    {"provider_key": "complete_the_duo", "label": "Complete the Duo", "icon": "🤝", "category": "games", "display_order": 23, "patient_visible": True, "family_visible": True},
    {"provider_key": "spot_the_difference", "label": "Spot the Difference", "icon": "🔍", "category": "games", "display_order": 24, "patient_visible": True, "family_visible": True},
    {"provider_key": "pen_pal_letter", "label": "Pen Pal Letter", "icon": "✉️", "category": "wellbeing", "display_order": 25, "patient_visible": True, "family_visible": True},
    {"provider_key": "gridless_crossword", "label": "Gridless Crossword", "icon": "📝", "category": "games", "display_order": 26, "patient_visible": True, "family_visible": True},
    {"provider_key": "world_news", "label": "World News", "icon": "🌍", "category": "core", "display_order": 27, "patient_visible": True, "family_visible": True},
    {"provider_key": "hobby_spotlight", "label": "Hobby Spotlight", "icon": "🎨", "category": "lifestyle", "display_order": 28, "patient_visible": True, "family_visible": True},
    {"provider_key": "family_greeting", "label": "Family Greeting", "icon": "👨‍👩‍👧", "category": "core", "display_order": 29, "patient_visible": True, "family_visible": True},
    {"provider_key": "local_history", "label": "Local History", "icon": "🏛️", "category": "memory", "display_order": 30, "patient_visible": True, "family_visible": True},
    {"provider_key": "personal_affirmation", "label": "Personal Affirmation", "icon": "💪", "category": "wellbeing", "display_order": 31, "patient_visible": True, "family_visible": True},
    {"provider_key": "activity_suggestion", "label": "Activity Suggestion", "icon": "🌟", "category": "wellbeing", "display_order": 32, "patient_visible": True, "family_visible": True},
    {"provider_key": "animal_friend", "label": "Animal Friend", "icon": "🐾", "category": "memory", "display_order": 33, "patient_visible": True, "family_visible": True},
    {"provider_key": "bingo", "label": "Bingo", "icon": "🎲", "category": "games", "display_order": 34, "patient_visible": True, "family_visible": True},
    {"provider_key": "color_match", "label": "Color Match", "icon": "🎨", "category": "games", "display_order": 35, "patient_visible": True, "family_visible": True},
    {"provider_key": "daily_blessing", "label": "Daily Blessing", "icon": "🕊️", "category": "wellbeing", "display_order": 36, "patient_visible": True, "family_visible": True},
    {"provider_key": "simple_math", "label": "Simple Math", "icon": "➕", "category": "games", "display_order": 39, "patient_visible": True, "family_visible": True},
    {"provider_key": "word_connect", "label": "Word Connect", "icon": "🔗", "category": "games", "display_order": 40, "patient_visible": True, "family_visible": True},
    {"provider_key": "classic_art", "label": "Art of the Day", "icon": "🖼️", "category": "memory", "display_order": 41, "patient_visible": True, "family_visible": True},
    {"provider_key": "nature_park", "label": "National Park", "icon": "🏞️", "category": "memory", "display_order": 42, "patient_visible": True, "family_visible": True},
    {"provider_key": "wikimedia_gallery", "label": "Photo of the Day", "icon": "📸", "category": "memory", "display_order": 43, "patient_visible": True, "family_visible": True},
]

DEFAULT_PATIENTS = [
    {
        "display_name": "Rose Ellis",
        "stage": "moderate",
        "access_state": "active",
        "timezone": "America/Chicago",
        "delivery_time": "08:30",
        "delivery_days": ["Mon", "Wed", "Fri", "Sun"],
        "auth_image_keys": ["sun", "dog", "house"],
        "preferences": {
            "family_members": ["Nina", "Paul", "Maggie"],
            "preference_tags": ["1950s music", "family photos", "tea and biscuits", "gardening"],
        },
        "highlights": [
            {"provider_key": "family_greeting", "title": "Family hello", "body": "Nina says the daffodils are opening and she saved the first photo for you.", "card_kind": "family", "display_order": 1},
            {"provider_key": "nostalgia", "title": "Memory lane", "body": "Today’s memory card revisits spring walks and favorite songs from the 1950s.", "card_kind": "memory", "display_order": 2},
            {"provider_key": "activity_suggestion", "title": "Gentle activity", "body": "Try watering one plant or naming three flowers you remember from home.", "card_kind": "activity", "display_order": 3},
        ],
    },
    {
        "display_name": "Arthur Bloom",
        "stage": "mild",
        "access_state": "inactive",
        "timezone": "America/New_York",
        "delivery_time": "09:15",
        "delivery_days": ["Tue", "Thu", "Sat"],
        "auth_image_keys": ["tree", "car", "star"],
        "preferences": {
            "family_members": ["Janet", "Chris"],
            "preference_tags": ["local history", "jazz", "crosswords"],
        },
        "highlights": [
            {"provider_key": "family_greeting", "title": "Daily note", "body": "Chris left a short update about yesterday’s walk by the river.", "card_kind": "family", "display_order": 1},
            {"provider_key": "brain_booster", "title": "Brain booster", "body": "A short word puzzle is ready for the next active session.", "card_kind": "activity", "display_order": 2},
            {"provider_key": "personal_affirmation", "title": "Comfort prompt", "body": "Play a favorite jazz recording and read one memory card aloud.", "card_kind": "comfort", "display_order": 3},
        ],
    },
]


def _patient_to_dict(
    patient: CareCirclePatientProfile,
    family_name: str,
    family_join_code: str,
    highlights: list[CareCirclePatientContentCard] | None = None,
    feedback_by_provider: dict[str, str] | None = None,
) -> dict[str, Any]:
    raw = patient.preferences or {}
    feedback_by_provider = feedback_by_provider or {}
    return {
        "id": str(patient.id),
        "displayName": patient.display_name,
        "familyName": family_name,
        "joinCode": family_join_code,
        "stage": patient.stage,
        "accessState": patient.access_state,
        "timezone": patient.timezone,
        "preferredLanguage": patient.preferred_language,
        "country": patient.country,
        "postalCode": patient.postal_code,
        "latitude": patient.latitude,
        "longitude": patient.longitude,
        "deliveryTime": patient.delivery_time,
        "days": patient.delivery_days or [],
        "authImageKeys": patient.auth_image_keys or [],
        "email": patient.email,
        "phoneNumber": patient.phone_number,
        "preferences": {
            "recipientName": raw.get("recipient_name"),
            "preferredPronoun": raw.get("preferred_pronoun"),
            "hometown": raw.get("hometown"),
            "cityForWeather": raw.get("city_for_weather"),
            "eraOfYouth": raw.get("era_of_youth"),
            "nationalityOrBackground": raw.get("nationality_or_background"),
            "mobilityLevel": raw.get("mobility_level"),
            "familyMembers": raw.get("family_members", []),
            "lifeRoles": raw.get("life_roles", []),
            "pets": raw.get("pets", []),
            "hobbies": raw.get("hobbies", []),
            "favoriteActivities": raw.get("favorite_activities", []),
            "favoriteSingers": raw.get("favorite_singers", []),
            "favouriteFoods": raw.get("favourite_foods", []),
            "favouriteTvShows": raw.get("favourite_tv_shows", []),
        },
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
        "newsletters_sent": 0,
        "highlights": [
            {
                "title": card.title,
                "body": card.body,
                "renderedHtml": card.rendered_html,
                "kind": card.card_kind,
                "providerKey": card.provider_key,
                "displayOrder": card.display_order,
                "feedback": feedback_by_provider.get(card.provider_key),
            }
            for card in (highlights or [])
        ],
    }


def _normalize_join_code(join_code: str) -> str:
    return "".join(ch for ch in join_code.upper().strip() if ch in string.ascii_uppercase + string.digits)


async def _generate_unique_join_code(db: AsyncSession) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        candidate = "".join(choice(alphabet) for _ in range(6))
        existing = await db.scalar(
            select(CareCircleFamily.id).where(CareCircleFamily.join_code == candidate)
        )
        if existing is None:
            return candidate


def _load_provider_catalog_inventory() -> list[dict[str, Any]]:
    if PROVIDER_INVENTORY_CONFIG_PATH.exists():
        raw_inventory = json.loads(PROVIDER_INVENTORY_CONFIG_PATH.read_text(encoding="utf-8"))
        providers = raw_inventory.get("providers", [])
        normalized: list[dict[str, Any]] = []
        for item in providers:
            if item["name"] in OBSOLETE_PROVIDER_KEYS:
                continue
            normalized.append(
                {
                    "provider_key": item["name"],
                    "label": item["label"],
                    "icon": item.get("icon"),
                    "category": item.get("category", "core"),
                    "enabled": bool(item.get("enabled", True)),
                    "display_order": int(item.get("order", 0)),
                    "patient_visible": bool(item.get("patient_visible", True)),
                    "family_visible": bool(item.get("family_visible", True)),
                }
            )
        return normalized
    return DEFAULT_DAILY_NEWSLETTER_PROVIDER_CATALOG


def _load_provider_common_flag(provider_key: str) -> bool:
    config_path = PROVIDER_CONFIGS_ROOT / provider_key / "config.json"
    if not config_path.exists():
        return False

    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    return bool(raw.get("common", False))


async def remove_obsolete_provider_data(db: AsyncSession) -> None:
    """Delete provider rows that should no longer exist anywhere in Care Circle."""
    if not OBSOLETE_PROVIDER_KEYS:
        return

    for model in (
        CareCircleProviderSessionOutput,
        CareCircleProviderRunLog,
        CareCirclePatientContentCard,
        CareCircleProviderPatientConfig,
        CareCirclePatientProviderFeedback,
        CareCircleProviderCatalog,
    ):
        await db.execute(
            delete(model).where(model.provider_key.in_(OBSOLETE_PROVIDER_KEYS))
        )


async def ensure_provider_catalog_seeded(db: AsyncSession) -> None:
    await remove_obsolete_provider_data(db)
    provider_catalog = _load_provider_catalog_inventory()
    existing_rows = (
        await db.execute(select(CareCircleProviderCatalog))
    ).scalars().all()
    existing_map = {row.provider_key: row for row in existing_rows}

    for item in provider_catalog:
        existing = existing_map.get(item["provider_key"])
        if existing:
            existing.label = item["label"]
            existing.icon = item["icon"]
            existing.category = item["category"]
            existing.display_order = item["display_order"]
            continue

        db.add(CareCircleProviderCatalog(**item, source_app="daily_newsletter"))
    await db.commit()


async def _seed_patients_for_family(
    db: AsyncSession, family: CareCircleFamily, user: User
) -> None:
    """Seed default patients for a family that has no patients."""
    for patient_data in DEFAULT_PATIENTS:
        patient = CareCirclePatientProfile(
            family_id=family.id,
            created_by_user_id=user.id,
            display_name=patient_data["display_name"],
            stage=patient_data["stage"],
            access_state=patient_data["access_state"],
            timezone=patient_data["timezone"],
            delivery_time=patient_data["delivery_time"],
            delivery_days=patient_data["delivery_days"],
            auth_image_keys=patient_data["auth_image_keys"],
            preferences=patient_data["preferences"],
        )
        db.add(patient)
        await db.flush()
        for highlight in patient_data["highlights"]:
            db.add(CareCirclePatientContentCard(
                patient_id=patient.id, **highlight, is_active=True
            ))
    await db.commit()


async def _seed_default_family_state(db: AsyncSession, user: User) -> CareCircleFamily:
    family = CareCircleFamily(
        name=f"{user.display_name or user.username} household",
        join_code=await _generate_unique_join_code(db),
        created_by_user_id=user.id,
    )
    db.add(family)
    await db.flush()

    db.add(CareCircleFamilyMembership(
        family_id=family.id, user_id=user.id, role="owner", status="active", is_primary=True
    ))

    await _seed_patients_for_family(db, family, user)
    await db.refresh(family)
    return family


async def get_or_create_family_for_user(db: AsyncSession, user: User) -> CareCircleFamily:
    membership = await db.scalar(
        select(CareCircleFamilyMembership)
        .where(
            CareCircleFamilyMembership.user_id == user.id,
            CareCircleFamilyMembership.status == "active",
        )
        .order_by(CareCircleFamilyMembership.is_primary.desc(), CareCircleFamilyMembership.id.asc())
    )
    if membership:
        family = await db.get(CareCircleFamily, membership.family_id)
        if family:
            patient_count = await db.scalar(
                select(func.count(CareCirclePatientProfile.id)).where(CareCirclePatientProfile.family_id == family.id)
            )
            if not patient_count or patient_count == 0:
                await _seed_patients_for_family(db, family, user)
            if not family.join_code:
                family.join_code = await _generate_unique_join_code(db)
                await db.commit()
            return family
    # If the user only has a pending request, don't auto-create a new family
    has_pending = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.user_id == user.id,
            CareCircleFamilyMembership.status == "pending",
        )
    )
    if has_pending:
        raise ValueError("Your join request is pending approval. You do not have an active family yet.")
    return await _seed_default_family_state(db, user)


async def list_family_patients(db: AsyncSession, user: User) -> list[dict[str, Any]]:
    await ensure_provider_catalog_seeded(db)
    family = await get_or_create_family_for_user(db, user)
    patients = (
        await db.execute(
            select(CareCirclePatientProfile)
            .where(CareCirclePatientProfile.family_id == family.id)
            .order_by(CareCirclePatientProfile.id.asc())
        )
    ).scalars().all()

    # Count successful newsletter runs per patient
    patient_ids = [p.id for p in patients]
    newsletter_counts: dict[int, int] = {}
    if patient_ids:
        rows = (
            await db.execute(
                select(
                    CareCircleProviderRunLog.patient_id,
                    func.count(CareCircleProviderRunLog.id).label("cnt"),
                )
                .where(
                    CareCircleProviderRunLog.patient_id.in_(patient_ids),
                    CareCircleProviderRunLog.status == "succeeded",
                )
                .group_by(CareCircleProviderRunLog.patient_id)
            )
        ).all()
        newsletter_counts = {row.patient_id: row.cnt for row in rows}

    results = [_patient_to_dict(patient, family.name, family.join_code) for patient in patients]
    for item in results:
        pid = int(item["id"])
        item["newsletters_sent"] = newsletter_counts.get(pid, 0)
    return results


async def list_family_activity_events(
    db: AsyncSession,
    user: User,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Build a recent family activity feed from existing Care Circle state."""
    family = await get_or_create_family_for_user(db, user)
    events: list[dict[str, Any]] = []

    def add_event(
        *,
        event_id: str,
        event_type: str,
        title: str,
        description: str,
        tone: str,
        occurred_at,
        patient_id: int | None = None,
        patient_name: str | None = None,
        provider_key: str | None = None,
    ) -> None:
        if not occurred_at:
            return
        events.append({
            "id": event_id,
            "type": event_type,
            "title": title,
            "description": description,
            "tone": tone,
            "occurred_at": occurred_at.isoformat(),
            "patient_id": patient_id,
            "patient_name": patient_name,
            "provider_key": provider_key,
            "_sort": occurred_at,
        })

    add_event(
        event_id=f"family-{family.id}-created",
        event_type="family_created",
        title="Care Circle created",
        description=f"{family.name} is ready for family members and friend profiles.",
        tone="success",
        occurred_at=family.created_at,
    )

    patient_rows = (
        await db.execute(
            select(CareCirclePatientProfile)
            .where(CareCirclePatientProfile.family_id == family.id)
            .order_by(desc(CareCirclePatientProfile.created_at))
            .limit(limit)
        )
    ).scalars().all()
    for patient in patient_rows:
        add_event(
            event_id=f"patient-{patient.id}-created",
            event_type="patient_created",
            title=f"{patient.display_name} was added",
            description=f"Friend profile is {patient.access_state} with {len(patient.auth_image_keys or [])} sign-in images configured.",
            tone="info" if patient.access_state == "active" else "warning",
            occurred_at=patient.created_at,
            patient_id=patient.id,
            patient_name=patient.display_name,
        )

    output_rows = (
        await db.execute(
            select(CareCircleProviderSessionOutput, CareCirclePatientProfile)
            .join(CareCirclePatientProfile, CareCirclePatientProfile.id == CareCircleProviderSessionOutput.patient_id)
            .where(CareCirclePatientProfile.family_id == family.id)
            .order_by(desc(CareCircleProviderSessionOutput.created_at))
            .limit(limit)
        )
    ).all()
    for output, patient in output_rows:
        add_event(
            event_id=f"session-output-{output.id}",
            event_type="provider_output_created",
            title="Daily content generated",
            description=f"{output.provider_key.replace('_', ' ').title()} generated content for {patient.display_name}.",
            tone="success",
            occurred_at=output.created_at,
            patient_id=patient.id,
            patient_name=patient.display_name,
            provider_key=output.provider_key,
        )

    run_rows = (
        await db.execute(
            select(CareCircleProviderRunLog, CareCirclePatientProfile)
            .join(CareCirclePatientProfile, CareCirclePatientProfile.id == CareCircleProviderRunLog.patient_id)
            .where(CareCirclePatientProfile.family_id == family.id)
            .order_by(desc(CareCircleProviderRunLog.created_at))
            .limit(limit)
        )
    ).all()
    for run, patient in run_rows:
        if run.status == "succeeded":
            continue
        add_event(
            event_id=f"provider-run-{run.id}",
            event_type="provider_run_failed",
            title="Provider fallback used",
            description=f"{run.provider_key.replace('_', ' ').title()} could not finish for {patient.display_name}.",
            tone="warning",
            occurred_at=run.created_at,
            patient_id=patient.id,
            patient_name=patient.display_name,
            provider_key=run.provider_key,
        )

    member_rows = (
        await db.execute(
            select(CareCircleFamilyMembership, User)
            .join(User, User.id == CareCircleFamilyMembership.user_id)
            .where(CareCircleFamilyMembership.family_id == family.id)
            .order_by(desc(CareCircleFamilyMembership.created_at))
            .limit(limit)
        )
    ).all()
    for membership, member in member_rows:
        if membership.role == "owner":
            continue
        status_label = "requested access" if membership.status == "pending" else f"became {membership.status}"
        add_event(
            event_id=f"membership-{membership.id}-{membership.status}",
            event_type=f"membership_{membership.status}",
            title="Family member update",
            description=f"{member.display_name or member.username} {status_label}.",
            tone="info" if membership.status == "active" else "warning",
            occurred_at=membership.created_at,
        )

    events.sort(key=lambda event: event["_sort"], reverse=True)
    return [{key: value for key, value in event.items() if key != "_sort"} for event in events[:limit]]


async def get_family_patient_detail(db: AsyncSession, user: User, patient_id: int) -> dict[str, Any] | None:
    family = await get_or_create_family_for_user(db, user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        return None
    highlights = (
        await db.execute(
            select(CareCirclePatientContentCard)
            .where(CareCirclePatientContentCard.patient_id == patient.id, CareCirclePatientContentCard.is_active.is_(True))
            .order_by(CareCirclePatientContentCard.display_order.asc(), CareCirclePatientContentCard.id.asc())
        )
    ).scalars().all()
    return _patient_to_dict(patient, family.name, family.join_code, highlights)


async def update_family_patient_detail(
    db: AsyncSession,
    user: User,
    patient_id: int,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    family = await get_or_create_family_for_user(db, user)
    patient = await db.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.id == patient_id,
            CareCirclePatientProfile.family_id == family.id,
        )
    )
    if not patient:
        return None

    normalized_join_code = _normalize_join_code(payload["joinCode"])
    existing_join_code_owner = await db.scalar(
        select(CareCircleFamily).where(
            CareCircleFamily.join_code == normalized_join_code,
            CareCircleFamily.id != family.id,
        )
    )
    if existing_join_code_owner:
        raise ValueError("Join code is already assigned to another family")

    patient.display_name = payload["displayName"].strip()
    patient.stage = payload["stage"].strip()
    patient.access_state = payload["accessState"].strip()
    patient.timezone = payload["timezone"].strip()
    patient.preferred_language = payload.get("preferredLanguage", "en")
    patient.country = payload.get("country", "US")
    patient.postal_code = (payload.get("postalCode") or "").strip() or None
    patient.delivery_time = payload["deliveryTime"] or None
    patient.delivery_days = payload["days"]
    patient.auth_image_keys = payload["authImageKeys"]
    patient.email = payload.get("email") or None
    patient.phone_number = payload.get("phoneNumber") or None
    prefs = payload.get("preferences") or {}
    patient.preferences = {
        "recipient_name": prefs.get("recipientName") or None,
        "preferred_pronoun": prefs.get("preferredPronoun") or None,
        "hometown": prefs.get("hometown") or None,
        "city_for_weather": prefs.get("cityForWeather") or None,
        "era_of_youth": prefs.get("eraOfYouth") or None,
        "nationality_or_background": prefs.get("nationalityOrBackground") or None,
        "mobility_level": prefs.get("mobilityLevel") or None,
        "family_members": prefs.get("familyMembers") or [],
        "life_roles": prefs.get("lifeRoles") or [],
        "pets": prefs.get("pets") or [],
        "hobbies": prefs.get("hobbies") or [],
        "favorite_activities": prefs.get("favoriteActivities") or [],
        "favorite_singers": prefs.get("favoriteSingers") or [],
        "favourite_foods": prefs.get("favouriteFoods") or [],
        "favourite_tv_shows": prefs.get("favouriteTvShows") or [],
    }
    if patient.postal_code:
        resolved_location = await resolve_postal_location(
            postal_code=patient.postal_code,
            country_code=patient.country,
        )
        if resolved_location:
            patient.latitude = resolved_location.latitude
            patient.longitude = resolved_location.longitude
            if not patient.preferences.get("city_for_weather") and resolved_location.formatted_city:
                patient.preferences["city_for_weather"] = resolved_location.formatted_city
        else:
            patient.latitude = None
            patient.longitude = None
    else:
        patient.latitude = None
        patient.longitude = None
    family.name = payload["familyName"].strip()
    family.join_code = normalized_join_code

    await db.commit()
    return await get_family_patient_detail(db, user, patient_id)


async def create_family_patient(
    db: AsyncSession,
    user: User,
    payload: dict[str, Any],
) -> dict[str, Any]:
    family = await get_or_create_family_for_user(db, user)
    patient = CareCirclePatientProfile(
        family_id=family.id,
        created_by_user_id=user.id,
        display_name=payload["displayName"].strip(),
        stage=payload.get("stage", "moderate"),
        access_state=payload.get("accessState", "active"),
        timezone=payload.get("timezone", "America/Chicago"),
        preferred_language=payload.get("preferredLanguage", "en"),
        country=payload.get("country", "US"),
        postal_code=(payload.get("postalCode") or "").strip() or None,
        delivery_time=payload.get("deliveryTime") or None,
        delivery_days=[],
        auth_image_keys=[],
        preferences={},
    )
    if patient.postal_code:
        resolved_location = await resolve_postal_location(
            postal_code=patient.postal_code,
            country_code=patient.country,
        )
        if resolved_location:
            patient.latitude = resolved_location.latitude
            patient.longitude = resolved_location.longitude
            patient.preferences = {
                "city_for_weather": resolved_location.formatted_city,
            } if resolved_location.formatted_city else {}
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return _patient_to_dict(patient, family.name, family.join_code)


async def list_provider_catalog(db: AsyncSession) -> list[dict[str, Any]]:
    await ensure_provider_catalog_seeded(db)
    providers = (
        await db.execute(select(CareCircleProviderCatalog).order_by(CareCircleProviderCatalog.display_order.asc(), CareCircleProviderCatalog.id.asc()))
    ).scalars().all()
    return [
        {
            "providerKey": provider.provider_key,
            "label": provider.label,
            "icon": provider.icon,
            "category": provider.category,
            "enabled": provider.enabled,
            "displayOrder": provider.display_order,
            "patientVisible": provider.patient_visible,
            "familyVisible": provider.family_visible,
            "common": _load_provider_common_flag(provider.provider_key),
        }
        for provider in providers
    ]


async def get_patient_auth_catalog() -> list[dict[str, str]]:
    return PATIENT_AUTH_CATALOG

async def update_provider_catalog(db: AsyncSession, provider_key: str, enabled: bool, patient_visible: bool):
    provider = await db.scalar(select(CareCircleProviderCatalog).where(CareCircleProviderCatalog.provider_key == provider_key))
    if not provider:
        return None
    provider.enabled = enabled
    provider.patient_visible = patient_visible
    await db.commit()
    await db.refresh(provider)
    return provider


async def authenticate_patient_by_images(db: AsyncSession, selected_keys: list[str]) -> dict[str, Any] | None:
    unique_keys = []
    for key in selected_keys:
        if key not in PATIENT_AUTH_KEYS:
            return None
        if key not in unique_keys:
            unique_keys.append(key)
    if len(unique_keys) != 3:
        return None

    patients = (
        await db.execute(select(CareCirclePatientProfile).where(CareCirclePatientProfile.access_state == "active"))
    ).scalars().all()
    normalized = json.dumps(sorted(unique_keys))
    for patient in patients:
        if json.dumps(sorted(patient.auth_image_keys or [])) == normalized:
            family = await db.get(CareCircleFamily, patient.family_id)
            highlights = (
                await db.execute(
                    select(CareCirclePatientContentCard)
                    .where(CareCirclePatientContentCard.patient_id == patient.id, CareCirclePatientContentCard.is_active.is_(True))
                    .order_by(CareCirclePatientContentCard.display_order.asc(), CareCirclePatientContentCard.id.asc())
                )
            ).scalars().all()
            feedback_by_provider = await get_patient_provider_feedback_map(db, patient.id)
            return _patient_to_dict(
                patient,
                family.name if family else "Care Circle",
                family.join_code if family and family.join_code else "",
                highlights,
                feedback_by_provider,
            )
    return None


async def get_patient_session(db: AsyncSession, patient_id: int) -> dict[str, Any] | None:
    patient = await db.get(CareCirclePatientProfile, patient_id)
    if not patient or patient.access_state == "archived":
        return None
    family = await db.get(CareCircleFamily, patient.family_id)
    highlights = (
        await db.execute(
            select(CareCirclePatientContentCard)
            .where(CareCirclePatientContentCard.patient_id == patient.id, CareCirclePatientContentCard.is_active.is_(True))
            .order_by(CareCirclePatientContentCard.display_order.asc(), CareCirclePatientContentCard.id.asc())
        )
    ).scalars().all()
    feedback_by_provider = await get_patient_provider_feedback_map(db, patient.id)
    return _patient_to_dict(
        patient,
        family.name if family else "Care Circle",
        family.join_code if family and family.join_code else "",
        highlights,
        feedback_by_provider,
    )


async def get_patient_provider_feedback_map(
    db: AsyncSession,
    patient_id: int,
) -> dict[str, str]:
    rows = (
        await db.execute(
            select(CareCirclePatientProviderFeedback).where(
                CareCirclePatientProviderFeedback.patient_id == patient_id
            )
        )
    ).scalars().all()
    return {row.provider_key: row.feedback for row in rows}


async def set_patient_provider_feedback(
    db: AsyncSession,
    patient_id: int,
    provider_key: str,
    feedback: str | None,
) -> str | None:
    if provider_key in OBSOLETE_PROVIDER_KEYS:
        raise ValueError(f"Provider '{provider_key}' is no longer available")

    await ensure_provider_catalog_seeded(db)
    provider = await db.scalar(
        select(CareCircleProviderCatalog).where(
            CareCircleProviderCatalog.provider_key == provider_key
        )
    )
    if not provider:
        raise ValueError(f"Provider '{provider_key}' was not found")

    existing = await db.scalar(
        select(CareCirclePatientProviderFeedback).where(
            CareCirclePatientProviderFeedback.patient_id == patient_id,
            CareCirclePatientProviderFeedback.provider_key == provider_key,
        )
    )

    if feedback is None:
        if existing:
            await db.delete(existing)
            await db.commit()
        return None

    if existing:
        existing.feedback = feedback
        await db.commit()
        await db.refresh(existing)
        return existing.feedback

    new_feedback = CareCirclePatientProviderFeedback(
        patient_id=patient_id,
        provider_key=provider_key,
        feedback=feedback,
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback.feedback


async def get_patient_provider_configs(
    db: AsyncSession, patient_id: int
) -> list[dict[str, Any]]:
    """List all provider configs for a patient."""
    configs = (
        await db.execute(
            select(CareCircleProviderPatientConfig).where(
                CareCircleProviderPatientConfig.patient_id == patient_id,
                CareCircleProviderPatientConfig.provider_key.notin_(OBSOLETE_PROVIDER_KEYS),
            )
        )
    ).scalars().all()
    return [
        {
            "id": c.id,
            "patient_id": c.patient_id,
            "provider_key": c.provider_key,
            "is_enabled": c.is_enabled,
            "display_order": c.display_order,
            "custom_parameters": c.custom_parameters or {},
        }
        for c in configs
    ]


async def upsert_patient_provider_config(
    db: AsyncSession,
    patient_id: int,
    provider_key: str,
    is_enabled: bool,
    custom_parameters: dict | None = None,
    display_order: int | None = None,
) -> CareCircleProviderPatientConfig:
    """Insert or update a per-patient provider config."""
    if provider_key in OBSOLETE_PROVIDER_KEYS:
        raise ValueError(f"Provider '{provider_key}' is no longer available")

    existing = await db.scalar(
        select(CareCircleProviderPatientConfig).where(
            CareCircleProviderPatientConfig.patient_id == patient_id,
            CareCircleProviderPatientConfig.provider_key == provider_key,
        )
    )
    if existing:
        existing.is_enabled = is_enabled
        if custom_parameters is not None:
            existing.custom_parameters = custom_parameters
        if display_order is not None:
            existing.display_order = display_order
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        new_config = CareCircleProviderPatientConfig(
            patient_id=patient_id,
            provider_key=provider_key,
            is_enabled=is_enabled,
            display_order=display_order,
            custom_parameters=custom_parameters or {},
        )
        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
        return new_config


async def reorder_patient_provider_configs(
    db: AsyncSession,
    patient_id: int,
    ordering: list[dict],
) -> None:
    """Bulk-update display_order for a patient's enabled provider configs."""
    for item in ordering:
        provider_key = item["provider_key"]
        if provider_key in OBSOLETE_PROVIDER_KEYS:
            continue
        new_order = item["display_order"]
        existing = await db.scalar(
            select(CareCircleProviderPatientConfig).where(
                CareCircleProviderPatientConfig.patient_id == patient_id,
                CareCircleProviderPatientConfig.provider_key == provider_key,
            )
        )
        if existing:
            existing.display_order = new_order
        else:
            db.add(CareCircleProviderPatientConfig(
                patient_id=patient_id,
                provider_key=provider_key,
                is_enabled=True,
                display_order=new_order,
                custom_parameters={},
            ))
    await db.commit()


# ---------------------------------------------------------------------------
# Family membership / join-request functions
# ---------------------------------------------------------------------------

async def request_to_join_family(db: AsyncSession, user: User, join_code: str) -> dict[str, Any]:
    """Create a pending membership for a user wanting to join a family by join code."""
    normalized = _normalize_join_code(join_code)
    family = await db.scalar(select(CareCircleFamily).where(CareCircleFamily.join_code == normalized))
    if not family:
        raise ValueError("No family found with that join code.")
    if family.is_disabled:
        raise ValueError("This family is currently disabled.")

    existing = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.user_id == user.id,
        )
    )
    if existing:
        if existing.status == "active":
            raise ValueError("You are already a member of this family.")
        if existing.status == "pending":
            raise ValueError("You already have a pending request for this family.")
        # rejected — allow re-request by updating status
        existing.status = "pending"
        await db.commit()
        return {"status": "pending", "family_name": family.name}

    db.add(CareCircleFamilyMembership(
        family_id=family.id,
        user_id=user.id,
        role="member",
        status="pending",
        is_primary=True,
    ))
    await db.commit()
    return {"status": "pending", "family_name": family.name}


async def get_owner_family(db: AsyncSession, user: User) -> CareCircleFamily | None:
    """Return the family the user owns (active owner membership)."""
    membership = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.user_id == user.id,
            CareCircleFamilyMembership.role == "owner",
            CareCircleFamilyMembership.status == "active",
        )
    )
    if not membership:
        return None
    return await db.get(CareCircleFamily, membership.family_id)


async def get_owner_family_summary(db: AsyncSession, owner_user: User) -> dict[str, Any]:
    """Return owner-only family summary details used by the account UI."""
    family = await get_owner_family(db, owner_user)
    if not family:
        raise ValueError("You do not own a family.")

    active_member_count = await db.scalar(
        select(func.count(CareCircleFamilyMembership.id)).where(
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.status == "active",
        )
    )
    pending_request_count = await db.scalar(
        select(func.count(CareCircleFamilyMembership.id)).where(
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.status == "pending",
        )
    )

    return {
        "id": family.id,
        "name": family.name,
        "join_code": family.join_code,
        "active_member_count": active_member_count or 0,
        "pending_request_count": pending_request_count or 0,
    }


async def list_join_requests(db: AsyncSession, owner_user: User) -> list[dict[str, Any]]:
    """Return pending join requests for the owner's family."""
    family = await get_owner_family(db, owner_user)
    if not family:
        return []
    rows = (
        await db.execute(
            select(CareCircleFamilyMembership, User)
            .join(User, User.id == CareCircleFamilyMembership.user_id)
            .where(
                CareCircleFamilyMembership.family_id == family.id,
                CareCircleFamilyMembership.status == "pending",
            )
            .order_by(CareCircleFamilyMembership.created_at.asc())
        )
    ).all()
    return [
        {
            "id": m.id,
            "user_id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "email": u.email,
            "requested_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, u in rows
    ]


async def resolve_join_request(
    db: AsyncSession, owner_user: User, membership_id: int, approve: bool
) -> dict[str, Any]:
    """Approve or reject a pending join request. Owner only."""
    family = await get_owner_family(db, owner_user)
    if not family:
        raise ValueError("You do not own a family.")
    membership = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.id == membership_id,
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.status == "pending",
        )
    )
    if not membership:
        raise ValueError("Join request not found.")
    membership.status = "active" if approve else "rejected"
    await db.commit()
    return {"id": membership_id, "status": membership.status}


async def list_family_members(db: AsyncSession, owner_user: User) -> list[dict[str, Any]]:
    """Return all active non-owner members of the owner's family."""
    family = await get_owner_family(db, owner_user)
    if not family:
        return []
    rows = (
        await db.execute(
            select(CareCircleFamilyMembership, User)
            .join(User, User.id == CareCircleFamilyMembership.user_id)
            .where(
                CareCircleFamilyMembership.family_id == family.id,
                CareCircleFamilyMembership.status == "active",
                CareCircleFamilyMembership.role != "owner",
            )
            .order_by(CareCircleFamilyMembership.created_at.asc())
        )
    ).all()
    return [
        {
            "id": m.id,
            "user_id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "email": u.email,
            "role": m.role,
            "joined_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, u in rows
    ]


async def remove_family_member(db: AsyncSession, owner_user: User, membership_id: int) -> None:
    """Remove an active member from the owner's family."""
    family = await get_owner_family(db, owner_user)
    if not family:
        raise ValueError("You do not own a family.")
    membership = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.id == membership_id,
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.role != "owner",
        )
    )
    if not membership:
        raise ValueError("Member not found.")
    await db.delete(membership)
    await db.commit()


# ---------------------------------------------------------------------------
# Admin family management
# ---------------------------------------------------------------------------

async def admin_list_families(db: AsyncSession) -> list[dict[str, Any]]:
    """Return all families with owner username, member count, patient count."""
    families = (await db.execute(select(CareCircleFamily).order_by(CareCircleFamily.id.asc()))).scalars().all()
    result = []
    for family in families:
        owner_row = await db.scalar(
            select(CareCircleFamilyMembership).where(
                CareCircleFamilyMembership.family_id == family.id,
                CareCircleFamilyMembership.role == "owner",
                CareCircleFamilyMembership.status == "active",
            )
        )
        owner_user = await db.get(User, owner_row.user_id) if owner_row else None
        member_count = await db.scalar(
            select(func.count(CareCircleFamilyMembership.id)).where(
                CareCircleFamilyMembership.family_id == family.id,
                CareCircleFamilyMembership.status == "active",
            )
        )
        patient_count = await db.scalar(
            select(func.count(CareCirclePatientProfile.id)).where(
                CareCirclePatientProfile.family_id == family.id,
            )
        )
        pending_count = await db.scalar(
            select(func.count(CareCircleFamilyMembership.id)).where(
                CareCircleFamilyMembership.family_id == family.id,
                CareCircleFamilyMembership.status == "pending",
            )
        )
        result.append({
            "id": family.id,
            "name": family.name,
            "join_code": family.join_code,
            "is_disabled": family.is_disabled,
            "owner_username": owner_user.username if owner_user else None,
            "owner_display_name": owner_user.display_name if owner_user else None,
            "member_count": member_count or 0,
            "patient_count": patient_count or 0,
            "pending_requests": pending_count or 0,
            "created_at": family.created_at.isoformat() if family.created_at else None,
        })
    return result


async def admin_set_family_disabled(db: AsyncSession, family_id: int, disabled: bool) -> dict[str, Any]:
    family = await db.get(CareCircleFamily, family_id)
    if not family:
        raise ValueError("Family not found.")
    family.is_disabled = disabled
    await db.commit()
    return {"id": family.id, "is_disabled": family.is_disabled}


async def admin_delete_family(db: AsyncSession, family_id: int) -> None:
    family = await db.get(CareCircleFamily, family_id)
    if not family:
        raise ValueError("Family not found.")
    await db.delete(family)
    await db.commit()
