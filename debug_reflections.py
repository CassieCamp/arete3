import asyncio
import sys
import os
sys.path.append('./backend')
os.chdir('./backend')

from app.db.mongodb import get_database
from app.repositories.journey.reflection_repository import ReflectionSourceRepository

async def check_reflection_structure():
    repo = ReflectionSourceRepository()
    reflections = await repo.get_by_user_id('user_2znorKQkuTVCyn2VNTbZAGSA6LF')
    
    for reflection in reflections:
        print(f'\n=== Reflection {reflection.id} ===')
        print(f'Title: {reflection.title}')
        print(f'Has document_analysis: {bool(reflection.document_analysis)}')
        
        if reflection.document_analysis:
            print(f'Document analysis summary: {reflection.document_analysis.summary[:100]}...')
            print(f'Document analysis entities keys: {list(reflection.document_analysis.entities.keys()) if reflection.document_analysis.entities else "None"}')
            
            if reflection.document_analysis.entities:
                for key, value in reflection.document_analysis.entities.items():
                    print(f'  {key}: {type(value)} - {str(value)[:200]}...')

asyncio.run(check_reflection_structure())