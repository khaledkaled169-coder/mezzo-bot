## 2026-07-16 - Dynamic Onboarding Routing
**Learning:** Returning users running `/start` should not be forced through the onboarding registration funnel again. Routing them dynamically based on registration state (fully registered, partially registered, unregistered) improves user retention and matches user expectations of a persistent state.
**Action:** Use database lookup in the `/start` handler to route fully registered users to the main menu, partially registered users to the Mezzo ID prompt, and unregistered users to the phone number sharing prompt.
