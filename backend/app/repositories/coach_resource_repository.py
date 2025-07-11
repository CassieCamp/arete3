from typing import List, Optional, Dict, Any
from app.models.coach_resource import CoachResource, CoachClientNote
from app.db.mongodb import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CoachResourceRepository:
    def __init__(self):
        self.resources_collection_name = "coach_resources"
        self.notes_collection_name = "coach_client_notes"

    # Coach Resources methods
    async def create_resource(self, resource: CoachResource) -> CoachResource:
        """Create a new coach resource"""
        try:
            db = get_database()
            resource_dict = resource.model_dump(by_alias=True, exclude={"id"})
            
            # Remove the id field if it's None or empty
            if "_id" in resource_dict and resource_dict["_id"] is None:
                del resource_dict["_id"]
            
            result = await db[self.resources_collection_name].insert_one(resource_dict)
            
            # Fetch the created resource
            created_resource = await db[self.resources_collection_name].find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for Pydantic model
            if created_resource and "_id" in created_resource:
                created_resource["_id"] = str(created_resource["_id"])
            
            return CoachResource(**created_resource)
            
        except Exception as e:
            logger.error(f"Error creating coach resource: {e}")
            raise

    async def get_resource_by_id(self, resource_id: str) -> Optional[CoachResource]:
        """Get coach resource by ID"""
        try:
            if not ObjectId.is_valid(resource_id):
                return None
                
            db = get_database()
            resource_data = await db[self.resources_collection_name].find_one({"_id": ObjectId(resource_id)})
            
            if resource_data:
                # Convert ObjectId to string for Pydantic model
                resource_data["_id"] = str(resource_data["_id"])
                return CoachResource(**resource_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching coach resource {resource_id}: {e}")
            return None

    async def get_resources_by_coach(
        self, 
        coach_user_id: str, 
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        is_template: Optional[bool] = None
    ) -> List[CoachResource]:
        """Get resources for a coach with optional filters"""
        try:
            db = get_database()
            
            query = {"coach_user_id": coach_user_id, "active": True}
            if category:
                query["category"] = category
            if resource_type:
                query["resource_type"] = resource_type
            if is_template is not None:
                query["is_template"] = is_template
            
            cursor = db[self.resources_collection_name].find(query).sort("created_at", -1)
            
            resources = []
            async for resource_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in resource_data:
                    resource_data["_id"] = str(resource_data["_id"])
                resources.append(CoachResource(**resource_data))
            
            return resources
            
        except Exception as e:
            logger.error(f"Error fetching resources for coach {coach_user_id}: {e}")
            return []

    async def get_client_specific_resources(self, coach_user_id: str, client_user_id: str) -> List[CoachResource]:
        """Get resources specific to a client"""
        try:
            db = get_database()
            cursor = db[self.resources_collection_name].find({
                "coach_user_id": coach_user_id,
                "client_specific": True,
                "target_client_id": client_user_id,
                "active": True
            }).sort("created_at", -1)
            
            resources = []
            async for resource_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in resource_data:
                    resource_data["_id"] = str(resource_data["_id"])
                resources.append(CoachResource(**resource_data))
            
            return resources
            
        except Exception as e:
            logger.error(f"Error fetching client-specific resources for coach {coach_user_id}, client {client_user_id}: {e}")
            return []

    async def get_template_resources(self, coach_user_id: str) -> List[CoachResource]:
        """Get template resources for a coach"""
        try:
            db = get_database()
            cursor = db[self.resources_collection_name].find({
                "coach_user_id": coach_user_id,
                "is_template": True,
                "active": True
            }).sort("created_at", -1)
            
            resources = []
            async for resource_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in resource_data:
                    resource_data["_id"] = str(resource_data["_id"])
                resources.append(CoachResource(**resource_data))
            
            return resources
            
        except Exception as e:
            logger.error(f"Error fetching template resources for coach {coach_user_id}: {e}")
            return []

    async def update_resource(self, resource_id: str, update_data: Dict[str, Any]) -> Optional[CoachResource]:
        """Update coach resource"""
        try:
            if not ObjectId.is_valid(resource_id):
                return None
            
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.resources_collection_name].update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_resource_by_id(resource_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating coach resource {resource_id}: {e}")
            return None

    async def delete_resource(self, resource_id: str) -> bool:
        """Delete coach resource (soft delete by setting active=False)"""
        try:
            if not ObjectId.is_valid(resource_id):
                return False
            
            db = get_database()
            result = await db[self.resources_collection_name].update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting coach resource {resource_id}: {e}")
            return False

    # Coach Client Notes methods
    async def create_client_note(self, note: CoachClientNote) -> CoachClientNote:
        """Create or update coach-client notes"""
        try:
            db = get_database()
            
            # Check if notes already exist for this coach-client pair
            existing_note = await db[self.notes_collection_name].find_one({
                "coach_user_id": note.coach_user_id,
                "client_user_id": note.client_user_id
            })
            
            if existing_note:
                # Update existing notes
                note_dict = note.model_dump(exclude={"id", "created_at"})
                note_dict["updated_at"] = datetime.utcnow()
                
                await db[self.notes_collection_name].update_one(
                    {"_id": existing_note["_id"]},
                    {"$set": note_dict}
                )
                
                # Return updated note
                updated_note = await db[self.notes_collection_name].find_one({"_id": existing_note["_id"]})
                updated_note["_id"] = str(updated_note["_id"])
                return CoachClientNote(**updated_note)
            else:
                # Create new notes
                note_dict = note.model_dump(by_alias=True, exclude={"id"})
                
                if "_id" in note_dict and note_dict["_id"] is None:
                    del note_dict["_id"]
                
                result = await db[self.notes_collection_name].insert_one(note_dict)
                
                # Fetch the created note
                created_note = await db[self.notes_collection_name].find_one({"_id": result.inserted_id})
                created_note["_id"] = str(created_note["_id"])
                return CoachClientNote(**created_note)
            
        except Exception as e:
            logger.error(f"Error creating/updating coach client note: {e}")
            raise

    async def get_client_note(self, coach_user_id: str, client_user_id: str) -> Optional[CoachClientNote]:
        """Get coach-client notes"""
        try:
            db = get_database()
            note_data = await db[self.notes_collection_name].find_one({
                "coach_user_id": coach_user_id,
                "client_user_id": client_user_id
            })
            
            if note_data:
                # Convert ObjectId to string for Pydantic model
                note_data["_id"] = str(note_data["_id"])
                return CoachClientNote(**note_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching coach client note for coach {coach_user_id}, client {client_user_id}: {e}")
            return None

    async def get_all_client_notes_for_coach(self, coach_user_id: str) -> List[CoachClientNote]:
        """Get all client notes for a coach"""
        try:
            db = get_database()
            cursor = db[self.notes_collection_name].find({"coach_user_id": coach_user_id}).sort("updated_at", -1)
            
            notes = []
            async for note_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in note_data:
                    note_data["_id"] = str(note_data["_id"])
                notes.append(CoachClientNote(**note_data))
            
            return notes
            
        except Exception as e:
            logger.error(f"Error fetching all client notes for coach {coach_user_id}: {e}")
            return []

    async def update_client_note(self, coach_user_id: str, client_user_id: str, update_data: Dict[str, Any]) -> Optional[CoachClientNote]:
        """Update coach-client notes"""
        try:
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.notes_collection_name].update_one(
                {
                    "coach_user_id": coach_user_id,
                    "client_user_id": client_user_id
                },
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_client_note(coach_user_id, client_user_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating coach client note: {e}")
            return None

    async def delete_client_note(self, coach_user_id: str, client_user_id: str) -> bool:
        """Delete coach-client notes"""
        try:
            db = get_database()
            result = await db[self.notes_collection_name].delete_one({
                "coach_user_id": coach_user_id,
                "client_user_id": client_user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting coach client note: {e}")
            return False