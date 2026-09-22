## 2026-07-16 - State-Aware Telegram Onboarding Routing
**Learning:** Forcing registered users to re-share contacts or re-enter onboarding steps on `/start` adds unnecessary friction and degrades user experience.
**Action:** Always check user registration state in SQLite database on `/start` command to dynamically route fully registered users to the main menu and partially registered users directly to missing step prompts.
