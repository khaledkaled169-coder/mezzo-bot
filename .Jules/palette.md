## 2026-07-16 - Dynamic Onboarding Routing
**Learning:** Static onboarding flows in Telegram bots cause extreme friction. Users who are already registered should never be prompted for phone numbers or ID verification again when running `/start`. Instead, the bot should detect their state and route them directly to their destination to improve retention.
**Action:** Always check the database registration state in the `/start` handler and dynamically route fully registered users to the main menu, partially registered users to the missing step, and unregistered users to the initial step.
