# Architecture Notes & Incident Logging

This directory contains permanent logs of architectural decisions, root cause analyses, and systemic bug fixes for the Arete project.

## Purpose

When we encounter bugs that stem from architectural issues (like navigation role leakage, session sync problems, or data consistency issues), we document both the immediate fix and the underlying systemic changes to prevent recurrence.

## Naming Convention

Files should follow: `YYYY-MM-DD-short-description.md`

Examples:
- `2025-07-14-navigation-role-sync-fix.md`
- `2025-07-15-clerk-session-validation-hardening.md`
- `2025-07-16-database-consistency-improvements.md`

## Required Content

Each log entry must include:

- **Summary:** Plain English description of the issue and what was fixed
- **Root Cause Analysis:** Brief description of the underlying problem
- **Solution Applied:** How it was fixed (brief, non-technical OK)
- **Preventative Measures:** What changes were made to avoid recurrence (e.g., test updates, config hardening)
- **Follow-Up Notes (Optional):** Any areas flagged for future attention

## Why We Do This

- **Learning:** Understand patterns in our bugs to improve architecture
- **Prevention:** Document systemic changes that prevent similar issues
- **Collaboration:** Help team members understand past decisions and their context
- **Accountability:** Track that we're addressing root causes, not just symptoms

## Usage

This practice is triggered whenever we complete:
- Root cause analysis of a systemic bug
- Architecture decision that affects multiple components
- Preventative refactoring to eliminate entire classes of bugs

These logs are permanent and should not be overwritten in automated refactors.