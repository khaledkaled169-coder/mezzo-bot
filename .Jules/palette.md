## 2026-07-16 - Dynamic Onboarding State Routing in Telegram Bot /start Handler
**Learning:** Returning users who execute `/start` experience frustration and friction if reset to the initial contact-sharing step. Inspecting user registration state in SQLite on `/start` allows smooth direct routing to the main menu for fully registered users and directly to Mezzo ID prompt for partially registered users.
**Action:** Always check user registration state in `/start` command handlers to bypass redundant onboarding steps and present appropriate options/menu directly.
