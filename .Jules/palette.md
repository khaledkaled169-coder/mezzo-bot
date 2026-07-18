## 2026-07-16 - Tap-to-Copy Payments Improvement
**Learning:** Monospace formatting (backticks) in Telegram messages converts account numbers and deposit amounts into easily copyable fields (tap-to-copy), drastically reducing user friction and spelling errors during manual banking transactions.
**Action:** Always format critical numeric data, account details, and reference IDs in Telegram bot notifications using monospace blocks and sanitize the input with `clean_mono` to avoid parsing/formatting crashes.
