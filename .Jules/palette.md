## 2026-07-16 - Dynamic Onboarding State Routing in Telegram Bots
**Learning:** Returning users executing `/start` commands experience unnecessary friction when re-prompted for information they have already provided (like phone number sharing).
**Action:** Always inspect user database state on `/start` and dynamically route fully registered users to the main menu or partially registered users directly to their missing step.
