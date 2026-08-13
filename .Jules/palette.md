## 2026-07-16 - Dynamic Onboarding Routing
**Learning:** Hardcoded onboarding flows in conversational interfaces can degrade UX for returning or partially registered users. Dynamically routing users based on their registration state (unregistered, partially registered, fully registered) during `/start` prevents redundant prompts and reduces onboarding friction.
**Action:** Always inspect the user database/session state on the `/start` entry point to guide the user to their next unresolved task or directly to the main application interface.
