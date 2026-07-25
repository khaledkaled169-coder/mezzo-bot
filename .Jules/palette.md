# Palette Journal

## 2026-07-16 - Support Menu Micro-UX Improvements
**Learning:** Monospace formatting in Telegram is essential for allowing users to tap-to-copy critical contact details, such as phone numbers, while maintaining standard unformatted handles (e.g., `@mezzodeposite`) ensures they remain active, clickable links in standard Telegram clients. Combining bold headers with proper Markdown parsers provides clear hierarchy for the UI.
**Action:** Always format phone numbers and accounts in monospace (using backticks) to enable tap-to-copy, keep Telegram handles unformatted to preserve clickable links, and ensure `parse_mode="Markdown"` is present.
