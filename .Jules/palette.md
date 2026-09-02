# Palette's UX Journal

## 2026-07-16 - Smart Onboarding Routing in /start Handler
**Learning:** Returning or already registered users triggering the `/start` command experienced unnecessary UX friction when re-prompted to share their phone number or re-enter details.
**Action:** Always check existing database state in the `/start` handler to dynamically route users (show main menu for fully registered users, prompt for Mezzo ID for partially registered users, or request contact for new users).
