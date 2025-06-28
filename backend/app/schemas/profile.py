from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class CoachDataSchema(BaseModel):
    specialties: List[str]
    experience: int
    philosophy: str


class ClientDataSchema(BaseModel):
    background: str
    challenges: List[str]


class OrganizationDataSchema(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None  # For client organizations
    department: Optional[str] = None  # For client organizations
    is_solo_practice: Optional[bool] = True  # For coach organizations


class CoachProfileCreateRequest(BaseModel):
    first_name: str
    last_name: str
    coach_data: CoachDataSchema
    organization: OrganizationDataSchema


class ClientProfileCreateRequest(BaseModel):
    first_name: str
    last_name: str
    client_data: ClientDataSchema
    organization: OrganizationDataSchema


class ProfileCreateRequest(BaseModel):
    first_name: str
    last_name: str
    coach_data: Optional[CoachDataSchema] = None
    client_data: Optional[ClientDataSchema] = None


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    coach_data: Optional[CoachDataSchema] = None
    client_data: Optional[ClientDataSchema] = None


class OrganizationResponse(BaseModel):
    clerk_org_id: str
    name: str
    role: str
    metadata: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    clerk_user_id: str
    first_name: str
    last_name: str
    coach_data: Optional[CoachDataSchema] = None
    client_data: Optional[ClientDataSchema] = None
    primary_organization_id: Optional[str] = None
    organization: Optional[OrganizationResponse] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    clerk_user_id: str
    email: str
    role: str
    created_at: str

    class Config:
        from_attributes = True