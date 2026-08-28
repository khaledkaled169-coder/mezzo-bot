## 2026-07-16 - Tap-to-copy formatting for payment instructions
**Learning:** Users copying account numbers or phone numbers from payment instruction messages in Telegram frequently introduce typos when copying manually. Monospace formatting (backticks) enables single-tap copying in Telegram mobile clients.
**Action:** Always format critical payment details (account numbers, phone numbers, transaction IDs, exact amounts) in monospace backticks and ensure `parse_mode="Markdown"` is set.
