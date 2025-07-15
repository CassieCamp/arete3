#!/usr/bin/env python3
"""
Check Clerk publicMetadata for user cassandra310+morgan@gmail.com
to verify what role is actually stored as source of truth
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
USER_ID = 'user_2zqiKLR8NWeoMLtxm4PYxO7qeYu'

def check_clerk_user_metadata():
    """Check what's actually stored in Clerk publicMetadata"""
    
    if not CLERK_SECRET_KEY:
        print("❌ CLERK_SECRET_KEY not found in environment")
        return
    
    url = f"https://api.clerk.com/v1/users/{USER_ID}"
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        
        print(f"🔍 **Clerk User Data for {USER_ID}:**")
        print(f"📧 Email: {user_data.get('email_addresses', [{}])[0].get('email_address', 'N/A')}")
        print(f"🏷️  **publicMetadata**: {json.dumps(user_data.get('public_metadata', {}), indent=2)}")
        print(f"🔒 **privateMetadata**: {json.dumps(user_data.get('private_metadata', {}), indent=2)}")
        print(f"🔧 **unsafeMetadata**: {json.dumps(user_data.get('unsafe_metadata', {}), indent=2)}")
        
        # Check specifically for role data
        public_meta = user_data.get('public_metadata', {})
        primary_role = public_meta.get('primary_role')
        roles = public_meta.get('roles', [])
        
        print(f"\n✅ **ROLE ANALYSIS:**")
        print(f"   Primary Role: {primary_role}")
        print(f"   Roles Array: {roles}")
        
        if primary_role == 'coach':
            print("✅ Clerk publicMetadata shows correct 'coach' role")
            print("🔄 **NEXT STEP**: Test session invalidation (sign out/in)")
        elif primary_role:
            print(f"❌ Clerk publicMetadata shows incorrect role: '{primary_role}'")
            print("🔧 **NEXT STEP**: Update Clerk publicMetadata to 'coach'")
        else:
            print("❌ No primary_role found in Clerk publicMetadata")
            print("🔧 **NEXT STEP**: Set primary_role to 'coach' in Clerk")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Clerk user data: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    check_clerk_metadata()