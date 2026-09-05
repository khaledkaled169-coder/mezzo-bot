## 2026-07-16 - Dynamic Onboarding State Routing
**Learning:** Re-triggering initial onboarding steps (like phone sharing prompts) for already registered users upon calling `/start` creates unnecessary user friction and confusion.
**Action:** Always check existing database state in command entry points like `/start` to immediately route registered users to the main interface or their next incomplete step.
