## 2026-06-16 - [Tap-to-copy for Financial and Contact Information]
**Learning:** In Telegram bot interfaces, wrapping financial details (account numbers, amounts) and contact information (phone numbers) in monospace backticks (`` ` ``) enables "tap-to-copy" functionality. This significantly reduces friction for users performing payments or seeking support.
**Action:** Always use monospace formatting for sensitive or actionable alphanumeric data in Telegram bots, and ensure dynamic data is sanitized using a `clean_mono` helper and protected with a Markdown escape function like `esc`.
