## 2026-07-16 - Tap-to-Copy Payment Instructions
**Learning:** Telegram mobile/desktop clients support single-tap copying for monospace text blocks (`code`). Wrapping payment accounts and deposit amounts in backticks reduces user copy-paste errors when initiating transfers in banking or wallet apps.
**Action:** Always format sensitive transfer details (e.g., account numbers, phone numbers, exact amounts) in monospace backticks and pass `parse_mode="Markdown"` in Telegram bot messages.
