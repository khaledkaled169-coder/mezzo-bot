# Palette UX Journal

## 2026-07-16 - Dynamic Onboarding Routing on `/start`
**Learning:** Returning users who sent `/start` were re-prompted for phone contact sharing, causing unnecessary friction for registered users.
**Action:** Route users based on SQLite registration state in the `/start` handler.
