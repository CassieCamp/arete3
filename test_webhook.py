#!/usr/bin/env python3
"""
Test script to simulate a Clerk webhook call
"""
import requests
import json
import hmac
import hashlib

# Sample Clerk user.created webhook payload
webhook_payload = {
    "data": {
        "id": "user_test123456789",
        "email_addresses": [
            {
                "id": "idn_test123",
                "email_address": "testuser@example.com"
            }
        ],
        "primary_email_address_id": "idn_test123",
        "first_name": "Test",
        "last_name": "User"
    },
    "object": "event",
    "type": "user.created"
}

def generate_signature(payload_bytes, secret):
    """Generate a valid Clerk webhook signature"""
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return f"v1,{signature}"

def test_webhook():
    """Send a test webhook to our local server"""
    url = "http://localhost:8000/api/v1/webhooks/clerk"
    
    # Convert payload to bytes for signature generation
    payload_json = json.dumps(webhook_payload, separators=(',', ':'))
    payload_bytes = payload_json.encode('utf-8')
    
    # Use the actual webhook secret from the environment
    webhook_secret = "whsec_GQW45/DF85Lo7FfLoxdtKUz3AoDVzZoA"
    signature = generate_signature(payload_bytes, webhook_secret)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Svix-Webhooks/1.0",
        "svix-signature": signature
    }
    
    try:
        print("Sending test webhook to:", url)
        print("Payload:", json.dumps(webhook_payload, indent=2))
        print("Signature:", signature)
        
        response = requests.post(url, data=payload_bytes, headers=headers)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"Error sending webhook: {e}")

if __name__ == "__main__":
    test_webhook()