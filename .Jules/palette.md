## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** In Telegram bot interfaces, users frequently need to copy bank account numbers, phone numbers, and cleaned transaction amounts to switch to payment apps (e.g. Telebirr, CBE Birr) without transcription errors.
**Action:** Always wrap payment account numbers, phone numbers, and amounts in monospace backticks (`` `...` ``) and set `parse_mode="Markdown"` (or `parse_mode="HTML"` with `<code>...</code>`) so users can tap to copy on mobile.
