## 2026-06-16 - Tap-to-copy Monospace Formatting
**Learning:** In Telegram bots, using monospace formatting (backticks) for critical information like phone numbers, account numbers, and transaction IDs significantly improves UX by enabling 'tap-to-copy'. However, when using Markdown V1, special characters inside backticks are not escaped, which can cause parsing errors if not sanitized.
**Action:** Always wrap dynamic data in a `clean_mono()` helper to remove internal backticks before placing it inside a monospace block, and use `esc()` for dynamic data outside of monospace blocks.
