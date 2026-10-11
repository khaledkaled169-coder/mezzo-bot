## 2026-07-16 - Dynamic Onboarding Routing on Telegram /start Command
**Learning:** Re-triggering initial onboarding steps (like requesting contact permissions) for already-registered users when invoking `/start` creates unnecessary friction and confusion. Routing users based on SQLite registration state directly to the main menu or missing onboarding step improves flow efficiency.
**Action:** Always check existing database state in Telegram `/start` handlers to route users directly to their relevant menu or next onboarding step.
