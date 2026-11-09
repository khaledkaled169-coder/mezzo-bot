# Palette's Journal - Critical Learnings Only

## 2026-07-16 - Tap-to-Copy Phone Numbers vs Clickable Telegram Handles
**Learning:** In Telegram bots using Markdown V1, enclosing contact phone numbers in monospace backticks (`` `+251712759695` ``) enables one-tap copy functionality on mobile devices without requiring manual selection. However, wrapping Telegram handles (e.g., `@mezzodeposite`) in backticks prevents Telegram clients from auto-linking the `@username` mention into a clickable profile/chat link.
**Action:** When formatting contact/support screens in Telegram, wrap phone numbers and account codes in monospace backticks for seamless tap-to-copy, but leave `@username` handles unadorned so they remain active, clickable links.
