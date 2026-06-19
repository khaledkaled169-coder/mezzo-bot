# Palette's Journal - Mezzo Bot

## 2026-06-16 - Tap-to-copy and Markdown Safety
**Learning:** Using monospace formatting for account numbers and phone numbers in Telegram bots is a critical UX pattern that enables "tap-to-copy", significantly reducing user friction during payment tasks. Additionally, escaping dynamic user-provided strings is essential when using Markdown parse mode to avoid API errors from special characters.
**Action:** Always wrap actionable data in backticks and use a helper function to escape dynamic content in Markdown messages.
