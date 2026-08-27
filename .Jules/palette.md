## 2026-07-16 - Payment Instructions Monospace Tap-to-Copy UX

**Learning:** Wrapping key numeric details (e.g., account numbers, phone numbers, clean transaction amounts) in backticks with `parse_mode="Markdown"` in Telegram messages enables native tap-to-copy functionality on mobile and desktop clients, significantly reducing friction during payment transfers.
**Action:** Always format sensitive transfer identifiers, account numbers, and amounts using inline code (monospace backticks) and ensure internal backticks are sanitized in dynamic inputs.
