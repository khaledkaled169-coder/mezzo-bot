## 2026-07-16 - Dynamic Onboarding Command Routing
**Learning:** Returning or registered users who run `/start` out of habit or as a reset mechanism should not be forced into re-sharing contacts/credentials, but instead dynamically routed based on database state.
**Action:** Inspect user records in `/start` command handlers: immediately present main menu navigation for fully registered users, and directly resume missing registration steps (e.g., Mezzo ID) for partially registered users while removing contact reply keyboards.
