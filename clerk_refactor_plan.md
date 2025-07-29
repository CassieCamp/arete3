# Clerk Refactoring Plan

## 1. Executive Summary

This document outlines the plan to refactor the existing user management system to rely entirely on Clerk as the single source of truth. The current hybrid system, which maintains a local `users` collection in MongoDB synced from Clerk, will be deprecated. This change will simplify the architecture, reduce data redundancy, and improve maintainability.

The core of this refactoring involves:

- Migrating application-specific user data from our local `users` collection to Clerk's `publicMetadata`.
- Removing the `User` model, `user_repository.py`, and associated CRUD operations.
- Updating services and API endpoints to fetch user data directly from Clerk.
- Modifying dependent services (e.g., `ProfileService`) to use the `clerk_user_id` instead of the local MongoDB `user_id`.

## 2. Analysis of the Current System

The current user management architecture consists of the following key components:

- **`app/models/user.py`**: Defines the `User` model, which is stored in the `users` collection in MongoDB. It contains fields like `clerk_user_id`, `email`, `primary_role`, `organization_roles`, and `session_auto_send_context`.
- **`app/repositories/user_repository.py`**: Handles all database operations (CRUD) for the `users` collection.
- **`app/services/user_service.py`**: Contains business logic for user management. It currently interacts with both Clerk's API and the local `user_repository.py`. It includes logic for syncing user data from Clerk to the local database.
- **`app/api/v1/endpoints/users.py`**: Exposes user-related API endpoints. These endpoints currently rely on `user_service.py` to interact with the local user database.
- **Dependencies**: Other parts of the application, such as `ProfileService` and the `CoachingRelationship` model, have foreign key-like relationships to the local `User` model's `_id`.

This architecture introduces unnecessary complexity and potential for data inconsistency between Clerk and the local database.

## 3. Refactoring Plan

The refactoring process will be executed in the following steps:

### Step 1: Migrate User Data to Clerk `publicMetadata`

We will write a one-time migration script to move data from the local `users` collection to the corresponding user's `publicMetadata` in Clerk.

- **Fields to Migrate**:
  - `primary_role`
  - `organization_roles`
  - `session_auto_send_context`
- **Script (`migrations/migrate_user_metadata_to_clerk.py`)**:
  1. Fetch all users from the local `users` collection.
  2. For each user, call the Clerk API to update the user's `publicMetadata` with the fields listed above.
  3. Log the results of each migration.

### Step 2: Remove the Local User Model and Repository

Once the data is migrated, we can remove the components related to the local `users` collection.

- **Delete Files**:
  - `backend/app/models/user.py`
  - `backend/app/repositories/user_repository.py`
- **Update `backend/app/services/user_service.py`**:
  - Remove all methods that interact with `user_repository.py` (`get_user_by_clerk_id`, `create_user_from_clerk`, `sync_user_from_clerk`).
  - The `get_user` method should be the primary method for fetching user data, and it should fetch directly from Clerk. It should be enhanced to return the full Clerk user object, including `publicMetadata`.

### Step 3: Update Dependent Services and Models

All parts of the application that currently reference the local `user_id` must be updated to use the `clerk_user_id` instead.

- **`app/models/profile.py`**:
  - The `user_id` field should be renamed to `clerk_user_id` and its type changed to `str`.
- **`app/services/profile_service.py`**:
  - Update all methods to use `clerk_user_id` for lookups and creation.
- **Other Models**:
  - Audit any other models that have a `user_id` field (e.g., `CoachingRelationship`, `Entry`) and update them to use `clerk_user_id`. This will involve data migration for those collections as well.

### Step 4: Update API Endpoints

The API endpoints in `app/api/v1/endpoints/users.py` must be refactored to use the updated `user_service.py` and rely solely on Clerk data.

- **`GET /me`**: This endpoint should be modified to call the updated `get_user` method in `user_service.py` and return data directly from the Clerk user object.
- **Profile Endpoints**: Ensure that the profile endpoints (`GET /me/profile`, `PUT /me/profile`, `POST /me/profile`) correctly use the `clerk_user_id` from the authenticated user's session.
- **Authorization Endpoints**: The authorization logic (e.g., `check-coach-authorization`) must be updated to read roles and permissions from the Clerk user's `publicMetadata` instead of the local user record.

### Step 5: Remove Clerk Webhook for User Syncing

The Clerk webhook at `app/api/v1/webhooks/clerk.py` that handles `user.created` and `user.updated` events to sync to the local database is no longer needed and should be removed.

- **Delete Logic**: Remove the code that processes user creation and updates.
- **Update Clerk Configuration**: The webhook endpoint in the Clerk dashboard should be disabled or removed.

## 4. New Code and Modifications

- **New Migration Script**: `backend/migrations/migrate_user_metadata_to_clerk.py`
- **Modified Files**:
  - `backend/app/services/user_service.py`
  - `backend/app/api/v1/endpoints/users.py`
  - `backend/app/models/profile.py` (and other dependent models)
  - `backend/app/services/profile_service.py` (and other dependent services)
  - `backend/app/api/v1/webhooks/clerk.py`
- **Deleted Files**:
  - `backend/app/models/user.py`
  - `backend/app/repositories/user_repository.py`

## 5. Completion Criteria

The refactoring will be considered complete when:

1. All application-specific user data is successfully migrated to Clerk's `publicMetadata`.
2. The local `users` collection is no longer read from or written to by the application.
3. All user-related operations fetch data directly from Clerk.
4. All system functionality dependent on user data operates correctly with the new architecture.
5. The `users` collection is dropped from the MongoDB database.
