#!/usr/bin/env python3
"""
Test script to verify CenterIntegrationService can be imported and instantiated.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.journey import CenterIntegrationService
    from app.services.goal_service import GoalService
    from app.repositories.goal_repository import GoalRepository
    
    print("✅ Successfully imported CenterIntegrationService")
    
    # Test instantiation
    goal_repository = GoalRepository()
    goal_service = GoalService(goal_repository)
    center_integration_service = CenterIntegrationService(goal_service)
    
    print("✅ Successfully instantiated CenterIntegrationService")
    print(f"Service initialized with goal_service: {type(center_integration_service.goal_service).__name__}")
    
    # Test that placeholder methods exist
    placeholder_methods = [
        '_get_values_data',
        '_get_energy_logs_data', 
        '_get_documents_data',
        '_get_assessments_data'
    ]
    
    for method_name in placeholder_methods:
        if hasattr(center_integration_service, method_name):
            print(f"✅ Placeholder method exists: {method_name}")
        else:
            print(f"❌ Missing placeholder method: {method_name}")
    
    print("\n🎉 CenterIntegrationService is ready for integration work!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)