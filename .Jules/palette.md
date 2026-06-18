## 2026-06-16 - Tap-to-Copy vs Clickability in Telegram
**Learning:** Wrapping sensitive data like account numbers in monospace backticks enables "tap-to-copy" in Telegram, which is a great UX win. However, wrapping Telegram handles (e.g., @username) in backticks makes them non-clickable in many clients, causing a regression.
**Action:** Use monospace for numbers/IDs only. Ensure support handles remain as plain text to preserve clickability. Always include `parse_mode="Markdown"` when using these styles.
