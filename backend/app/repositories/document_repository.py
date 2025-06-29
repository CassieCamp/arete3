from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.document import Document
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self):
        self.collection_name = "documents"

    async def create_document(self, document: Document) -> Document:
        """Create a new document record"""
        logger.info(f"=== DocumentRepository.create_document called ===")
        logger.info(f"Input document: {document}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            document_dict = document.dict(by_alias=True, exclude_unset=True)
            logger.info(f"Document dict before processing: {document_dict}")
            
            # Remove the id field if it's None or empty
            if "_id" in document_dict and document_dict["_id"] is None:
                del document_dict["_id"]
                logger.info("Removed None _id field")
            
            # Ensure timestamps are set
            now = datetime.utcnow()
            document_dict["created_at"] = now
            document_dict["updated_at"] = now
            
            logger.info(f"Final document dict for insertion: {document_dict}")
            
            result = await db[self.collection_name].insert_one(document_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            document.id = result.inserted_id
            logger.info(f"✅ Successfully created document with ID: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"❌ Error in create_document: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_documents_by_user_id(self, user_id: str) -> List[Document]:
        """
        Get all documents for a specific user.
        
        Args:
            user_id: The user ID to search for
            
        Returns:
            List[Document]: List of documents for the user
        """
        logger.info(f"=== DocumentRepository.get_documents_by_user_id called ===")
        logger.info(f"user_id: {user_id}")
        
        try:
            db = await get_database()
            collection = db.documents
            
            # Find all documents for the user, sorted by created_at descending (newest first)
            cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
            documents = []
            
            async for doc_data in cursor:
                try:
                    # Convert MongoDB document to Document model
                    document = Document(**doc_data)
                    documents.append(document)
                except Exception as e:
                    logger.error(f"Error converting document {doc_data.get('_id')}: {e}")
                    continue
            
            logger.info(f"✅ Retrieved {len(documents)} documents for user {user_id}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error in get_documents_by_user_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        logger.info(f"=== DocumentRepository.get_document_by_id called ===")
        logger.info(f"Searching for document_id: {document_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            document_doc = await db[self.collection_name].find_one({"_id": ObjectId(document_id)})
            logger.info(f"Query result: {document_doc}")
            
            if document_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in document_doc and document_doc["_id"]:
                    document_doc["_id"] = str(document_doc["_id"])
                    logger.info(f"Converted ObjectId to string: {document_doc['_id']}")
                
                document = Document(**document_doc)
                logger.info(f"✅ Found document: {document}")
                return document
            
            logger.info("No document found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_document_by_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_documents_by_user_id(self, user_id: str) -> List[Document]:
        """Get all documents uploaded by a specific user"""
        logger.info(f"=== DocumentRepository.get_documents_by_user_id called ===")
        logger.info(f"Searching for documents for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)  # Sort by newest first
            document_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(document_docs)} documents for user")
            
            documents = []
            for doc in document_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                documents.append(Document(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error in get_documents_by_user_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_document(self, document_id: str, update_data: dict) -> Optional[Document]:
        """Update an existing document record"""
        logger.info(f"=== DocumentRepository.update_document called ===")
        logger.info(f"Updating document_id: {document_id} with data: {update_data}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Update result: modified_count={result.modified_count}")
            
            if result.modified_count:
                updated_document = await self.get_document_by_id(document_id)
                logger.info(f"✅ Successfully updated document")
                return updated_document
            
            logger.info("No document was updated")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in update_document: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document record from the database"""
        logger.info(f"=== DocumentRepository.delete_document called ===")
        logger.info(f"Deleting document_id: {document_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(document_id)})
            
            success = result.deleted_count > 0
            logger.info(f"Delete result: deleted_count={result.deleted_count}, success={success}")
            
            if success:
                logger.info(f"✅ Successfully deleted document")
            else:
                logger.info("No document was deleted")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in delete_document: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_documents_by_category(self, user_id: str, category: str) -> List[Document]:
        """Get documents by user ID and category"""
        logger.info(f"=== DocumentRepository.get_documents_by_category called ===")
        logger.info(f"Searching for documents for user_id: {user_id}, category: {category}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id, "category": category}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)
            document_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(document_docs)} documents for user in category")
            
            documents = []
            for doc in document_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                documents.append(Document(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(documents)} documents by category")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error in get_documents_by_category: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_processed_documents_by_user_id(self, user_id: str) -> List[Document]:
        """Get all processed documents for a user (documents with extracted text)"""
        logger.info(f"=== DocumentRepository.get_processed_documents_by_user_id called ===")
        logger.info(f"Searching for processed documents for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id, "is_processed": True}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)
            document_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(document_docs)} processed documents for user")
            
            documents = []
            for doc in document_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                documents.append(Document(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(documents)} processed documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error in get_processed_documents_by_user_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise