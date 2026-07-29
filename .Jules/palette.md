## 2026-07-16 - Registration Routing UX
**Learning:** Dynamic routing in the Telegram bot's /start command prevents users who are already fully or partially registered from getting stuck in an infinite prompt loop or seeing a confusing welcome screen when they just want to access the main menu.
**Action:** Check the registration state of the user (fully registered, registered with phone only, or unregistered) inside `/start` and route them accordingly to avoid UX friction.
