## 2026-06-16 - [Telegram Tap-to-Copy UX]
**Learning:** Monospace formatting (backticks) in Telegram Markdown V1 serves a dual purpose: visual hierarchy and functional "tap-to-copy" behavior. For financial bots, this is a critical accessibility feature for account numbers and transaction IDs.
**Action:** Always wrap copy-sensitive financial data in monospace backticks and sanitize them using a `clean_mono` helper (removing internal backticks) to ensure the copy-paste action works reliably without rendering literal backslashes.
