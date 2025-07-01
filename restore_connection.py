#!/usr/bin/env python3
"""
Script to restore the connection between coach and client accounts
"""
import asyncio
import sys
import os
import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token for the coach account"""
    # This would normally come from Clerk, but for testing we'll use the coach's Clerk ID
    return "user_2z8yf2QwU5mvpGWFlwNkegdxi2m"

async def restore_connection():
    """Restore the connection between coach and client"""
    print("=== Restoring Coach-Client Connection ===")
    
    try:
        # Coach details
        coach_clerk_id = "user_2z8yf2QwU5mvpGWFlwNkegdxi2m"
        client_email = "cassandra310+client8@gmail.com"
        
        print(f"Coach ID: {coach_clerk_id}")
        print(f"Client Email: {client_email}")
        
        # Create connection request
        url = f"{API_BASE}/coaching-relationships/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {coach_clerk_id}"  # This would be a proper JWT in production
        }
        
        payload = {
            "client_email": client_email
        }
        
        print(f"\nSending POST request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            relationship_data = response.json()
            print(f"✅ Successfully created connection request!")
            print(f"Relationship ID: {relationship_data.get('id')}")
            print(f"Status: {relationship_data.get('status')}")
            
            # Now we need the client to accept the request
            relationship_id = relationship_data.get('id')
            if relationship_id:
                print(f"\n=== Client accepting the request ===")
                
                # Switch to client context
                client_clerk_id = "user_2zEbicg7TUWFHOT7rQQm1DEODjP"
                client_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {client_clerk_id}"
                }
                
                accept_url = f"{API_BASE}/coaching-relationships/{relationship_id}/respond"
                accept_payload = {
                    "status": "active"
                }
                
                print(f"Sending POST request to: {accept_url}")
                print(f"Payload: {json.dumps(accept_payload, indent=2)}")
                
                accept_response = requests.post(accept_url, json=accept_payload, headers=client_headers)
                
                print(f"Accept Response Status: {accept_response.status_code}")
                print(f"Accept Response Body: {accept_response.text}")
                
                if accept_response.status_code == 200:
                    print("✅ Client successfully accepted the connection!")
                    print("🎉 Connection restored!")
                else:
                    print("❌ Failed to accept connection")
            
        else:
            print(f"❌ Failed to create connection request")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(restore_connection())