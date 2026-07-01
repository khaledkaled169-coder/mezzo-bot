## 2026-06-16 - Improving Onboarding & Data Formatting
**Learning:** Returning users shouldn't be forced through onboarding. Formatting phone numbers and IDs as monospace in Telegram messages enables "tap-to-copy," a significant UX win for manual payment flows. Always escape dynamic user data (first names, usernames) outside of monospace blocks to prevent Markdown V1 parsing errors.
**Action:** Implement registration checks in /start handlers and use `clean_mono()` / `esc()` helpers for all dynamic Telegram UI strings.
