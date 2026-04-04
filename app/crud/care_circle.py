import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientContentCard,
    CareCirclePatientProfile,
    CareCircleProviderCatalog,
)
from app.models.user import User

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

DAILY_NEWSLETTER_PROVIDER_CATALOG = [
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
    {"provider_key": "nature_scene", "label": "Nature Scene", "icon": "🌿", "category": "memory", "display_order": 14, "patient_visible": True, "family_visible": True},
    {"provider_key": "simple_recipe", "label": "Simple Recipe", "icon": "🍳", "category": "lifestyle", "display_order": 15, "patient_visible": False, "family_visible": True},
    {"provider_key": "this_day_history", "label": "On This Day", "icon": "📅", "category": "memory", "display_order": 16, "patient_visible": True, "family_visible": True},
    {"provider_key": "riddle", "label": "Daily Riddle", "icon": "🤔", "category": "games", "display_order": 17, "patient_visible": True, "family_visible": True},
    {"provider_key": "missing_vowels", "label": "Missing Vowels", "icon": "🔤", "category": "games", "display_order": 18, "patient_visible": True, "family_visible": True},
    {"provider_key": "finish_phrase", "label": "Finish the Phrase", "icon": "💬", "category": "games", "display_order": 19, "patient_visible": True, "family_visible": True},
    {"provider_key": "odd_one_out", "label": "Odd One Out", "icon": "🎯", "category": "games", "display_order": 20, "patient_visible": True, "family_visible": True},
    {"provider_key": "word_scramble", "label": "Word Scramble", "icon": "🔀", "category": "games", "display_order": 21, "patient_visible": True, "family_visible": True},
    {"provider_key": "song_of_the_day", "label": "Song of the Day", "icon": "🎵", "category": "memory", "display_order": 22, "patient_visible": True, "family_visible": True},
    {"provider_key": "complete_the_duo", "label": "Complete the Duo", "icon": "🤝", "category": "games", "display_order": 23, "patient_visible": True, "family_visible": True},
    {"provider_key": "spot_the_difference", "label": "Spot the Difference", "icon": "🔍", "category": "games", "display_order": 24, "patient_visible": True, "family_visible": True},
    {"provider_key": "pen_pal_letter", "label": "Pen Pal Letter", "icon": "✉️", "category": "wellbeing", "display_order": 25, "patient_visible": False, "family_visible": True},
    {"provider_key": "gridless_crossword", "label": "Gridless Crossword", "icon": "📝", "category": "games", "display_order": 26, "patient_visible": True, "family_visible": True},
    {"provider_key": "world_news", "label": "World News", "icon": "🌍", "category": "core", "display_order": 27, "patient_visible": False, "family_visible": True},
    {"provider_key": "hobby_spotlight", "label": "Hobby Spotlight", "icon": "🎨", "category": "lifestyle", "display_order": 28, "patient_visible": True, "family_visible": True},
    {"provider_key": "family_greeting", "label": "Family Greeting", "icon": "👨‍👩‍👧", "category": "core", "display_order": 29, "patient_visible": True, "family_visible": True},
    {"provider_key": "local_history", "label": "Local History", "icon": "🏛️", "category": "memory", "display_order": 30, "patient_visible": True, "family_visible": True},
    {"provider_key": "personal_affirmation", "label": "Personal Affirmation", "icon": "💪", "category": "wellbeing", "display_order": 31, "patient_visible": True, "family_visible": True},
    {"provider_key": "activity_suggestion", "label": "Activity Suggestion", "icon": "🌟", "category": "wellbeing", "display_order": 32, "patient_visible": True, "family_visible": True},
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


def _patient_to_dict(patient: CareCirclePatientProfile, family_name: str, highlights: list[CareCirclePatientContentCard] | None = None) -> dict[str, Any]:
    preferences = patient.preferences or {}
    return {
        "id": str(patient.id),
        "displayName": patient.display_name,
        "familyName": family_name,
        "stage": patient.stage,
        "accessState": patient.access_state,
        "timezone": patient.timezone,
        "deliveryTime": patient.delivery_time,
        "days": patient.delivery_days or [],
        "familyMembers": preferences.get("family_members", []),
        "preferences": preferences.get("preference_tags", []),
        "authImageKeys": patient.auth_image_keys or [],
        "highlights": [
            {
                "title": card.title,
                "body": card.body,
                "kind": card.card_kind,
                "providerKey": card.provider_key,
                "displayOrder": card.display_order,
            }
            for card in (highlights or [])
        ],
    }


async def ensure_provider_catalog_seeded(db: AsyncSession) -> None:
    count = await db.scalar(select(func.count(CareCircleProviderCatalog.id)))
    if count and count > 0:
        return

    for item in DAILY_NEWSLETTER_PROVIDER_CATALOG:
        db.add(CareCircleProviderCatalog(**item, enabled=True, source_app="daily_newsletter"))
    await db.commit()


async def _seed_default_family_state(db: AsyncSession, user: User) -> CareCircleFamily:
    family = CareCircleFamily(
        name=f"{user.display_name or user.username} household",
        created_by_user_id=user.id,
    )
    db.add(family)
    await db.flush()

    db.add(CareCircleFamilyMembership(family_id=family.id, user_id=user.id, role="owner", is_primary=True))

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
            db.add(CareCirclePatientContentCard(patient_id=patient.id, **highlight, is_active=True))

    await db.commit()
    await db.refresh(family)
    return family


async def get_or_create_family_for_user(db: AsyncSession, user: User) -> CareCircleFamily:
    membership = await db.scalar(
        select(CareCircleFamilyMembership).where(CareCircleFamilyMembership.user_id == user.id).order_by(CareCircleFamilyMembership.is_primary.desc(), CareCircleFamilyMembership.id.asc())
    )
    if membership:
        family = await db.get(CareCircleFamily, membership.family_id)
        if family:
            return family
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
    return [_patient_to_dict(patient, family.name) for patient in patients]


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
    return _patient_to_dict(patient, family.name, highlights)


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
            return _patient_to_dict(patient, family.name if family else "Care Circle", highlights)
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
    return _patient_to_dict(patient, family.name if family else "Care Circle", highlights)
