#!/usr/bin/env python3
"""
Test script to verify Journey System model imports
"""

try:
    from app.models.journey import (
        CategoryType,
        DocumentType,
        ProcessingStatus,
        ReviewStatus,
        PyObjectId,
        BaseJourneyDocument,
        UserOwnedDocument,
        ProcessableDocument,
        ReflectionSource,
        ProcessingEvent,
        Insight
    )
    
    print("✅ All imports successful!")
    print(f"✅ CategoryType has {len(CategoryType)} values")
    print(f"✅ DocumentType has {len(DocumentType)} values")
    print(f"✅ ProcessingStatus has {len(ProcessingStatus)} values")
    print(f"✅ ReviewStatus has {len(ReviewStatus)} values")
    print("✅ Base classes imported successfully")
    print("✅ ReflectionSource model imported successfully")
    print("✅ ProcessingEvent model imported successfully")
    print("✅ Insight model imported successfully")
    
    # Test enum values
    print("\nCategoryType values:")
    for cat in CategoryType:
        print(f"  - {cat.value}")
        
    print("\nDocumentType values:")
    for doc in DocumentType:
        print(f"  - {doc.value}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")