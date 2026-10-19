## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** Telegram renders text formatted in backticks (`code`) as monospace tap-to-copy blocks. Wrapping critical numbers (account numbers, phone numbers, exact deposit amounts) in backticks eliminates friction during mobile banking transfers.
**Action:** Always format account numbers, payment phone numbers, and amounts in backticks and pass `parse_mode="Markdown"` when presenting payment instructions in Telegram bot messages.
