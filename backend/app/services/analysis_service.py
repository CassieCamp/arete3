from typing import List, Optional
from app.models.client_baseline import ClientBaseline
from app.repositories.baseline_repository import BaselineRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ai_service import AIService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, baseline_repository: BaselineRepository, document_repository: DocumentRepository):
        self.baseline_repository = baseline_repository
        self.document_repository = document_repository
        self.ai_service = AIService()
    
    async def generate_client_baseline(
        self, 
        user_id: str, 
        clerk_user_id: str,
        generated_by: str,
        document_ids: Optional[List[str]] = None
    ) -> ClientBaseline:
        """
        Generate a client baseline from their uploaded documents.
        """
        try:
            logger.info(f"=== AnalysisService.generate_client_baseline called ===")
            logger.info(f"user_id: {user_id}, generated_by: {generated_by}")
            
            # Get user's documents
            if document_ids:
                documents = []
                for doc_id in document_ids:
                    doc = await self.document_repository.get_document_by_id(doc_id)
                    if doc and doc.user_id == user_id:  # Security check
                        documents.append(doc)
            else:
                documents = await self.document_repository.get_documents_by_user_id(user_id)
            
            if not documents:
                raise ValueError("No documents found for analysis")
            
            # Filter to processed documents with extracted text
            processed_docs = [doc for doc in documents if doc.is_processed and doc.extracted_text]
            
            if not processed_docs:
                raise ValueError("No processed documents with extracted text found")
            
            # Limit number of documents
            if len(processed_docs) > settings.baseline_max_documents:
                processed_docs = sorted(processed_docs, key=lambda x: x.created_at, reverse=True)
                processed_docs = processed_docs[:settings.baseline_max_documents]
                logger.info(f"Limited analysis to {settings.baseline_max_documents} most recent documents")
            
            # Prepare document content for AI analysis
            documents_text = []
            for doc in processed_docs:
                documents_text.append({
                    "document_id": str(doc.id),
                    "filename": doc.file_name,
                    "content": doc.extracted_text,
                    "category": doc.category.value if hasattr(doc.category, 'value') else str(doc.category)
                })
            
            # Create pending baseline record
            pending_baseline = ClientBaseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                executive_summary="Baseline generation in progress...",
                status="processing",
                source_document_ids=[str(doc.id) for doc in processed_docs],
                analysis_scope=f"Processing {len(processed_docs)} documents",
                generated_by=generated_by
            )
            
            # Save pending baseline
            saved_baseline = await self.baseline_repository.create_baseline(pending_baseline)
            logger.info(f"Created pending baseline with ID: {saved_baseline.id}")
            
            # Generate baseline using AI
            completed_baseline = await self.ai_service.generate_client_baseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                documents_text=documents_text,
                generated_by=generated_by
            )
            
            # Update the baseline with results
            completed_baseline.id = saved_baseline.id
            updated_baseline = await self.baseline_repository.update_baseline(
                str(saved_baseline.id),
                completed_baseline.model_dump(exclude={"id"})
            )
            
            logger.info(f"✅ Successfully generated baseline for user {user_id}")
            return updated_baseline
            
        except Exception as e:
            logger.error(f"❌ Error in generate_client_baseline: {e}")
            raise