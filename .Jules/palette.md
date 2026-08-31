## 2026-07-16 - Dynamic Onboarding Routing on Telegram Bot Start
**Learning:** Prompting already registered users to re-share their contact details when they issue the `/start` command creates unnecessary friction and confusion. Dynamic routing based on stored user registration state improves user retention and navigation ease.
**Action:** Always inspect the user's registration state in command handlers like `/start` to immediately display the main menu or direct them to the precise missing setup step.
