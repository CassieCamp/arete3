#!/usr/bin/env python3
"""
MongoDB Database Clearing Script for Arete MVP

This script connects to the MongoDB Atlas cluster and completely clears
all collections in the specified database for a clean start.

Usage:
    python3 clear_mongodb_database.py

Configuration:
    The script reads connection details from the backend/.env file:
    - DATABASE_URL: MongoDB connection URI
    - DATABASE_NAME: Database name to clear

Safety Features:
    - Confirmation prompt before deletion
    - Lists all collections before clearing
    - Provides detailed logging of operations
    - Handles SSL connection issues gracefully
"""

import os
import sys
from typing import List, Optional
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.END}")

def print_header() -> None:
    """Print script header."""
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🗑️  MongoDB Database Clearing Script", Colors.BOLD + Colors.CYAN)
    print_colored("   Arete MVP - Clean Database Reset", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    print()

def load_environment() -> tuple[str, str]:
    """Load environment variables from backend/.env file."""
    print_colored("📁 Loading environment configuration...", Colors.BLUE)
    
    # Try to load from backend/.env
    env_path = os.path.join("backend", ".env")
    if not os.path.exists(env_path):
        print_colored(f"❌ Environment file not found: {env_path}", Colors.RED)
        print_colored("   Please ensure you're running this script from the project root directory.", Colors.YELLOW)
        sys.exit(1)
    
    load_dotenv(env_path)
    
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    if not database_url:
        print_colored("❌ DATABASE_URL not found in environment file", Colors.RED)
        sys.exit(1)
    
    if not database_name:
        print_colored("❌ DATABASE_NAME not found in environment file", Colors.RED)
        sys.exit(1)
    
    print_colored(f"✅ Environment loaded successfully", Colors.GREEN)
    print_colored(f"   Database: {database_name}", Colors.WHITE)
    print_colored(f"   Cluster: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'Unknown'}", Colors.WHITE)
    print()
    
    return database_url, database_name

def create_connection(database_url: str) -> Optional[MongoClient]:
    """Create MongoDB connection with SSL troubleshooting."""
    print_colored("🔌 Attempting to connect to MongoDB Atlas...", Colors.BLUE)
    
    # Connection options to help with SSL issues
    connection_options = {
        'serverSelectionTimeoutMS': 10000,  # 10 second timeout
        'connectTimeoutMS': 10000,
        'socketTimeoutMS': 10000,
        'retryWrites': True,
        'w': 'majority',
        'tls': True,
        'tlsAllowInvalidCertificates': True,  # Allow invalid certificates
        'tlsAllowInvalidHostnames': True,  # Allow invalid hostnames
    }
    
    try:
        # First attempt with standard connection
        print_colored("   Trying standard SSL connection...", Colors.WHITE)
        client = MongoClient(database_url, **connection_options)
        
        # Test the connection
        client.admin.command('ping')
        print_colored("✅ Connected successfully with standard SSL", Colors.GREEN)
        return client
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print_colored(f"⚠️  Standard connection failed: {str(e)[:100]}...", Colors.YELLOW)
        
        # Second attempt with relaxed SSL settings
        try:
            print_colored("   Trying connection with relaxed SSL settings...", Colors.WHITE)
            # Remove conflicting SSL options and use only tlsInsecure
            relaxed_options = {
                'serverSelectionTimeoutMS': 10000,
                'connectTimeoutMS': 10000,
                'socketTimeoutMS': 10000,
                'retryWrites': True,
                'w': 'majority',
                'tls': True,
                'tlsInsecure': True,  # Bypass all SSL verification
            }
            
            client = MongoClient(database_url, **relaxed_options)
            client.admin.command('ping')
            print_colored("✅ Connected successfully with relaxed SSL", Colors.GREEN)
            return client
            
        except Exception as e2:
            print_colored(f"❌ All connection attempts failed", Colors.RED)
            print_colored(f"   Last error: {str(e2)}", Colors.RED)
            print()
            print_colored("🔧 Troubleshooting suggestions:", Colors.YELLOW)
            print_colored("   1. Update PyMongo: pip install --upgrade pymongo", Colors.WHITE)
            print_colored("   2. Update certificates: /Applications/Python\\ 3.9/Install\\ Certificates.command", Colors.WHITE)
            print_colored("   3. Check MongoDB Atlas cluster status", Colors.WHITE)
            print_colored("   4. Verify network connectivity and firewall settings", Colors.WHITE)
            print_colored("   5. Try connecting from MongoDB Compass to test credentials", Colors.WHITE)
            return None

def list_collections(client: MongoClient, database_name: str) -> List[str]:
    """List all collections in the database."""
    print_colored("📋 Scanning database collections...", Colors.BLUE)
    
    try:
        db = client[database_name]
        collections = db.list_collection_names()
        
        if not collections:
            print_colored("   No collections found in database", Colors.YELLOW)
            return []
        
        print_colored(f"   Found {len(collections)} collections:", Colors.WHITE)
        for i, collection in enumerate(collections, 1):
            # Get document count for each collection
            try:
                count = db[collection].count_documents({})
                print_colored(f"   {i:2d}. {collection} ({count} documents)", Colors.WHITE)
            except Exception:
                print_colored(f"   {i:2d}. {collection} (count unavailable)", Colors.WHITE)
        
        print()
        return collections
        
    except Exception as e:
        print_colored(f"❌ Error listing collections: {e}", Colors.RED)
        return []

def confirm_deletion(database_name: str, collections: List[str]) -> bool:
    """Get user confirmation before deletion."""
    print_colored("⚠️  WARNING: DESTRUCTIVE OPERATION", Colors.RED + Colors.BOLD)
    print_colored(f"   This will permanently delete ALL data in database: {database_name}", Colors.RED)
    print_colored(f"   Collections to be cleared: {len(collections)}", Colors.RED)
    print()
    
    # Show collections that will be affected
    if collections:
        print_colored("📝 Collections that will be cleared:", Colors.YELLOW)
        for collection in collections:
            print_colored(f"   • {collection}", Colors.WHITE)
        print()
    
    print_colored("🔄 This action cannot be undone!", Colors.RED + Colors.BOLD)
    print()
    
    while True:
        response = input(f"{Colors.YELLOW}Type 'CLEAR DATABASE' to confirm deletion: {Colors.END}").strip()
        
        if response == "CLEAR DATABASE":
            print()
            print_colored("✅ Deletion confirmed. Proceeding...", Colors.GREEN)
            return True
        elif response.lower() in ['n', 'no', 'cancel', 'abort', 'exit']:
            print_colored("❌ Operation cancelled by user", Colors.YELLOW)
            return False
        else:
            print_colored("❌ Invalid response. Type 'CLEAR DATABASE' to confirm or 'cancel' to abort.", Colors.RED)

def clear_collections(client: MongoClient, database_name: str, collections: List[str]) -> bool:
    """Clear all collections in the database."""
    print_colored("🗑️  Starting database clearing process...", Colors.BLUE)
    
    db = client[database_name]
    cleared_count = 0
    failed_collections = []
    
    for i, collection_name in enumerate(collections, 1):
        try:
            print_colored(f"   [{i}/{len(collections)}] Clearing {collection_name}...", Colors.WHITE)
            
            # Get document count before deletion
            before_count = db[collection_name].count_documents({})
            
            # Drop the collection (faster than deleting documents)
            db[collection_name].drop()
            
            print_colored(f"   ✅ Cleared {collection_name} ({before_count} documents)", Colors.GREEN)
            cleared_count += 1
            
        except Exception as e:
            print_colored(f"   ❌ Failed to clear {collection_name}: {e}", Colors.RED)
            failed_collections.append(collection_name)
    
    print()
    
    # Summary
    if cleared_count == len(collections):
        print_colored(f"🎉 Successfully cleared all {cleared_count} collections!", Colors.GREEN + Colors.BOLD)
        return True
    else:
        print_colored(f"⚠️  Partially completed: {cleared_count}/{len(collections)} collections cleared", Colors.YELLOW)
        if failed_collections:
            print_colored(f"   Failed collections: {', '.join(failed_collections)}", Colors.RED)
        return False

def main():
    """Main script execution."""
    print_header()
    
    try:
        # Load environment
        database_url, database_name = load_environment()
        
        # Create connection
        client = create_connection(database_url)
        if not client:
            sys.exit(1)
        
        # List collections
        collections = list_collections(client, database_name)
        
        if not collections:
            print_colored("✅ Database is already empty. Nothing to clear.", Colors.GREEN)
            return
        
        # Get confirmation
        if not confirm_deletion(database_name, collections):
            return
        
        # Clear collections
        success = clear_collections(client, database_name, collections)
        
        # Final verification
        print_colored("🔍 Verifying database state...", Colors.BLUE)
        remaining_collections = list_collections(client, database_name)
        
        if not remaining_collections:
            print_colored("✅ Database successfully cleared! All collections removed.", Colors.GREEN + Colors.BOLD)
        else:
            print_colored(f"⚠️  Warning: {len(remaining_collections)} collections still exist", Colors.YELLOW)
        
    except KeyboardInterrupt:
        print_colored("\n❌ Operation cancelled by user (Ctrl+C)", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    finally:
        try:
            if 'client' in locals():
                client.close()
                print_colored("\n🔌 Database connection closed", Colors.BLUE)
        except:
            pass
    
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🏁 Script execution completed", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

if __name__ == "__main__":
    main()