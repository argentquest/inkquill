from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.utils.iso_codes import LANGUAGES, COUNTRIES


class CareCircleProviderRead(BaseModel):
    providerKey: str
    label: str
    icon: Optional[str] = None
    category: str
    enabled: bool
    displayOrder: int
    patientVisible: bool
    familyVisible: bool


class CareCirclePatientHighlightRead(BaseModel):
    title: str
    body: str
    renderedHtml: Optional[str] = None
    kind: str
    providerKey: str
    displayOrder: int
    feedback: Optional[Literal["like", "dislike"]] = None


class CareCirclePatientPreferences(BaseModel):
    # Identity
    recipientName: Optional[str] = None
    preferredPronoun: Optional[str] = None
    # Location & background
    hometown: Optional[str] = None
    cityForWeather: Optional[str] = None
    eraOfYouth: Optional[str] = None
    nationalityOrBackground: Optional[str] = None
    # Health
    mobilityLevel: Optional[str] = None
    # People & relationships
    familyMembers: List[str] = Field(default_factory=list)
    lifeRoles: List[str] = Field(default_factory=list)
    pets: List[str] = Field(default_factory=list)
    # Interests
    hobbies: List[str] = Field(default_factory=list)
    favoriteActivities: List[str] = Field(default_factory=list)
    favoriteSingers: List[str] = Field(default_factory=list)
    favouriteFoods: List[str] = Field(default_factory=list)
    favouriteTvShows: List[str] = Field(default_factory=list)


class CareCirclePatientRead(BaseModel):
    id: str
    displayName: str
    familyName: str
    joinCode: str
    stage: str  # "early", "mild", "moderate", "severe"
    accessState: str
    timezone: str
    preferredLanguage: str = Field(default="en")
    country: str = Field(default="US")
    postalCode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    deliveryTime: Optional[str] = None
    days: List[str] = Field(default_factory=list)
    authImageKeys: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    preferences: CareCirclePatientPreferences = Field(default_factory=CareCirclePatientPreferences)


class CareCirclePatientDetailRead(CareCirclePatientRead):
    highlights: List[CareCirclePatientHighlightRead] = Field(default_factory=list)


class CareCirclePatientAuthCatalogItem(BaseModel):
    key: str
    label: str
    emoji: str


class CareCirclePatientLoginRequest(BaseModel):
    selected_image_keys: List[str]


class CareCircleProviderPatientConfigUpdate(BaseModel):
    is_enabled: bool = True
    custom_parameters: Optional[dict] = None
    display_order: Optional[int] = None


class CareCirclePatientProviderFeedbackUpdate(BaseModel):
    feedback: Optional[Literal["like", "dislike"]] = None


class ProviderReorderItem(BaseModel):
    provider_key: str
    display_order: int


class CareCircleProviderReorderRequest(BaseModel):
    ordering: List[ProviderReorderItem]


class CareCirclePatientCreateRequest(BaseModel):
    displayName: str = Field(min_length=1, max_length=255)
    familyName: Optional[str] = None
    stage: str = Field(default="moderate", min_length=1, max_length=50)  # "early", "mild", "moderate", "severe"
    accessState: str = Field(default="active", min_length=1, max_length=50)
    timezone: str = Field(default="America/Chicago", min_length=1, max_length=100)
    preferredLanguage: str = Field(default="en", min_length=2, max_length=10)
    country: str = Field(default="US", min_length=2, max_length=10)
    postalCode: Optional[str] = Field(default=None, max_length=32)
    deliveryTime: Optional[str] = None


class CareCirclePatientUpdateRequest(BaseModel):
    familyName: str = Field(min_length=1, max_length=255)
    joinCode: str = Field(min_length=3, max_length=20)
    displayName: str = Field(min_length=1, max_length=255)
    stage: str = Field(min_length=1, max_length=50)  # "early", "mild", "moderate", "severe"
    accessState: str = Field(min_length=1, max_length=50)
    timezone: str = Field(min_length=1, max_length=100)
    preferredLanguage: str = Field(default="en", min_length=2, max_length=10)
    country: str = Field(default="US", min_length=2, max_length=10)
    postalCode: Optional[str] = Field(default=None, max_length=32)
    deliveryTime: Optional[str] = None
    days: List[str] = Field(default_factory=list)
    authImageKeys: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    preferences: CareCirclePatientPreferences = Field(default_factory=CareCirclePatientPreferences)


class CareCircleProviderPatientConfigRead(BaseModel):
    id: int
    patient_id: int
    provider_key: str
    is_enabled: bool
    display_order: Optional[int] = None
    custom_parameters: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class JoinFamilyRequest(BaseModel):
    join_code: str = Field(min_length=3, max_length=20)


class FamilyInviteEmailRequest(BaseModel):
    email: EmailStr


class OwnerFamilySummaryRead(BaseModel):
    id: int
    name: str
    join_code: str
    active_member_count: int
    pending_request_count: int


class FamilyJoinRequestRead(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    requested_at: Optional[str] = None


class FamilyMemberRead(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    joined_at: Optional[str] = None


class AdminFamilyRead(BaseModel):
    id: int
    name: str
    join_code: str
    is_disabled: bool
    owner_user_id: Optional[int] = None
    owner_username: Optional[str] = None
    owner_display_name: Optional[str] = None
    member_count: int
    patient_count: int
    pending_requests: int
    created_at: Optional[str] = None


class AdminFamilyDisableRequest(BaseModel):
    disabled: bool
