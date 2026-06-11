## 2026-06-11 - Bypass Onboarding for Returning Users
**Learning:** Returning users experience unnecessary friction when the `/start` command forces them through the registration flow (sharing phone number) even if they are already registered.
**Action:** Always check the database for an existing `mezzo_id` in the `/start` handler and redirect returning users directly to the main menu.
