from pydantic import BaseModel


class UserSessionSettingsUpdate(BaseModel):
    session_auto_send_context: bool