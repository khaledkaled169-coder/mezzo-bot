# Palette's Journal - Critical UX & Accessibility Learnings

## 2026-07-16 - Telegram Support Menu Tap-to-Copy and Clickable Links
**Learning:** Monospace formatting (`+251...`) in Telegram bots enables instant tap-to-copy functionality for phone numbers on mobile clients. However, Telegram handles (e.g., `@mezzodeposite`) should NOT be wrapped in monospace backticks because backticks prevent Telegram clients from recognizing and hyperlinking the handle into an interactive profile link.
**Action:** Always format phone numbers, bank accounts, and transaction IDs with monospace backticks for tap-to-copy convenience, but leave `@username` handles unformatted so users can tap directly to initiate chat.
