## 2026-07-16 - Dynamic Onboarding Routing on `/start` Command
**Learning:** Re-prompting returning users for phone numbers or registration credentials when invoking `/start` creates significant onboarding friction. By checking existing registration state dynamically, users can bypass redundant onboarding steps seamlessly.
**Action:** Always check existing database state in initial entry point handlers like `/start` to route registered users directly to the main interface or their relevant completion step.
