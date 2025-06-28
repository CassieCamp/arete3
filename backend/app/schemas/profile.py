from pydantic import BaseModel
from typing import List, Optional


class CoachDataSchema(BaseModel):
    specialties: List[str]
    experience: int
    philosophy: str


class ClientDataSchema(BaseModel):
    background: str
    challenges: List[str]


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


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    coach_data: Optional[CoachDataSchema] = None
    client_data: Optional[ClientDataSchema] = None
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