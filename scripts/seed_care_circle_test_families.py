import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.security import get_password_hash
from app.crud.care_circle import ensure_provider_catalog_seeded
from app.db.database import async_session_local
from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientContentCard,
    CareCirclePatientProfile,
)
from app.models.user import User


COMMON_PASSWORD = "password123"


@dataclass(frozen=True)
class SeedUser:
    email: str
    display_name: str
    role: str
    primary_family: str | None = None


@dataclass(frozen=True)
class SeedPatient:
    family_name: str
    owner_email: str
    recipient_name: str
    auth_image_keys: list[str]
    preferences: dict[str, Any]
    email: str = ""
    phone_number: str = ""


@dataclass(frozen=True)
class SeedFamily:
    name: str
    join_code: str
    members: list[SeedUser]


FAMILIES = [
    SeedFamily(
        name="Maple Grove",
        join_code="MAP111",
        members=[
            SeedUser("ericsilvertx+clara@gmail.com", "Clara Maple", "owner", primary_family="Maple Grove"),
            SeedUser("ericsilvertx+mason@gmail.com", "Mason Maple", "member"),
            SeedUser("ericsilvertx+nina@gmail.com", "Nina Maple", "member"),
        ],
    ),
    SeedFamily(
        name="Harbor Point",
        join_code="HBR222",
        members=[
            SeedUser("olivia.harbor@example.com", "Olivia Harbor", "owner", primary_family="Harbor Point"),
            SeedUser("ericsilvertx+ethan@gmail.com", "Ethan Harbor", "member"),
            SeedUser("ericsilvertx+jack@gmail.com", "Jack Harbor", "member"),
        ],
    ),
    SeedFamily(
        name="Sunset Ridge",
        join_code="SUN333",
        members=[
            SeedUser("ericsilvertx+sophie@gmail.com", "Sophie Sunset", "owner", primary_family="Sunset Ridge"),
            SeedUser("ericsilvertx+noah@gmail.com", "Noah Sunset", "member"),
            SeedUser("ericsilvertx+maya@gmail.com", "Maya Sunset", "member"),
        ],
    ),
]


SHARED_USER = SeedUser(
    "ericsilvertx+taylor@gmail.com",
    "Taylor Shared",
    "member",
    primary_family="Maple Grove",
)


PATIENTS = [
    SeedPatient(
        family_name="Maple Grove",
        owner_email="ericsilvertx+clara@gmail.com",
        recipient_name="Clara Maple",
        email="ericsilvertx+patient.clara@gmail.com",
        phone_number="+15125550101",
        auth_image_keys=["sun", "flower", "house"],
        preferences={
            "city_for_weather": "Portland, OR",
            "timezone": "America/Los_Angeles",
            "delivery_time": "08:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1944-04-10",
            "preferred_pronoun": "she/her",
            "nationality_or_background": "American",
            "religion_or_faith": "Methodist",
            "life_roles": ["mother", "grandmother", "school teacher"],
            "hometown": "Eugene, OR",
            "era_of_youth": "1950s",
            "favorite_singers": ["Doris Day", "Patti Page", "Perry Como"],
            "favorite_activities": ["Knitting", "Tending her rose garden"],
            "hobbies": ["Scrapbooking", "Jigsaw puzzles"],
            "favourite_foods": ["Chicken pot pie", "Lemon drizzle cake", "Fresh strawberries"],
            "favourite_tv_shows": ["I Love Lucy", "The Ed Sullivan Show"],
            "pets": ["cat named Mittens"],
            "family_members": ["Mason", "Nina"],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Maple Grove",
        owner_email="ericsilvertx+clara@gmail.com",
        recipient_name="Mason Maple",
        email="ericsilvertx+patient.mason@gmail.com",
        phone_number="+15125550102",
        auth_image_keys=["dog", "car", "tree"],
        preferences={
            "city_for_weather": "Portland, OR",
            "timezone": "America/Los_Angeles",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1941-11-03",
            "preferred_pronoun": "he/him",
            "nationality_or_background": "American",
            "religion_or_faith": "Presbyterian",
            "life_roles": ["father", "grandfather", "carpenter", "coach"],
            "hometown": "Salem, OR",
            "era_of_youth": "1950s",
            "favorite_singers": ["Johnny Cash", "Elvis Presley", "Hank Williams"],
            "favorite_activities": ["Woodworking", "Watching baseball"],
            "hobbies": ["Fishing", "Model trains"],
            "favourite_foods": ["Beef stew", "Apple pie", "Corn on the cob"],
            "favourite_tv_shows": ["Gunsmoke", "Bonanza"],
            "pets": ["dog named Biscuit"],
            "family_members": ["Clara", "Nina"],
            "cognitive_stage": "moderate",
            "mobility_level": "seated",
            "sensory_notes": ["hard of hearing"],
        },
    ),
    SeedPatient(
        family_name="Maple Grove",
        owner_email="ericsilvertx+clara@gmail.com",
        recipient_name="Nina Maple",
        email="ericsilvertx+patient.nina@gmail.com",
        phone_number="+15125550103",
        auth_image_keys=["cake", "bird", "flower"],
        preferences={
            "city_for_weather": "Portland, OR",
            "timezone": "America/Los_Angeles",
            "delivery_time": "08:30",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1947-08-22",
            "preferred_pronoun": "she/her",
            "nationality_or_background": "American",
            "religion_or_faith": "Catholic",
            "life_roles": ["mother", "nurse", "volunteer"],
            "hometown": "Astoria, OR",
            "era_of_youth": "1960s",
            "favorite_singers": ["Ella Fitzgerald", "Billie Holiday", "Dionne Warwick"],
            "favorite_activities": ["Reading", "Watercolour painting"],
            "hobbies": ["Bird watching", "Crossword puzzles"],
            "favourite_foods": ["Tomato soup", "Fresh bread", "Vanilla sponge cake"],
            "favourite_tv_shows": ["The Mary Tyler Moore Show", "Bewitched"],
            "pets": [],
            "family_members": ["Clara", "Mason"],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": ["large print needed"],
        },
    ),
    SeedPatient(
        family_name="Harbor Point",
        owner_email="olivia.harbor@example.com",
        recipient_name="Olivia Harbor",
        email="ericsilvertx+patient.olivia@gmail.com",
        phone_number="+441234550201",
        auth_image_keys=["bird", "house", "tree"],
        preferences={
            "city_for_weather": "Portsmouth",
            "timezone": "Europe/London",
            "delivery_time": "08:00",
            "delivery_days": [],
            "language": "en-GB",
            "date_of_birth": "1939-05-07",
            "preferred_pronoun": "she/her",
            "nationality_or_background": "British",
            "religion_or_faith": "Church of England",
            "life_roles": ["mother", "grandmother", "district nurse"],
            "hometown": "Portsmouth",
            "era_of_youth": "1940s",
            "favorite_singers": ["Vera Lynn", "Gracie Fields", "Cliff Richard"],
            "favorite_activities": ["Knitting", "Listening to the radio"],
            "hobbies": ["Crossword puzzles", "Baking Victoria sponge"],
            "favourite_foods": ["Fish and chips", "Victoria sponge", "Egg and cress sandwiches"],
            "favourite_tv_shows": ["Coronation Street", "Last of the Summer Wine"],
            "pets": ["cat named Biscuit"],
            "family_members": ["Ethan", "Jack"],
            "cognitive_stage": "moderate",
            "mobility_level": "seated",
            "sensory_notes": ["large print needed", "hard of hearing"],
        },
    ),
    SeedPatient(
        family_name="Harbor Point",
        owner_email="olivia.harbor@example.com",
        recipient_name="Ethan Harbor",
        email="ericsilvertx+patient.ethan@gmail.com",
        phone_number="+16175550202",
        auth_image_keys=["car", "sun", "bird"],
        preferences={
            "city_for_weather": "Boston, MA",
            "timezone": "America/New_York",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1943-02-14",
            "preferred_pronoun": "he/him",
            "nationality_or_background": "American",
            "religion_or_faith": "Protestant",
            "life_roles": ["father", "harbour master", "sailor"],
            "hometown": "Gloucester, MA",
            "era_of_youth": "1950s",
            "favorite_singers": ["Frank Sinatra", "Dean Martin", "Sammy Davis Jr"],
            "favorite_activities": ["Sailing", "Watching the sea"],
            "hobbies": ["Fishing", "Woodcarving"],
            "favourite_foods": ["Lobster roll", "Clam chowder", "Blueberry pie"],
            "favourite_tv_shows": ["The Tonight Show", "Ed Sullivan Show"],
            "pets": [],
            "family_members": ["Olivia", "Jack"],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Harbor Point",
        owner_email="olivia.harbor@example.com",
        recipient_name="Jack Harbor",
        email="ericsilvertx+patient.jack@gmail.com",
        phone_number="+353871550203",
        auth_image_keys=["dog", "cake", "house"],
        preferences={
            "city_for_weather": "Galway",
            "timezone": "Europe/Dublin",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-IE",
            "date_of_birth": "1946-03-17",
            "preferred_pronoun": "he/him",
            "nationality_or_background": "Irish",
            "religion_or_faith": "Catholic",
            "life_roles": ["father", "farmer", "GAA player"],
            "hometown": "Galway",
            "era_of_youth": "1960s",
            "favorite_singers": ["Daniel O'Donnell", "Val Doonican", "Christy Moore"],
            "favorite_activities": ["Tending the garden", "Watching GAA football"],
            "hobbies": ["Fishing", "Playing cards"],
            "favourite_foods": ["Irish stew", "Soda bread", "Bacon and cabbage"],
            "favourite_tv_shows": ["The Late Late Show", "Nationwide"],
            "pets": ["dog named Patch"],
            "family_members": ["Olivia", "Ethan"],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Sunset Ridge",
        owner_email="ericsilvertx+sophie@gmail.com",
        recipient_name="Sophie Sunset",
        email="ericsilvertx+patient.sophie@gmail.com",
        phone_number="+61291550301",
        auth_image_keys=["flower", "tree", "sun"],
        preferences={
            "city_for_weather": "Sydney",
            "timezone": "Australia/Sydney",
            "delivery_time": "08:00",
            "delivery_days": [],
            "language": "en-AU",
            "date_of_birth": "1940-09-15",
            "preferred_pronoun": "she/her",
            "nationality_or_background": "Australian",
            "religion_or_faith": "Anglican",
            "life_roles": ["mother", "grandmother", "schoolteacher", "choir member"],
            "hometown": "Newcastle, NSW",
            "era_of_youth": "1950s",
            "favorite_singers": ["Shirley Bassey", "Dusty Springfield", "Petula Clark"],
            "favorite_activities": ["Knitting", "Tending her garden"],
            "hobbies": ["Reading", "Watercolour painting"],
            "favourite_foods": ["Pavlova", "Lamingtons", "Vegemite on toast"],
            "favourite_tv_shows": ["The Graham Kennedy Show", "Neighbours"],
            "pets": [],
            "family_members": ["Noah", "Maya"],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Sunset Ridge",
        owner_email="ericsilvertx+sophie@gmail.com",
        recipient_name="Noah Sunset",
        email="ericsilvertx+patient.noah@gmail.com",
        phone_number="+16025550302",
        auth_image_keys=["car", "dog", "bird"],
        preferences={
            "city_for_weather": "Phoenix, AZ",
            "timezone": "America/Phoenix",
            "delivery_time": "09:30",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1945-06-21",
            "preferred_pronoun": "he/him",
            "nationality_or_background": "American",
            "religion_or_faith": "Jewish",
            "life_roles": ["father", "accountant", "golfer"],
            "hometown": "Scottsdale, AZ",
            "era_of_youth": "1960s",
            "favorite_singers": ["Nat King Cole", "Tony Bennett", "Bobby Darin"],
            "favorite_activities": ["Playing golf", "Reading the newspaper"],
            "hobbies": ["Chess", "Cooking breakfast"],
            "favourite_foods": ["Pastrami sandwich", "Matzo ball soup", "Cheesecake"],
            "favourite_tv_shows": ["M*A*S*H", "All in the Family"],
            "pets": ["dog named Sandy"],
            "family_members": ["Sophie", "Maya"],
            "cognitive_stage": "mild",
            "mobility_level": "active",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Sunset Ridge",
        owner_email="ericsilvertx+sophie@gmail.com",
        recipient_name="Maya Sunset",
        email="ericsilvertx+patient.maya@gmail.com",
        phone_number="+13055550303",
        auth_image_keys=["cake", "flower", "house"],
        preferences={
            "city_for_weather": "Miami, FL",
            "timezone": "America/New_York",
            "delivery_time": "08:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1948-01-30",
            "preferred_pronoun": "she/her",
            "nationality_or_background": "Jamaican-American",
            "religion_or_faith": "Pentecostal",
            "life_roles": ["mother", "nurse", "community organiser", "dance teacher"],
            "hometown": "Kingston, Jamaica",
            "era_of_youth": "1960s",
            "favorite_singers": ["Harry Belafonte", "Celia Cruz", "Aretha Franklin"],
            "favorite_activities": ["Dancing", "Cooking Caribbean food"],
            "hobbies": ["Gardening", "Sewing"],
            "favourite_foods": ["Jerk chicken", "Rice and peas", "Ackee and saltfish"],
            "favourite_tv_shows": ["The Cosby Show", "Soul Train"],
            "pets": [],
            "family_members": ["Sophie", "Noah"],
            "cognitive_stage": "mild",
            "mobility_level": "active",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Maple Grove",
        owner_email="ericsilvertx+clara@gmail.com",
        recipient_name="Taylor Shared",
        email="ericsilvertx+patient.taylor@gmail.com",
        phone_number="+13125550401",
        auth_image_keys=["moon", "star", "boat"],
        preferences={
            "city_for_weather": "Chicago, IL",
            "timezone": "America/Chicago",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1943-07-04",
            "preferred_pronoun": "they/them",
            "nationality_or_background": "American",
            "religion_or_faith": "",
            "life_roles": ["parent", "librarian"],
            "hometown": "Chicago, IL",
            "era_of_youth": "1960s",
            "favorite_singers": ["Joni Mitchell", "Carole King", "James Taylor"],
            "favorite_activities": ["Reading", "Listening to folk music"],
            "hobbies": ["Jigsaw puzzles", "Crossword puzzles"],
            "favourite_foods": ["Deep dish pizza", "Chocolate chip cookies"],
            "favourite_tv_shows": ["The Carol Burnett Show", "Masterpiece Theatre"],
            "pets": [],
            "family_members": [],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Harbor Point",
        owner_email="olivia.harbor@example.com",
        recipient_name="Taylor Shared",
        email="ericsilvertx+patient.taylor@gmail.com",
        phone_number="+13125550401",
        auth_image_keys=["moon", "star", "boat"],
        preferences={
            "city_for_weather": "Chicago, IL",
            "timezone": "America/Chicago",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1943-07-04",
            "preferred_pronoun": "they/them",
            "nationality_or_background": "American",
            "religion_or_faith": "",
            "life_roles": ["parent", "librarian"],
            "hometown": "Chicago, IL",
            "era_of_youth": "1960s",
            "favorite_singers": ["Joni Mitchell", "Carole King", "James Taylor"],
            "favorite_activities": ["Reading", "Listening to folk music"],
            "hobbies": ["Jigsaw puzzles", "Crossword puzzles"],
            "favourite_foods": ["Deep dish pizza", "Chocolate chip cookies"],
            "favourite_tv_shows": ["The Carol Burnett Show", "Masterpiece Theatre"],
            "pets": [],
            "family_members": [],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
    SeedPatient(
        family_name="Sunset Ridge",
        owner_email="ericsilvertx+sophie@gmail.com",
        recipient_name="Taylor Shared",
        email="ericsilvertx+patient.taylor@gmail.com",
        phone_number="+13125550401",
        auth_image_keys=["moon", "star", "boat"],
        preferences={
            "city_for_weather": "Chicago, IL",
            "timezone": "America/Chicago",
            "delivery_time": "09:00",
            "delivery_days": [],
            "language": "en-US",
            "date_of_birth": "1943-07-04",
            "preferred_pronoun": "they/them",
            "nationality_or_background": "American",
            "religion_or_faith": "",
            "life_roles": ["parent", "librarian"],
            "hometown": "Chicago, IL",
            "era_of_youth": "1960s",
            "favorite_singers": ["Joni Mitchell", "Carole King", "James Taylor"],
            "favorite_activities": ["Reading", "Listening to folk music"],
            "hobbies": ["Jigsaw puzzles", "Crossword puzzles"],
            "favourite_foods": ["Deep dish pizza", "Chocolate chip cookies"],
            "favourite_tv_shows": ["The Carol Burnett Show", "Masterpiece Theatre"],
            "pets": [],
            "family_members": [],
            "cognitive_stage": "mild",
            "mobility_level": "walking",
            "sensory_notes": [],
        },
    ),
]


def _synthesized_preference_tags(preferences: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for key in ("era_of_youth", "hometown"):
        value = preferences.get(key)
        if value:
            tags.append(str(value))
    for key in ("favorite_activities", "hobbies", "favorite_singers", "favourite_tv_shows", "favourite_foods"):
        for value in preferences.get(key, [])[:2]:
            if value and value not in tags:
                tags.append(str(value))
    return tags[:8]


def _starter_cards(patient_name: str, preferences: dict[str, Any]) -> list[dict[str, Any]]:
    family_members = preferences.get("family_members") or []
    favorite_activities = preferences.get("favorite_activities") or []
    era = preferences.get("era_of_youth") or "years gone by"
    hometown = preferences.get("hometown") or "home"
    first_activity = favorite_activities[0] if favorite_activities else "a favorite hobby"
    family_line = ", ".join(family_members) if family_members else "family"

    return [
        {
            "provider_key": "family_greeting",
            "title": "Family hello",
            "body": f"{family_line} are thinking of {patient_name} today and sending love.",
            "card_kind": "family",
            "display_order": 1,
        },
        {
            "provider_key": "nostalgia",
            "title": "Memory lane",
            "body": f"Today could be a nice moment to talk about {hometown} and memories from the {era}.",
            "card_kind": "memory",
            "display_order": 2,
        },
        {
            "provider_key": "activity_suggestion",
            "title": "Gentle activity",
            "body": f"Try a short moment with {first_activity.lower()} or a simple conversation about it.",
            "card_kind": "activity",
            "display_order": 3,
        },
    ]


async def _get_user_by_email(session, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == email))


async def _get_user_by_username(session, username: str) -> User | None:
    return await session.scalar(select(User).where(User.username == username))


async def _get_or_create_user(session, seed_user: SeedUser) -> User:
    username = seed_user.email.lower()
    user = await _get_user_by_email(session, seed_user.email.lower())
    if user is None:
        user = await _get_user_by_username(session, username)

    if user is None:
        user = User(
            username=username,
            email=seed_user.email.lower(),
            display_name=seed_user.display_name,
            hashed_password=get_password_hash(COMMON_PASSWORD),
            is_active=True,
            auth_provider="local",
        )
        session.add(user)
        await session.flush()
        return user

    user.username = username
    user.email = seed_user.email.lower()
    user.display_name = seed_user.display_name
    user.hashed_password = get_password_hash(COMMON_PASSWORD)
    user.is_active = True
    user.auth_provider = "local"
    await session.flush()
    return user


async def _get_or_create_family(session, family_name: str, join_code: str, owner_user_id: int) -> CareCircleFamily:
    family = await session.scalar(
        select(CareCircleFamily).where(CareCircleFamily.name == family_name)
    )
    if family is None:
        family = CareCircleFamily(name=family_name, join_code=join_code, created_by_user_id=owner_user_id)
        session.add(family)
        await session.flush()
        return family

    family.created_by_user_id = owner_user_id
    family.join_code = join_code
    await session.flush()
    return family


async def _upsert_membership(
    session,
    *,
    family: CareCircleFamily,
    user: User,
    role: str,
    is_primary: bool,
) -> None:
    existing_membership = await session.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.family_id == family.id,
            CareCircleFamilyMembership.user_id == user.id,
        )
    )
    if existing_membership is None:
        existing_membership = CareCircleFamilyMembership(
            family_id=family.id,
            user_id=user.id,
            role=role,
            is_primary=is_primary,
        )
        session.add(existing_membership)
    else:
        existing_membership.role = role
        existing_membership.is_primary = is_primary
    await session.flush()


async def _reset_primary_memberships(session, user: User, primary_family_id: int) -> None:
    memberships = (
        await session.execute(
            select(CareCircleFamilyMembership).where(CareCircleFamilyMembership.user_id == user.id)
        )
    ).scalars().all()
    for membership in memberships:
        membership.is_primary = membership.family_id == primary_family_id
    await session.flush()


async def _upsert_patient(session, family: CareCircleFamily, owner_user: User, seed_patient: SeedPatient) -> CareCirclePatientProfile:
    patient = await session.scalar(
        select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.family_id == family.id,
            CareCirclePatientProfile.display_name == seed_patient.recipient_name,
        )
    )

    prefs = dict(seed_patient.preferences)
    prefs["family_members"] = list(prefs.get("family_members", []))
    prefs["preference_tags"] = _synthesized_preference_tags(prefs)

    if patient is None:
        patient = CareCirclePatientProfile(
            family_id=family.id,
            created_by_user_id=owner_user.id,
            display_name=seed_patient.recipient_name,
            family_name=seed_patient.family_name,
            email=seed_patient.email or None,
            phone_number=seed_patient.phone_number or None,
            stage=prefs.get("cognitive_stage", "mild"),
            access_state="active",
            timezone=prefs.get("timezone", "America/Chicago"),
            delivery_time=prefs.get("delivery_time"),
            delivery_days=prefs.get("delivery_days", []),
            auth_image_keys=seed_patient.auth_image_keys,
            preferences=prefs,
        )
        session.add(patient)
        await session.flush()
    else:
        patient.created_by_user_id = owner_user.id
        patient.display_name = seed_patient.recipient_name
        patient.family_name = seed_patient.family_name
        patient.email = seed_patient.email or None
        patient.phone_number = seed_patient.phone_number or None
        patient.stage = prefs.get("cognitive_stage", patient.stage)
        patient.access_state = "active"
        patient.timezone = prefs.get("timezone", patient.timezone)
        patient.delivery_time = prefs.get("delivery_time")
        patient.delivery_days = prefs.get("delivery_days", [])
        patient.auth_image_keys = seed_patient.auth_image_keys
        patient.preferences = prefs
        await session.flush()

    existing_cards = (
        await session.execute(
            select(CareCirclePatientContentCard).where(CareCirclePatientContentCard.patient_id == patient.id)
        )
    ).scalars().all()
    for card in existing_cards:
        await session.delete(card)
    await session.flush()

    for card_data in _starter_cards(seed_patient.recipient_name, prefs):
        session.add(
            CareCirclePatientContentCard(
                patient_id=patient.id,
                is_active=True,
                **card_data,
            )
        )
    await session.flush()
    return patient


async def main() -> None:
    async with async_session_local() as session:
        await ensure_provider_catalog_seeded(session)

        family_map: dict[str, CareCircleFamily] = {}
        user_map: dict[str, User] = {}

        for family_seed in FAMILIES:
            owner_seed = next(member for member in family_seed.members if member.role == "owner")
            owner_user = await _get_or_create_user(session, owner_seed)
            family = await _get_or_create_family(session, family_seed.name, family_seed.join_code, owner_user.id)
            family_map[family_seed.name] = family

            for member in family_seed.members:
                user = await _get_or_create_user(session, member)
                user_map[user.email] = user
                await _upsert_membership(
                    session,
                    family=family,
                    user=user,
                    role=member.role,
                    is_primary=member.primary_family == family.name,
                )

        shared_user = await _get_or_create_user(session, SHARED_USER)
        user_map[shared_user.email] = shared_user
        for family_name in ("Maple Grove", "Harbor Point", "Sunset Ridge"):
            await _upsert_membership(
                session,
                family=family_map[family_name],
                user=shared_user,
                role="member",
                is_primary=family_name == SHARED_USER.primary_family,
            )

        for user in user_map.values():
            memberships = (
                await session.execute(
                    select(CareCircleFamilyMembership).where(CareCircleFamilyMembership.user_id == user.id)
                )
            ).scalars().all()
            if not memberships:
                continue
            primary = next((m for m in memberships if m.is_primary), memberships[0])
            await _reset_primary_memberships(session, user, primary.family_id)

        for seed_patient in PATIENTS:
            family = family_map[seed_patient.family_name]
            owner_user = user_map[seed_patient.owner_email.lower()]
            await _upsert_patient(session, family, owner_user, seed_patient)

        await session.commit()

        memberships_count = await session.scalar(select(func.count(CareCircleFamilyMembership.id)))
        patients_count = await session.scalar(select(func.count(CareCirclePatientProfile.id)))
        families_count = await session.scalar(select(func.count(CareCircleFamily.id)))

        print("Seed complete.")
        print(f"Families: {families_count}")
        print(f"Memberships: {memberships_count}")
        print(f"Patients: {patients_count}")
        print("Login username values are the seeded email addresses.")
        print(f"Shared password: {COMMON_PASSWORD}")
        print("Join codes persisted for Maple Grove, Harbor Point, and Sunset Ridge.")


if __name__ == "__main__":
    asyncio.run(main())
