from pydantic import BaseModel, EmailStr, validator


class CoachingInterestCreate(BaseModel):
    name: str
    email: EmailStr
    goals: str
    email_permission: bool
    
    @validator('email_permission')
    def email_permission_must_be_true(cls, v):
        if not v:
            raise ValueError('Email permission must be granted to proceed')
        return v
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('goals')
    def goals_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Goals cannot be empty')
        return v.strip()