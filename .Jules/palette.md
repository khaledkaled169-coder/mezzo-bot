## 2026-06-08 - Skip Onboarding for Returning Users
**Learning:** Returning users experience friction if forced through the onboarding flow (sharing phone number and Mezzo ID) every time they use the `/start` command. Checking for existing registration data (e.g., `mezzo_id`) allows for a smoother "fast-path" directly to the main interface.
**Action:** Always check the database for existing user records in the `/start` handler to determine if the onboarding flow can be bypassed.
