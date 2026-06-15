## 2026-06-15 - Onboarding Bypass for Returning Users
**Learning:** The `/start` command should check the database for existing registration (specifically the presence of a 'mezzo_id') to bypass the onboarding flow for returning users. This reduces friction for users who accidentally restart the bot or come back after a session timeout.
**Action:** Always verify user registration status in the `/start` handler and redirect to the main menu if they are already fully onboarded.
