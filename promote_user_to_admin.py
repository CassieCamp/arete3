#!/usr/bin/env python3
"""
Script to promote cassandra310+jamie@gmail.com from 'member' to 'admin' role
This simulates the role change that would be done in the Clerk dashboard
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
if not CLERK_SECRET_KEY:
    print("❌ CLERK_SECRET_KEY not found in environment")
    exit(1)

# User to promote
USER_EMAIL = "cassandra310+jamie@gmail.com"
USER_ID = "user_2znorKQkuTVCyn2VNTbZAGSA6LF"  # From the backend logs

def update_user_role():
    """Update user's primary_role from 'member' to 'admin' in Clerk publicMetadata"""
    
    url = f"https://api.clerk.com/v1/users/{USER_ID}"
    
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, get current user data
    print(f"🔍 Fetching current user data for {USER_EMAIL}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch user: {response.status_code} - {response.text}")
        return False
    
    user_data = response.json()
    current_metadata = user_data.get('public_metadata', {})
    current_role = current_metadata.get('primary_role', 'member')
    
    print(f"📋 Current role: {current_role}")
    
    if current_role == 'admin':
        print("✅ User is already an admin!")
        return True
    
    # Update the role to admin
    print(f"🔄 Promoting user from '{current_role}' to 'admin'...")
    
    updated_metadata = {**current_metadata, 'primary_role': 'admin'}
    
    update_data = {
        "public_metadata": updated_metadata
    }
    
    response = requests.patch(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ Successfully promoted user to admin!")
        print(f"📧 User: {USER_EMAIL}")
        print(f"🆔 User ID: {USER_ID}")
        print(f"🎭 New role: admin")
        return True
    else:
        print(f"❌ Failed to update user: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Starting user role promotion...")
    print("=" * 50)
    
    success = update_user_role()
    
    print("=" * 50)
    if success:
        print("✅ Role promotion completed successfully!")
        print("\n📝 Next steps:")
        print("1. User should now have 'admin' role in Clerk")
        print("2. When they refresh their session, JWT will contain new role")
        print("3. They should gain access to admin pages")
    else:
        print("❌ Role promotion failed!")