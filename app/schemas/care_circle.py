from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class CareCirclePatientRead(BaseModel):
    id: str
    displayName: str
    familyName: str
    joinCode: str
    stage: str
    accessState: str
    timezone: str
    deliveryTime: Optional[str] = None
    days: List[str] = Field(default_factory=list)
    familyMembers: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    authImageKeys: List[str] = Field(default_factory=list)


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
    custom_parameters: dict = Field(default_factory=dict)
    display_order: Optional[int] = None


class ProviderReorderItem(BaseModel):
    provider_key: str
    display_order: int


class CareCircleProviderReorderRequest(BaseModel):
    ordering: List[ProviderReorderItem]


class CareCirclePatientUpdateRequest(BaseModel):
    familyName: str = Field(min_length=1, max_length=255)
    joinCode: str = Field(min_length=3, max_length=20)
    displayName: str = Field(min_length=1, max_length=255)
    stage: str = Field(min_length=1, max_length=50)
    accessState: str = Field(min_length=1, max_length=50)
    timezone: str = Field(min_length=1, max_length=100)
    deliveryTime: Optional[str] = None
    days: List[str] = Field(default_factory=list)
    familyMembers: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    authImageKeys: List[str] = Field(default_factory=list)


class CareCircleProviderPatientConfigRead(BaseModel):
    id: int
    patient_id: int
    provider_key: str
    is_enabled: bool
    display_order: Optional[int] = None
    custom_parameters: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
