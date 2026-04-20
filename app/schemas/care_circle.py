from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

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
    stage: str
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


class ProviderReorderItem(BaseModel):
    provider_key: str
    display_order: int


class CareCircleProviderReorderRequest(BaseModel):
    ordering: List[ProviderReorderItem]


class CareCirclePatientCreateRequest(BaseModel):
    displayName: str = Field(min_length=1, max_length=255)
    familyName: Optional[str] = None
    stage: str = Field(default="moderate", min_length=1, max_length=50)
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
    stage: str = Field(min_length=1, max_length=50)
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
