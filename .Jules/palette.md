## 2026-07-16 - [Tap-to-Copy for Financial Friction]
**Learning:** Monospace formatting (backticks) in Telegram enables 'tap-to-copy' functionality, which is critical for reducing friction when users need to copy account numbers, transaction IDs, or specific amounts for banking apps.
**Action:** Always wrap account numbers, phone numbers, and payment amounts in backticks to improve the user experience during payment flows.

## 2026-07-16 - [Dynamic Monospace Sanitization]
**Learning:** Telegram's Markdown V1 treats backticks as literal blocks. If dynamic data (like a user-provided name or amount) contains a backtick, it breaks the formatting.
**Action:** Use a helper like `clean_mono()` to remove internal backticks and handle `None` values before placing dynamic strings inside monospace blocks.
