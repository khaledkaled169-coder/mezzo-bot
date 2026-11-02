# Palette UX Journal

## 2026-07-16 - Tap-to-copy phone numbers in Telegram bot support menu
**Learning:** Monospace formatting (using backticks in Telegram Markdown) enables one-tap copy functionality on mobile devices for credentials and phone numbers. However, wrapping handles like `@username` in backticks disables Telegram's automatic handle detection and prevents users from directly tapping to chat.
**Action:** Use monospace formatting for numerical phone numbers and account identifiers to allow instant tap-to-copy, while leaving Telegram handles (`@username`) unescaped outside code blocks so they remain clickable links.
