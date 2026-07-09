## 2026-06-16 - Tap-to-copy Monospace Formatting
**Learning:** In Telegram bots, wrapping critical data like account numbers or transaction IDs in monospace backticks (`) enables "tap-to-copy" functionality on mobile clients, significantly reducing friction for users during payment flows.
**Action:** Always identify unique identifiers, financial amounts, and phone numbers in Telegram bot UIs and wrap them in monospace blocks, ensuring any internal backticks are sanitized first.

## 2026-06-16 - Markdown V1 Escaping for User-Generated Content
**Learning:** When using Markdown V1 in Telegram bots, unescaped special characters (like underscores in usernames) in dynamic strings can break message parsing and prevent message delivery.
**Action:** Implement a robust escaping helper (e.g., `esc()`) for all dynamic user-controlled strings (names, usernames) and a separate sanitizer (e.g., `clean_mono()`) for text placed inside monospace blocks where backslashes render literally.
