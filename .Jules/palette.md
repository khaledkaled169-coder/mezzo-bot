## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** Users transferring money via mobile banking apps (Telebirr, CBE) often make typos or experience friction when retyping account numbers, phone numbers, or exact payment amounts from Telegram bot messages.
**Action:** Always wrap payment account numbers, recipient phone numbers, and cleaned transaction amounts in monospace backticks (`` `...` ``) and send with `parse_mode="Markdown"` to allow single-tap copying on Telegram clients.
