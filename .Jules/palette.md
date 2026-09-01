## 2026-07-16 - Tap-to-copy Monospace Formatting in Payment Instructions
**Learning:** In Telegram bots, displaying account numbers, transaction IDs, or exact payment amounts in plain text requires users to manually select text, creating unnecessary friction during payment transfers.
**Action:** Always format numbers and copyable text (e.g. account numbers, phone numbers, deposit amounts) using Markdown backticks (```code```) and pass `parse_mode="Markdown"` so users can tap once to copy.
