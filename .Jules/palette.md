# Palette's Journal - Mezzo Bot

## 2026-06-16 - Tap-to-Copy for Financial Details
**Learning:** In mobile-first Telegram bots, users frequently need to copy account numbers and amounts to their banking apps. Monospace formatting (backticks) in Telegram Markdown V1 enables "tap-to-copy" functionality, significantly reducing friction.
**Action:** Always wrap account numbers, phone numbers, and financial amounts in backticks and ensure `parse_mode="Markdown"` is used.
