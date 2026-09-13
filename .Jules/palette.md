## 2026-07-16 - Tap-to-Copy Monospace Formatting for Payment Details
**Learning:** Telegram renders monospace backticks (`text`) as tap-to-copy text blocks on mobile clients. Cleaning internal backticks from dynamic deposit amounts prevents Markdown V1 parsing syntax failures.
**Action:** Always format sensitive transfer details (account numbers, phone numbers, exact amounts) in backticks and pass `parse_mode="Markdown"`.
