from typing import List, Optional

from pydantic import BaseModel, Field


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
    kind: str
    providerKey: str
    displayOrder: int


class CareCirclePatientRead(BaseModel):
    id: str
    displayName: str
    familyName: str
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
