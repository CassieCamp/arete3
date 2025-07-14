from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.models.coaching_interest import CoachingInterest
from app.schemas.coaching_interest import CoachingInterestCreate
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class CoachingInterestRepository:
    def __init__(self):
        self.collection_name = "coaching_interests"

    async def create(self, submission: CoachingInterestCreate) -> CoachingInterest:
        """Save a new coaching interest submission to the database"""
        logger.info(f"=== CoachingInterestRepository.create called ===")
        logger.info(f"Input submission: {submission}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            logger.info(f"Database connection obtained: {db}")
            logger.info(f"Collection name: {self.collection_name}")
            
            # Convert Pydantic model to dict
            submission_dict = submission.dict()
            
            # Add created_at timestamp
            submission_dict["created_at"] = datetime.utcnow()
            
            # Ensure email is stored in lowercase for consistent lookups
            if "email" in submission_dict:
                original_email = submission_dict["email"]
                submission_dict["email"] = submission_dict["email"].lower()
                logger.info(f"Email normalized: {original_email} -> {submission_dict['email']}")
            
            logger.info(f"Final submission dict for insertion: {submission_dict}")
            
            logger.info("Attempting to insert coaching interest submission into database...")
            result = await db[self.collection_name].insert_one(submission_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            # Create CoachingInterest model with the inserted ID
            coaching_interest = CoachingInterest(
                id=result.inserted_id,
                **submission_dict
            )
            
            logger.info(f"✅ Successfully created coaching interest submission with ID: {coaching_interest.id}")
            return coaching_interest
            
        except Exception as e:
            logger.error(f"❌ Error in create: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_all(self) -> List[CoachingInterest]:
        """Retrieve all coaching interest submissions"""
        logger.info(f"=== CoachingInterestRepository.get_all called ===")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            logger.info(f"Querying collection: {self.collection_name}")
            
            # Find all submissions, sorted by created_at descending (newest first)
            cursor = db[self.collection_name].find({}).sort("created_at", -1)
            submissions_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(submissions_docs)} coaching interest submissions")
            
            submissions = []
            for doc in submissions_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                
                submission = CoachingInterest(**doc)
                submissions.append(submission)
            
            logger.info(f"✅ Successfully retrieved {len(submissions)} coaching interest submissions")
            return submissions
            
        except Exception as e:
            logger.error(f"❌ Error in get_all: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_by_id(self, submission_id: str) -> Optional[CoachingInterest]:
        """Get coaching interest submission by ID"""
        logger.info(f"=== CoachingInterestRepository.get_by_id called ===")
        logger.info(f"Searching for submission ID: {submission_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            submission_doc = await db[self.collection_name].find_one({"_id": ObjectId(submission_id)})
            logger.info(f"Query result: {submission_doc}")
            
            if submission_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in submission_doc and submission_doc["_id"]:
                    submission_doc["_id"] = str(submission_doc["_id"])
                
                submission = CoachingInterest(**submission_doc)
                logger.info(f"✅ Found coaching interest submission: {submission}")
                return submission
            
            logger.info("No coaching interest submission found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_by_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_by_email(self, email: str) -> List[CoachingInterest]:
        """Get coaching interest submissions by email"""
        logger.info(f"=== CoachingInterestRepository.get_by_email called ===")
        logger.info(f"Searching for email: {email}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Search with normalized email (lowercase)
            cursor = db[self.collection_name].find({"email": email.lower()}).sort("created_at", -1)
            submissions_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(submissions_docs)} submissions for email: {email}")
            
            submissions = []
            for doc in submissions_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                
                submission = CoachingInterest(**doc)
                submissions.append(submission)
            
            logger.info(f"✅ Successfully retrieved {len(submissions)} submissions for email: {email}")
            return submissions
            
        except Exception as e:
            logger.error(f"❌ Error in get_by_email: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise