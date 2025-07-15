from pydantic import BaseModel, Field
from typing import Optional

class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    image_url: str = Field(..., description="User's profile image URL")
    email: str = Field(..., description="User's primary email address")