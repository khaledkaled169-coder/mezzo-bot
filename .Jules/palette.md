## 2026-07-16 - Formatting Telegram Withdrawal Instructions
**Learning:** Monospace formatting (`500`) on numerical values like minimum withdrawal amounts enables tap-to-copy functionality and provides quick visual scannability on Telegram mobile interfaces.
**Action:** Always wrap key numeric limits and transaction details in monospace backticks and ensure `parse_mode="Markdown"` is supplied to `edit_message_text`.
