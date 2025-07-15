from pydantic import BaseModel, Field

class UserSessionSettingsUpdate(BaseModel):
    session_auto_send_context: bool = Field(..., description="Enable or disable auto-sending of session context")