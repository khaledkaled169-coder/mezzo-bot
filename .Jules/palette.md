## 2026-07-16 - Monospace tap-to-copy formatting for payment details
**Learning:** In Telegram mobile clients, wrapping numerical values like account numbers, phone numbers, and payment amounts in monospace backticks (`code`) enables single-tap copying, drastically reducing manual entry friction and copy-paste errors for user transactions.
**Action:** Always format sensitive transfer identifiers, account numbers, and transaction amounts with monospace backticks in Telegram bot messages, ensuring `parse_mode="Markdown"` is enabled.
