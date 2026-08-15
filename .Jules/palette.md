## 2026-07-16 - Dynamic Onboarding Route for /start Command
**Learning:** Re-triggering initial registration prompts for already registered users upon typing /start creates friction and user confusion.
**Action:** Check user registration status in DB during /start command handling and dynamically route registered users directly to the main menu or relevant step.
