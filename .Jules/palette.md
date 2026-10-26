## 2026-07-16 - Monospace Tap-to-Copy for Payment Instructions
**Learning:** Telegram clients render text wrapped in backticks (monospace) with a tap-to-copy interaction on mobile, reducing friction when users need to transfer numbers (e.g. account numbers, phone numbers, exact payment amounts) into banking apps like Telebirr or CBE.
**Action:** Always wrap payment details, account/phone numbers, transaction IDs, and exact numerical amounts in monospace backticks in Telegram bot messages. Ensure parse_mode="Markdown" or parse_mode="HTML" is explicitly set.
