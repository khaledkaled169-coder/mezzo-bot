## 2026-07-16 - Dynamic Bot Onboarding State Routing
**Learning:** Returning Telegram bot users should not be forced through onboarding prompts repeatedly. Routing users directly to the main menu when registered or resuming exact onboarding steps improves flow continuity and reduces user friction.
**Action:** Inspect user registration state in `/start` handlers and dynamically route fully registered users to main navigation or resume incomplete onboarding steps appropriately.
