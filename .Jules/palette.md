## 2026-06-16 - Onboarding Bypass for Returning Users
**Learning:** Forcing registered users to re-share their contact info or re-enter IDs during the `/start` command creates unnecessary friction.
**Action:** Always check for existing registration data (e.g., `mezzo_id`) in the `/start` handler and redirect returning users directly to the main interface.
