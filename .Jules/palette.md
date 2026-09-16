## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** In Telegram bots, account numbers and amounts presented in plain text require users to manually select and copy text, which causes friction during mobile banking transfers.
**Action:** Always wrap account numbers, phone numbers, and amounts in monospace backticks (`...`) and pass `parse_mode="Markdown"` so users can tap to copy instantly.
