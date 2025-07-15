from clerk_backend_api import Clerk
from app.core.config import settings
from app.schemas.user import UserResponse
from app.models.user import User
from app.db.mongodb import get_database
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.clerk_client = Clerk()
        self.db = get_database()
        self.collection = self.db.get_collection("users")

    async def get_user(self, user_id: str) -> UserResponse | None:
        try:
            user = self.clerk_client.users.get_user(user_id)
            primary_email = next((e.email_address for e in user.email_addresses if e.id == user.primary_email_address_id), None)
            if not primary_email and user.email_addresses:
                primary_email = user.email_addresses[0].email_address

            return UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                image_url=user.image_url,
                email=primary_email
            )
        except Exception as e:
            logger.error(f"Error fetching user from Clerk: {e}")
            return None

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        user_data = await self.collection.find_one({"clerk_user_id": clerk_user_id})
        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return User(**user_data)
        return None

    async def create_user_from_clerk(self, clerk_user_id: str, email: str, primary_role: str) -> User:
        new_user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            primary_role=primary_role
        )
        result = await self.collection.insert_one(new_user.model_dump(by_alias=True, exclude=["id"]))
        new_user.id = result.inserted_id
        return new_user

    async def sync_user_from_clerk(self, clerk_user_id: str, primary_role: str) -> None:
        try:
            logger.info(f"🔄 Syncing user {clerk_user_id} from Clerk to local DB.")
            clerk_user = self.clerk_client.users.get_user(user_id=clerk_user_id)
            
            primary_email = next((e.email_address for e in clerk_user.email_addresses if e.id == clerk_user.primary_email_address_id), None)
            if not primary_email and clerk_user.email_addresses:
                primary_email = clerk_user.email_addresses[0].email_address

            if not primary_email:
                logger.error(f"❌ No email found for Clerk user {clerk_user_id}")
                return

            final_role = primary_role if primary_role != "member" else "client"
            
            await self.create_user_from_clerk(
                clerk_user_id=clerk_user_id,
                email=primary_email,
                primary_role=final_role
            )
            logger.info(f"✅ Successfully synced user {clerk_user_id} to backend.")
        except Exception as e:
            logger.error(f"❌ Failed to sync user {clerk_user_id} to backend: {e}")
