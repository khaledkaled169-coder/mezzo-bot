## 2026-07-16 - Tap-to-Copy Formatting for Payment Details
**Learning:** In Telegram bot interfaces, presenting key numerical data (such as bank account numbers, phone numbers, and deposit amounts) inside monospace backticks (`` `...` ``) with `parse_mode="Markdown"` enables one-tap copying in mobile clients, significantly reducing typing friction during payment steps.
**Action:** Always format account numbers, reference codes, and transfer amounts as monospace text in bot messages where users need to copy details into banking or mobile money apps.
